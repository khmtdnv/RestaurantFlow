from abc import ABC, abstractmethod
from typing import Type

from db.database import async_session_factory
from repositories.categories import CategoriesRepository
from repositories.combo import ComboRepository
from repositories.dishes import DishesRepository
from repositories.tag import TagRepository
from sqlalchemy.ext.asyncio import AsyncSession


class IUnitOfWork(ABC):
    session: AsyncSession
    dishes: DishesRepository
    categories: CategoriesRepository
    tag: TagRepository
    combo: ComboRepository

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, *args):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def flush(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass


class UnitOfWork:
    def __init__(self):
        self.async_session_factory = async_session_factory

    async def __aenter__(self):
        self.session = self.async_session_factory()
        self.categories = CategoriesRepository(self.session)
        self.dishes = DishesRepository(self.session)
        self.tag = TagRepository(self.session)
        self.combo = ComboRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def flush(self):
        await self.session.flush()

    async def rollback(self):
        await self.session.rollback()
