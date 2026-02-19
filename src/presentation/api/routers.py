from fastapi import APIRouter, Depends, HTTPException

from src.application.dto import UserCreateDTO, UserDTO
from src.application.interfaces import AbstractUnitOfWork
from src.application.use_cases import RegisterUserUseCase, VerifyPhoneUseCase
from src.infrastructure.uow import SQLAlchemyUnitOfWork
from src.presentation.api.schemas import UserCreate, UserRead, VerifyCodeRequest

user_router = APIRouter(prefix="/users", tags=["Users"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_uow() -> AbstractUnitOfWork:
    return SQLAlchemyUnitOfWork()


async def get_register_user_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(uow)


async def get_verify_phone_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> VerifyPhoneUseCase:
    return VerifyPhoneUseCase(uow)


@user_router.post("/", response_model=UserRead)
async def register_user(
    user: UserCreate,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
):
    try:
        create_dto = UserCreateDTO(name=user.name, phone_number=user.phone_number)
        user_dto = await use_case.execute(create_dto)

        return user_dto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/verify-code")
async def verify_code(
    data: VerifyCodeRequest,
    use_case: VerifyPhoneUseCase = Depends(get_verify_phone_use_case),
):
    try:
        await use_case.execute(phone_number=data.phone_number, code=data.code)
        return {"status": "ok", "message": "Номер подтвержден"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
