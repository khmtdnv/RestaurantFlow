import logging
from contextlib import asynccontextmanager

from core.logging import configure_logging
from domain.exceptions.base import DomainError
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from presentation.api.router import api_router

# logging
configure_logging()
log = logging.getLogger(__name__)


# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting up application...")
    yield
    log.info("Shutting down application...")


# app init
app = FastAPI(title="Ресторан - Микросервис Заказов", lifespan=lifespan)

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
    log.warning(f"Validation error: {exc.errors()} | Path: {request.url.path}")
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
