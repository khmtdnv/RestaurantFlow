import asyncio
import os

import pytest

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
os.environ["REDIS_HOST"] = "1"
os.environ["REDIS_PORT"] = "1"
os.environ["MINIO_HOST"] = "1"
os.environ["MINIO_PORT"] = "1"
os.environ["MINIO_ROOT_USER"] = "1"
os.environ["MINIO_ROOT_PASSWORD"] = "1"
import redis.asyncio as redis  # noqa
from httpx import ASGITransport, AsyncClient  # noqa
from infrastructure.database.base import Base  # noqa
from infrastructure.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork  # noqa
from main import app  # noqa
from presentation.dependencies import get_redis_client, get_uow  # noqa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa
from testcontainers.postgres import PostgresContainer  # noqa
from testcontainers.redis import RedisContainer  # noqa


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# значения scope
# 1. function (по умолчанию) - фикстура создается заново для каждого теста
# 2. class - фикстура создается один раз для всего тестового класса и разделяется всеми тестами внутри него
# 3. module - фикстура создается один раз для всего файла с тестами
# 4. package создается один раз для всей директории (пакета)
# 5. session - фикстура создается ровно один раз за весь запуск pytest (от момента ввода команды pytest до завершения процесса)
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)
        user = postgres.username
        password = postgres.password
        db = postgres.dbname

        driver_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        yield driver_url


@pytest.fixture(scope="session")
async def db_engine(postgres_container):
    engine = create_async_engine(postgres_container, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    connection = await db_engine.connect()
    transaction = await connection.begin()

    session_factory = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    session = session_factory()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as redis_container:
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(6379)
        yield f"redis://{host}:{port}/0"


@pytest.fixture(scope="session")
async def redis_client(redis_container):
    client = redis.from_url(redis_container, decode_responses=True)
    yield client
    await client.aclose()


@pytest.fixture(scope="function")
async def clean_redis(redis_client):
    await redis_client.flushall()
    return redis_client


@pytest.fixture(scope="function")
async def client(db_session, clean_redis):

    app.dependency_overrides[get_uow] = lambda: SQLAlchemyUnitOfWork(session=db_session)
    app.dependency_overrides[get_redis_client] = lambda: clean_redis
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
