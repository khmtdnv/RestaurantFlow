from typing import Annotated

import aiohttp
from application.use_cases.cart.add_item import AddItemToCartUseCase
from application.use_cases.cart.get_cart import GetCartUseCase
from application.use_cases.menu.sync_menu import SyncMenuUseCase
from application.use_cases.order.create_order import CreateOrderUseCase
from domain.interfaces.cart_repository import ICartRepository
from domain.interfaces.menu_repository import IMenuItemRepository
from domain.interfaces.payment_client import IPaymentClient
from domain.interfaces.uow import IUnitOfWork
from fastapi import Depends, Header, HTTPException, Request, status
from infrastructure.dependencies.postgres import get_db_session
from infrastructure.dependencies.redis import get_redis_client
from infrastructure.repositories.cart_repository import RedisCartRepository
from infrastructure.repositories.menu_repository import SQLAlchemyMenuItemRepository
from infrastructure.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from infrastructure.yookassa.client import PaymentClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


async def get_aiohttp_session(request: Request) -> aiohttp.ClientSession:
    return request.app.state.http_session


async def get_payment_client(
    session: aiohttp.ClientSession = Depends(get_aiohttp_session),
) -> IPaymentClient:
    base_url = "http://ms_payment_api:8000/api/v1"
    return PaymentClient(base_url=base_url, session=session)


# user_id extraction
def get_current_user(
    user_id: int = Header(..., alias="X-User-Id"),
) -> int:
    return user_id


def get_current_admin_user(
    user_id: int = Depends(get_current_user),
    is_superuser: bool = Header(..., alias="X-Is-Superuser"),
) -> int:
    if not is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется уровень администратора.",
        )
    return user_id


# uow creation
def get_uow(session: AsyncSession = Depends(get_db_session)) -> IUnitOfWork:
    return SQLAlchemyUnitOfWork(session)


# single repository creation
def get_cart_repository(redis: Redis = Depends(get_redis_client)) -> ICartRepository:
    return RedisCartRepository(redis_client=redis)


def get_menu_read_repository(
    session: AsyncSession = Depends(get_db_session),
) -> IMenuItemRepository:
    return SQLAlchemyMenuItemRepository(session=session)


# use case creation


def add_item_to_cart_use_case(
    cart_repo: ICartRepository = Depends(get_cart_repository),
    menu_repo: IMenuItemRepository = Depends(get_menu_read_repository),
) -> AddItemToCartUseCase:
    return AddItemToCartUseCase(cart_repo=cart_repo, menu_repo=menu_repo)


def get_cart_use_case(
    cart_repo: ICartRepository = Depends(get_cart_repository),
) -> GetCartUseCase:
    return GetCartUseCase(cart_repo)


def create_order_use_case(
    cart_repo: ICartRepository = Depends(get_cart_repository),
    uow: IUnitOfWork = Depends(get_uow),
    payment_client: IPaymentClient = Depends(get_payment_client),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(cart_repo=cart_repo, uow=uow, payment_client=payment_client)
