from fastapi import APIRouter, Depends, HTTPException

from src.schemas import UserCreate, UserRead
from src.uow import UnitOfWork, get_uow

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead)
async def register_user(user: UserCreate, uow: UnitOfWork = Depends(get_uow)):
    async with uow:
        existing_user = await uow.users.get_by_phone(phone=user.phone_number)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким номером телефона уже существует",
            )

        user_dict = user.model_dump()
        user = await uow.users.add_one(user_dict)
        await uow.commit()

        return user
