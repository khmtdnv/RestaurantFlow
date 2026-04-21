import functools


def connection_cache(ttl: int = 3600, key: str = "None"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis_client = args[0].redis
            if key != "None":
                cache = redis_client.get(key)
                return cache
            await func(*args, **kwargs)

        return wrapper

    return decorator
