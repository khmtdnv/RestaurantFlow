from typing import AsyncGenerator

from infrastructure.database.session import async_session_maker
from infrastructure.redis.connection import redis_pool
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    async with Redis(connection_pool=redis_pool) as client:
        yield client
