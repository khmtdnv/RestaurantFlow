from abc import ABC, abstractmethod
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User


class Repository[T](ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> T:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by) -> T | None:
        raise NotImplementedError


class SQLAlchemyRepository[T](Repository[T]):
    model: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> T:
        statement = self.model(**data)
        self.session.add(statement)
        await self.session.flush()
        await self.session.refresh(statement)
        return statement

    async def find_one(self, **filter_by) -> T | None:
        statement = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()


class UserRepository(SQLAlchemyRepository[User]):
    model = User

    async def get_by_phone(self, phone: str) -> User | None:
        statement = select(self.model).filter_by(phone_number=phone)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
