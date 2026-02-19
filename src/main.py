from fastapi import FastAPI

from src.presentation.api.routers import router as users_router

app = FastAPI(title="RestaurantFlow")

# Подключаем роутеры
app.include_router(users_router)
