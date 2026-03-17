import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from presentation.api.routers import all_routers

logging.basicConfig(level=logging.INFO, format="%(levelname)s: --- %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Ресторан", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "https://твое-приложение.com",
    ],
    allow_credentials=True,  # Разрешаем передавать куки и токены авторизации
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Разрешаем любые заголовки (включая наш Authorization)
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logging.warning(f"Ресурс не найден: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.error(f"Критическая системная ошибка: \n{str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера"},
    )


for router in all_routers:
    app.include_router(router)
