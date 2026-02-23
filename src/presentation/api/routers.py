import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.application.dto import UserCreateDTO, UserDTO
from src.application.interfaces import AbstractSMSService, AbstractUnitOfWork
from src.application.use_cases import (
    AuthenticateUserUseCase,
    RegisterUserUseCase,
    SendVerificationCodeUseCase,
)
from src.config import settings
from src.domain.entities import UserDomain
from src.infrastructure.services.sms import (  # Твой сервис отправки СМС (название может чуть отличаться)
    DummySMSService,
)
from src.infrastructure.uow import SQLAlchemyUnitOfWork
from src.presentation.api.schemas import (
    PhoneRequest,
    ResendCodeRequest,
    UserCreate,
    UserRead,
    VerifyCodeRequest,
)

user_router = APIRouter(prefix="/users", tags=["Users"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_uow() -> AbstractUnitOfWork:
    return SQLAlchemyUnitOfWork()


async def get_current_user(token: str, uow: AbstractUnitOfWork = Depends(get_uow)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")  # type: ignore
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    async with uow:
        user = await uow.users.find_one(id=int(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_phone_verified:
            raise HTTPException(status_code=403, detail="Phone not verified")
        return user


async def get_current_admin_user(current_user: UserDomain = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return current_user


async def get_register_user_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(uow)


async def get_authenticate_user_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(uow)


async def get_sms_service() -> AbstractSMSService:
    return DummySMSService()  # Подставляем реализацию сервиса СМС


async def get_send_verification_code_use_case(
    uow: AbstractUnitOfWork = Depends(get_uow),
    sms_service: AbstractSMSService = Depends(get_sms_service),
) -> SendVerificationCodeUseCase:
    return SendVerificationCodeUseCase(uow, sms_service)


@auth_router.post("/resend-code")
async def resend_code(
    data: ResendCodeRequest,
    use_case: SendVerificationCodeUseCase = Depends(
        get_send_verification_code_use_case
    ),
):
    try:
        await use_case.execute(phone_number=data.phone_number)
        return {"status": "ok", "message": "Новый код подтверждения успешно отправлен"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.get("/me")
async def get_me(current_user: UserDomain = Depends(get_current_user)):
    return current_user


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


@auth_router.post("/send-code")
async def send_auth_code(
    data: PhoneRequest,
    use_case: SendVerificationCodeUseCase = Depends(
        get_send_verification_code_use_case
    ),
):
    try:

        await use_case.execute(phone_number=data.phone_number)
        return {"status": "ok", "message": "Код отправлен"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/verify-code")
async def verify_code(
    data: VerifyCodeRequest,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
):
    try:
        tokens = await use_case.execute(phone_number=data.phone_number, code=data.code)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
