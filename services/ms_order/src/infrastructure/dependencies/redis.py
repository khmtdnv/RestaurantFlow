from typing import AsyncGenerator

from infrastructure.redis.connection import redis_pool
from redis.asyncio import Redis


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    async with Redis(connection_pool=redis_pool) as client:
        yield client
