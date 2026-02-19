from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.domain.entities import PhoneVerification, UserDomain

TEntity = TypeVar("TEntity")


class AbstractRepository(ABC, Generic[TEntity]):
    @abstractmethod
    async def add_one(self, entity: TEntity) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: TEntity) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by) -> TEntity | None:
        raise NotImplementedError


class AbstractUserRepository(AbstractRepository[UserDomain]):
    @abstractmethod
    async def get_by_phone(self, phone: str) -> UserDomain | None:
        raise NotImplementedError


class AbstractPhoneVerificationRepository(AbstractRepository[PhoneVerification]):
    pass


class AbstractUnitOfWork(ABC):
    users: AbstractUserRepository
    verifications: AbstractPhoneVerificationRepository

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


class AbstractAuthService(ABC):
    @abstractmethod
    async def create_access_token(self, data: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    async def decode_token(self, token: str) -> dict:
        raise NotImplementedError


class AbstractSMSService(ABC):
    @abstractmethod
    async def send_sms(self, phone: str, code: str):
        raise NotImplementedError
