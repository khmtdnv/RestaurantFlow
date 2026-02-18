from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User


class SQLAlchemyRepository:
    model: Any = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> Any:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj


class UserRepository(SQLAlchemyRepository):
    model = User

    async def get_by_phone(self, phone: str) -> Optional[User]:
        stmt = select(self.model).filter_by(phone_number=phone)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
