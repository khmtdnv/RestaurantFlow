from config import settings
from redis.asyncio import ConnectionPool

redis_pool = ConnectionPool.from_url(
    url=settings.REDIS_URL,
    decode_responses=True,
    max_connections=100,
)
