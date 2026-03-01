from abc import ABC, abstractmethod

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def create_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def read_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def read_all(self):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, data: dict):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    """
    Жизненный цикл любого запроса в БД с помощью SQLAlchemy
    1) Statement
        CREATE = insert(self.model).values(...)
        READ = select(self.model).where(...)
        UPDATE = update(self.model).values(...)
        DELETE = delete(self.model).where(...)
    2) Execution
        session.execute(statement)
    3) Processing
    """

    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_one(self, data: dict):
        statement = insert(self.model).values(**data).returning(self.model)  # type: ignore
        result = await self.session.execute(statement)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def read_one(self, **filters):
        statement = select(self.model).filter_by(**filters)  # type: ignore
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def read_all(self):
        statement = select(self.model)  # type: ignore
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update_one(self, data: dict, **filters):
        statement = update(self.model).values(**data).filter_by(**filters).returning(self.model)  # type: ignore
        result = await self.session.execute(statement)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def delete_one(self, **filters):
        statement = delete(self.model).filter_by(**filters)  # type: ignore
        await self.session.execute(statement)
