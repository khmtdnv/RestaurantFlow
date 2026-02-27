from typing import Annotated, AsyncGenerator

from fastapi import Depends
from redis.asyncio import Redis, from_url
from utils.unitofwork import IUnitOfWork, UnitOfWork

# В реальном проекте эти данные должны быть в pydantic-settings (.env)
REDIS_URL = "redis://redis:6379/0"


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Генератор для получения асинхронного клиента Redis.
    """
    # Создаем клиент
    client = from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        # Отдаем клиент в сервис или роутер
        yield client
    finally:
        # Важно: после завершения запроса закрываем соединение
        await client.close()


RedisDependency = Annotated[Redis, Depends(get_redis)]
UOWDependency = Annotated[IUnitOfWork, Depends(UnitOfWork)]
