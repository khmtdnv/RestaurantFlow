from abc import ABC, abstractmethod
from typing import Type

from db.db import async_session_factory
from repositories.users import UsersRepository


class IUnitOfWork(ABC):
    users: Type[UsersRepository]

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
        self.session = self.async_session_factory

        self.users = UsersRepository(self.session)  # type: ignore

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()  # type: ignore

    async def commit(self):
        await self.session.commit()  # type: ignore

    async def rollback(self):
        await self.session.rollback()  # type: ignore
