import time

import uvicorn
from api.routers import all_routers
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Ресторан")

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
async def global_exception_handler(request: Request, call_next):
    # API gateway отправил запрос в микросервис
    # здесь мы его перехватываем преждем чем он уйдет дальше в ручку
    print(f"Запрос пришел на {request.url.path}")
    start_time = time.time()

    try:
        # здесь мы передаем запрос, который мы поймали выше, дальше в ручку
        response = await call_next(request)

    except Exception as e:
        # здесь мы ловим любую ошибку которая вернется из ручки и выходим из функции заранее
        print(f"Поймали критическую ошибку: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Внутренняя ошибка сервера. Мы уже чиним!",
            },
        )

    process_time = time.time() - start_time
    print(f"Запрос обработан за {process_time} секунд")

    response.headers["X-Process-Time"] = str(process_time)

    # здесь мы возвращаем ответ если не словили ошибку выше
    return response


for router in all_routers:
    app.include_router(router)


# if __name__ == "__main__":
#     uvicorn.run(app="main:app", reload=True)
