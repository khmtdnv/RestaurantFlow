from typing import Annotated, AsyncGenerator

import jwt
from config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis, from_url
from utils.unitofwork import IUnitOfWork, UnitOfWork

REDIS_URL = "redis://ms_auth_cache:6379/0"


async def get_redis() -> AsyncGenerator[Redis, None]:
    client = from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


RedisDependency = Annotated[Redis, Depends(get_redis)]
UOWDependency = Annotated[IUnitOfWork, Depends(UnitOfWork)]

security = HTTPBearer()


async def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("typ") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный тип токена. Ожидается access токен.",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истек.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен.")


async def get_current_user(
    uow: UOWDependency,
    payload: dict = Depends(get_token_payload),
):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не содержит sub."
        )

    async with uow:
        user = await uow.users.read_one(id=int(user_id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден.",
            )

        return user


async def get_current_admin_user(
    current_user=Depends(get_current_user),
    payload: dict = Depends(get_token_payload),
):
    if not current_user and not payload.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется уровень администратора.",
        )
    return current_user
