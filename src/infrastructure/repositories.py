from typing import Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces import (
    AbstractPhoneVerificationRepository,
    AbstractRepository,
    AbstractUserRepository,
)
from src.domain.entities import PhoneVerification, UserDomain
from src.infrastructure.database.orm import PhoneVerificationORM, UserORM

TModel = TypeVar("TModel")
TEntity = TypeVar("TEntity", bound=BaseModel)


class SQLAlchemyRepository(AbstractRepository[TEntity], Generic[TModel, TEntity]):
    model: Type[TModel]
    entity: Type[TEntity]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: TEntity) -> TEntity:
        data_dict = data.model_dump(exclude_none=True)
        statement = self.model(**data_dict)

        self.session.add(statement)
        await self.session.flush()

        data.id = statement.id
        return data

    async def update(self, data: TEntity) -> TEntity:
        data_dict = data.model_dump(exclude_none=True)
        statement = self.model(**data_dict)

        await self.session.merge(statement)
        await self.session.flush()

        return data

    async def find_one(self, **filter_by) -> TEntity | None:
        statement = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(statement)
        orm_obj = result.scalar_one_or_none()

        if not orm_obj:
            return None

        return self.entity.model_validate(orm_obj)


class PhoneVerificationRepository(
    SQLAlchemyRepository[PhoneVerificationORM, PhoneVerification],
    AbstractPhoneVerificationRepository,
):
    model = PhoneVerificationORM
    entity = PhoneVerification


class UserRepository(SQLAlchemyRepository[UserORM, UserDomain], AbstractUserRepository):
    model = UserORM
    entity = UserDomain

    async def get_by_phone(self, phone: str) -> UserDomain | None:
        return await self.find_one(phone_number=phone)
