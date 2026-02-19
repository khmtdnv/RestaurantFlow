from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.domain.entities import UserDomain

TEntity = TypeVar("TEntity")


class AbstractRepository(ABC, Generic[TEntity]):
    @abstractmethod
    async def add_one(self, entity: TEntity) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by) -> TEntity | None:
        raise NotImplementedError


class AbstractUserRepository(AbstractRepository[UserDomain]):
    @abstractmethod
    async def get_by_phone(self, phone: str) -> UserDomain | None:
        raise NotImplementedError


class AbstractUnitOfWork(ABC):
    users: AbstractUserRepository

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
