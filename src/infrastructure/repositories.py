from abc import ABC, abstractmethod
from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import UserDomain
from src.infrastructure.database.orm import UserORM
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

    async def get_by_phone(self, phone: str) -> UserDomain | None:
        statement = select(self.model).filter_by(phone_number=phone)
        result = await self.session.execute(statement)
        orm_user = result.scalar_one_or_none()

        if not orm_user:
            return None

        return UserDomain.model_validate(orm_user, from_attributes=True)

    async def add_one(self, user: UserDomain) -> UserDomain:
        user_data = user.model_dump(exclude={"id", "created_at", "updated_at"})
        orm_model = UserORM(**user_data)
        self.session.add(orm_model)
        await self.session.flush()

        user.id = orm_model.id
        return user
