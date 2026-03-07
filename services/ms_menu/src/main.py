import asyncio
import logging
import time
from contextlib import asynccontextmanager

from aiormq.exceptions import AMQPConnectionError
from api.routers import all_routers
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils.rabbitmq import rabbitmq_client
from utils.redis import redis_client

logging.basicConfig(level=logging.INFO, format="%(levelname)s: --- %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Инициализация приложения: Подключение к RabbitMQ...")

    max_retries = 5
    base_delay = 2.0

    for attempt in range(1, max_retries + 1):
        try:
            await rabbitmq_client.connect()
            logging.info(f"Успешно подключились к RabbitMQ с {attempt} попытки.")
            break

        except AMQPConnectionError as e:
            logging.error(
                f"Ошибка подключения к RabbitMQ (Попытка {attempt}/{max_retries}): {e}"
            )

            if attempt == max_retries:
                logging.error(
                    "Критический сбой: Не удалось подключиться к брокеру. Остановка сервера."
                )
                raise e

            delay = base_delay * (2 ** (attempt - 1))
            logging.info(f"Ожидание {delay} сек. перед следующей попыткой...")
            await asyncio.sleep(delay)

    logging.info("Создание воркера в фоне")
    bg_task = asyncio.create_task(
        rabbitmq_client.consume("menu_cache_invalidation", "ms_menu.#")
    )

    yield

    logging.info("Начат процесс остановки приложения...")

    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        logging.info("Фоновый воркер успешно остановлен.")

    logging.info("Закрытие Redis")
    await redis_client.aclose()
    logging.info("Отключение от RabbitMQ")
    await rabbitmq_client.disconnect()


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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.error(f"Критическая ошибка: {exc}")
    return JSONResponse(status_code=500, content={"message": f"Ошибка {exc}"})


for router in all_routers:
    app.include_router(router)


# if __name__ == "__main__":
#     uvicorn.run(app="main:app", reload=True)
