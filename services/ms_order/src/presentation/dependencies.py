from typing import Annotated

from application.use_cases.cart.add_item import AddItemToCartUseCase
from application.use_cases.menu.sync_menu import SyncMenuUseCase
from domain.interfaces.cart_repository import ICartRepository
from domain.interfaces.menu_repository import IMenuItemRepository
from domain.interfaces.uow import IUnitOfWork
from fastapi import Depends, Header
from infrastructure.database.session import async_session_maker
from infrastructure.dependencies.postgres import get_db_session
from infrastructure.dependencies.redis import get_redis_client
from infrastructure.repositories.cart_repository import RedisCartRepository
from infrastructure.repositories.menu_item_repository import (
    SQLAlchemyMenuItemRepository,
)
from infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


def get_cart_repository(redis: Redis = Depends(get_redis_client)) -> ICartRepository:
    return RedisCartRepository(redis_client=redis)


def get_menu_read_repository(
    session: AsyncSession = Depends(get_db_session),
) -> IMenuItemRepository:
    return SQLAlchemyMenuItemRepository(session=session)


def get_current_user_id(
    user_id: int = Header(..., alias="X-User-Id", description="User ID from API Gateway.")
) -> int:
    """
    Extracts user_id from header.
    Automatically returns 422 if there is no header or user_id not int.
    """
    return user_id


def get_uow() -> IUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory=async_session_maker)


UOWDependency = Annotated[IUnitOfWork, Depends(get_uow)]


def get_sync_menu_use_case() -> SyncMenuUseCase:
    uow = SqlAlchemyUnitOfWork(session_factory=async_session_maker)
    return SyncMenuUseCase(uow)


def get_add_item_to_cart_use_case(
    cart_repo: ICartRepository = Depends(get_cart_repository),
    menu_repo: IMenuItemRepository = Depends(get_menu_read_repository),
) -> AddItemToCartUseCase:
    return AddItemToCartUseCase(cart_repo=cart_repo, menu_repo=menu_repo)
