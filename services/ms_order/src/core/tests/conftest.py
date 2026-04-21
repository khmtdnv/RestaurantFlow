import asyncio
import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ["DB_HOST"] = "1"
os.environ["DB_PORT"] = "1"
os.environ["DB_USER"] = "1"
os.environ["DB_PASS"] = "1"
os.environ["DB_NAME"] = "1"
os.environ["SECRET_KEY"] = "1"
os.environ["RABBITMQ_HOST"] = "1"
os.environ["RABBITMQ_PORT"] = "1"
os.environ["RABBITMQ_USER"] = "1"
os.environ["RABBITMQ_PASS"] = "1"
os.environ["REDIS_HOST"] = "loca1lhost"
os.environ["REDIS_PORT"] = "1"
os.environ["MINIO_HOST"] = "1"
os.environ["MINIO_PORT"] = "1"
os.environ["MINIO_ROOT_USER"] = "1"
os.environ["MINIO_ROOT_PASSWORD"] = "1"

from main import app  # noqa


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Создает асинхронный клиент для запросов."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides = {}
