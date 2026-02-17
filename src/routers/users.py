from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import src.crud as crud
from src.database import get_async_session
from src.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead)
async def register_user(
    user: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    db_user = await crud.get_user_by_phone_number(
        session,
        phone_number=user.phone_number,
    )
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с данным номером телефона уже существует",
        )

    return await crud.create_user(session=session, user_in=user)
