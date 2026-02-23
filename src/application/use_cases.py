import random
from datetime import datetime, timedelta, timezone

from src.application.dto import UserCreateDTO, UserDTO
from src.application.interfaces import AbstractSMSService, AbstractUnitOfWork
from src.domain.entities import PhoneVerification, UserDomain
from src.infrastructure.auth.jwt_handler import create_token
from src.presentation.api.schemas import TokenPair

# class RegisterUserUseCase:
#     def __init__(self, uow: AbstractUnitOfWork):
#         self.uow = uow

#     async def execute(self, user_data: UserCreateDTO) -> UserDTO:
#         async with self.uow:
#             existing_user = await self.uow.users.find_one(
#                 phone_number=user_data.phone_number
#             )
#             if existing_user:
#                 raise ValueError("Пользователь с таким номером уже существует")

#             new_user = UserDomain(
#                 name=user_data.name,
#                 phone_number=user_data.phone_number,
#             )

#             created_user = await self.uow.users.add_one(new_user)
#             await self.uow.commit()

#             return UserDTO.model_validate(created_user)


class SendVerificationCodeUseCase:
    def __init__(self, uow: AbstractUnitOfWork, sms_service: AbstractSMSService):
        self.uow = uow
        self.sms_service = sms_service

    async def execute(self, phone_number: str):
        code = str(random.randint(1000, 9999))
        verification = PhoneVerification(phone_number=phone_number, code=code)
        async with self.uow:
            await self.uow.verifications.add_one(verification)
            await self.sms_service.send_sms(phone=phone_number, code=code)
            await self.uow.commit()


class VerifyPhoneUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def execute(self, phone_number: str, code: str):
        async with self.uow:
            active_code = await self.uow.verifications.find_one(
                phone_number=phone_number,
                is_used=False,
            )
            if not active_code:
                raise ValueError("Акттивный код подтверждения не найден")

            active_code.verify(input_code=code, current_time=datetime.now())
            await self.uow.verifications.update(active_code)

            user = await self.uow.users.find_one(phone_number=phone_number)
            if user:
                user.is_phone_verified = True
                await self.uow.users.update(user)

            await self.uow.commit()
            return user.id


class AuthenticateUserUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def execute(self, phone_number: str, code: str) -> TokenPair:
        async with self.uow:
            active_code = await self.uow.verifications.find_one(
                phone_number=phone_number, is_used=False
            )
            if not active_code:
                raise ValueError("Код не найден")

            active_code.verify(input_code=code, current_time=datetime.now())
            await self.uow.verifications.update(active_code)

            user = await self.uow.users.find_one(phone_number=phone_number)

            if not user:
                new_user = UserDomain(
                    name="Гость",
                    phone_number=phone_number,
                    is_phone_verified=True,
                )
                user = await self.uow.users.add_one(new_user)

            access_token = create_token(
                {"sub": str(user.id), "typ": "access", "is_phone_verified": True},
                expires_delta=timedelta(minutes=15),
            )
            refresh_token = create_token(
                {"sub": str(user.id), "typ": "refresh", "is_phone_verified": True},
                expires_delta=timedelta(days=7),
            )

            user.is_phone_verified = True
            user.refresh_token = refresh_token
            user.token_expires_at = datetime.now(timezone.utc) + timedelta(days=7)

            await self.uow.users.update(user)
            await self.uow.commit()

            return TokenPair(access_token=access_token, refresh_token=refresh_token)
