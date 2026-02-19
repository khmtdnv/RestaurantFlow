from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.presentation.api.routers import auth_router, user_router

app = FastAPI(title="RestaurantFlow")

# Подключаем роутеры
app.include_router(user_router)
app.include_router(auth_router)


origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)
