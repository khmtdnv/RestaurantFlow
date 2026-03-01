from abc import ABC, abstractmethod
from typing import Type

from db.db import async_session_factory
from repositories.categories import CategoriesRepository
from repositories.dishes import DishesRepository


class IUnitOfWork(ABC):
    dishes: Type[DishesRepository]
    categories: Type[CategoriesRepository]

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

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
