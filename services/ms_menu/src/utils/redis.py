from config import settings
from redis.asyncio import Redis, from_url

redis_client = from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> Redis:
    yield redis_client  # type:ignore
