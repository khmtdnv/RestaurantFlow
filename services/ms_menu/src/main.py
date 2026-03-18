import logging
import time
from contextlib import asynccontextmanager

from api.routers import all_routers
from config import settings
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils.rabbitmq import get_rabbitmq_publisher

logging.basicConfig(level=logging.INFO, format="%(levelname)s: --- %(message)s")


rabbitmq_publisher = get_rabbitmq_publisher()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq_publisher.connect_and_init(
        amqp_url=settings.RABBITMQ_URL,
        exchange_name="ms_menu_exchange",
    )
    logging.info("КРОЛИК ЗАПУЩЕН")
    yield
    await rabbitmq_publisher.close()


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


@app.middleware("http")
async def calculate_request_time(request: Request, call_next):
    logging.info(f"Запрос пришел на {request.url.path}")
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logging.info(f"Запрос обработан за {process_time} секунд")

    response.headers["X-Process-Time"] = str(process_time)

    return response


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


# if __name__ == "__main__":
#     uvicorn.run(app="main:app", reload=True)
