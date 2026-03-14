import logging

from models import Category
from utils.rabbitmq import RabbitMQClient
from utils.unitofwork import IUnitOfWork

logger = logging.getLogger(__name__)


class CategoriesService:
    def __init__(self, uow: IUnitOfWork, broker: RabbitMQClient):
        self.uow = uow
        self.broker = broker

    async def get_categories(self):
        async with self.uow:
            categories_orm = await self.uow.categories.get_all()
            return categories_orm

    async def add_category(self, name: str):
        async with self.uow:
            category_orm = Category(name=name)
            self.uow.categories.add(category_orm)
            await self.uow.session.flush()
            return category_orm

    async def get_category(self, dish_id: int):
        async with self.uow:
            category_orm = await self.uow.categories.get_by_id(dish_id)
            if not category_orm:
                raise ValueError("Категория не найдена")
            return category_orm

    async def update_category(self, id: int, update_data: dict):
        async with self.uow:
            category_orm = await self.uow.categories.get_by_id(id)

            if not category_orm:
                raise ValueError("Категория не найдена")

            self.uow.categories.update(category_orm, **update_data)
            await self.uow.session.flush()
            return category_orm

    async def delete_category(self, id: int):
        async with self.uow:
            category_orm = await self.uow.categories.get_by_id(id)

            if not category_orm:
                raise ValueError("Категория не найдена")

            await self.uow.categories.delete(category_orm)
            await self.uow.session.flush()

            return category_orm
