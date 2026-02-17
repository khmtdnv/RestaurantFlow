from fastapi import FastAPI

from src.routers import users

app = FastAPI(title="RestaurantFlow")

# Подключаем роутеры
app.include_router(users.router)
