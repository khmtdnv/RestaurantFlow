import logging
from contextlib import asynccontextmanager

import aiohttp
from core.logging import configure_logging
from domain.exceptions.base import DomainError
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from infrastructure.database.session import engine
from infrastructure.redis.connection import redis_pool
from infrastructure.slowapi.rate_limit import limiter
from presentation.api.router import api_router
from redis.asyncio import Redis
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

# logging
configure_logging()
log = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
    before_sleep=before_sleep_log(log, logging.WARNING),
)
async def wait_for_postgres():
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    log.info("PostgreSQL готов")


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
    before_sleep=before_sleep_log(log, logging.WARNING),
)
async def wait_for_redis():
    client = Redis(connection_pool=redis_pool)
    await client.execute_command("PING")
    await client.aclose()
    log.info("Redis готов")


# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await wait_for_postgres()
    await wait_for_redis()
    app.state.http_session = aiohttp.ClientSession()
    yield
    await engine.dispose()
    await redis_pool.disconnect()
    await app.state.http_session.close()


# app init
app = FastAPI(title="Ресторан - Микросервис Заказов", lifespan=lifespan)

# подключаем лимитер
app.state.limiter = limiter

# middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "https://твое-приложение.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# global exception handlers


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return _rate_limit_exceeded_handler(request, exc)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    error_msg = str(exc)
    log.warning(f"Domain rule violation: {error_msg} | Path: {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "domain_error", "message": error_msg},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    log.warning(f"Ошибка валидации: {exc.errors()} | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"error": "validation_error", "details": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception(f"Unhandled server error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_error", "message": "Internal server error"},
    )


app.include_router(api_router)
