from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.schemas import UserCreate


async def get_user_by_phone_number(session: AsyncSession, phone_number: str):
    query = select(User).where(User.phone_number == phone_number)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_in: UserCreate):
    new_user = User(name=user_in.name, phone_number=user_in.phone_number)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
