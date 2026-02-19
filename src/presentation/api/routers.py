from fastapi import APIRouter, Depends, HTTPException

from src.application.interfaces import AbstractUnitOfWork
from src.application.use_cases import RegisterUserUseCase
from src.infrastructure.uow import SQLAlchemyUnitOfWork
from src.presentation.api.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


async def get_uow() -> AbstractUnitOfWork:
    return SQLAlchemyUnitOfWork()


async def get_register_user_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(uow)


@router.post("/", response_model=UserRead)
async def register_user(
    user: UserCreate,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
):
    try:
        created_user = await use_case.execute(name=user.name, phone=user.phone_number)
        return created_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
