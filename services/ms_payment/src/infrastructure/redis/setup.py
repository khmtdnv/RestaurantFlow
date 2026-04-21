from contextlib import asynccontextmanager

from core.config import settings
from fastapi import FastAPI
from redis.asyncio import ConnectionPool, Redis


@asynccontextmanager
async def setup_redis(app: FastAPI):
    pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
    app.state.redis_client = Redis(connection_pool=pool)

    try:
        yield
    finally:
        await app.state.redis_client.close()
        await pool.disconnect()
