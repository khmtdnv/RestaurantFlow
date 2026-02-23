from abc import ABC, abstractmethod

from db.db import async_session_factory
from sqlalchemy import insert, select


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one():
        raise NotImplementedError

    @abstractmethod
    async def find_all():
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict):
        async with async_session_factory() as session:
            statement = insert(self.model).values(**data).returning(self.model.id)  # type: ignore
            result = await session.execute(statement)
            await session.commit()
            return result.scalar_one_or_none

    async def find_all(self):
        async with async_session_factory() as session:
            statement = select(self.model)  # type: ignore
            result = await session.execute(statement)
            result = [row[0].to_read_model() for row in result.all()]
            return result
