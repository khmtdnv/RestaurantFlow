from abc import ABC, abstractmethod
from typing import Type

from repositories.categories import CategoriesRepository
from repositories.dishes import DishesRepository

from services.ms_menu.src.db.database import async_session_factory


class IUnitOfWork(ABC):
    dishes: DishesRepository
    categories: CategoriesRepository

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
    async def rollback(self):
        pass


class UnitOfWork:
    def __init__(self):
        self.async_session_factory = async_session_factory

    async def __aenter__(self):
        self.session = self.async_session_factory()
        self.categories = CategoriesRepository(self.session)
        self.dishes = DishesRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
