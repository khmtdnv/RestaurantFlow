from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, obj):
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, obj_id):
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, **filters):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, obj):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, obj):
        self.session.add(obj)

    async def get_by_id(self, obj_id: int):
        return await self.session.get(self.model, obj_id)

    async def get_one(self, **filters):
        statement = select(self.model).filter_by(**filters)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(self):
        statement = select(self.model)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def delete(self, obj):
        await self.session.delete(obj)
