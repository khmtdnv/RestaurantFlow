from core.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False,
    pool_size=15,  # Базовое количество постоянно открытых коннектов к БД
    max_overflow=15,  # Сколько коннектов можно открыть дополнительно при пиковой нагрузке
    pool_timeout=30,  # Сколько секунд ждать свободный коннект, прежде чем выкинуть TimeoutError
)

async_session_maker = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
