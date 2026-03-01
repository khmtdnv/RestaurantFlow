import random
from datetime import datetime, timedelta, timezone

import jwt
from config import settings
from fastapi import HTTPException
from redis.asyncio import Redis
from schemas.users import UserSchemaAdd, UserSchemaEdit
from utils.unitofwork import IUnitOfWork


class AuthService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    # Вспомогательные методы
    def create_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    def create_tokens_pair(self, user_id: int):
        access_token = self.create_token(
            {"sub": str(user_id), "typ": "access", "is_phone_verified": True},
            expires_delta=timedelta(minutes=15),
        )
        refresh_token = self.create_token(
            {"sub": str(user_id), "typ": "refresh", "is_phone_verified": True},
            expires_delta=timedelta(days=7),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }

    async def update_user(self, user_id: int, tokens_pair: dict):
        token_expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        updated_user = UserSchemaEdit(
            is_phone_verified=True,
            refresh_token=tokens_pair["refresh_token"],
            token_expires_at=token_expires_at,
        )
        updated_user_dict = updated_user.model_dump()
        await self.uow.users.update_one(data=updated_user_dict, id=user_id)  # type: ignore

    # Основные методы
    async def send_sms_code(self, redis: Redis, phone_number: str):
        code = str(random.randint(0, 9999)).zfill(4)
        key = f"sms_code:{phone_number}"
        ttl = 300
        await redis.set(key, code, ex=ttl)

        print("========== [SMS SERVICE MOCK] ==========")
        print(f"Отправляем код: {code}")
        print(f"На номер: {phone_number}")
        print("========================================")

    async def resend_sms_code(self, redis: Redis, phone_number: str):
        key = f"sms_cooldown:{phone_number}"
        is_on_cooldown = await redis.get(key)

        if is_on_cooldown:
            cooldown = await redis.ttl(key)
            raise HTTPException(
                status_code=400,
                detail=f"Слишком часто! Подождите {cooldown} секунд перед повторной отправкой",
            )

        await self.send_sms_code(redis=redis, phone_number=phone_number)
        await redis.set(key, 1, ex=60)

    async def verify_phone_by_code(self, redis: Redis, phone_number: str, code: str):
        key = f"sms_code:{phone_number}"
        saved_code = await redis.get(key)
        if not saved_code:
            raise HTTPException(
                status_code=400,
                detail="Код истек или не был запрошен изначально",
            )

        # saved_code.decode()
        if str(saved_code) != code:
            raise HTTPException(
                status_code=400,
                detail=f"Неверный код {saved_code} != {code}",
            )

        await redis.delete(key)

        async with self.uow:
            user = await self.uow.users.get_user_by_phone(phone_number=phone_number)  # type: ignore
            if not user:
                new_user = UserSchemaAdd(name="Guest", phone_number=phone_number)
                new_user_dict = new_user.model_dump()
                user = await self.uow.users.create_one(new_user_dict)  # type: ignore

            tokens_pair = self.create_tokens_pair(user_id=user.id)

            await self.update_user(user_id=user.id, tokens_pair=tokens_pair)
            await self.uow.commit()

            return tokens_pair

    async def refresh_token_pair(self, refresh_token: str):
        async with self.uow:
            user = await self.uow.users.get_user_by_refresh_token(
                refresh_token=refresh_token
            )  # type: ignore
            if not user or user.token_expires_at < datetime.now(timezone.utc):
                return HTTPException(status_code=400, detail="Токен не валиден")

            tokens_pair = self.create_tokens_pair(user_id=user.id)
            await self.update_user(user_id=user.id, tokens_pair=tokens_pair)

            return tokens_pair

    async def logout(self, redis: Redis, refresh_token: str):
        async with self.uow:
            user = await self.uow.users.get_user_by_refresh_token(
                refresh_token=refresh_token
            )  # type: ignore
            if not user or user.token_expires_at < datetime.now(timezone.utc):
                return HTTPException(status_code=400, detail="Токен не валиден")

            key = f"blacklisted:{refresh_token}"
            value = refresh_token
            ttl = datetime.now(timezone.utc) - user.token_expires_at
            await redis.set(key, value, ex=ttl)
