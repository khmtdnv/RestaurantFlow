from typing import AsyncGenerator

from infrastructure.database.session import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    # 'async with' searches for '__aenter__' and '__aexit__'
    async with async_session_maker() as session:
        # 'yield' freezes state of function making it generator and available to transport
        yield session
