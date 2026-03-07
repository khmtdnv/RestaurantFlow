import logging

from models.categories import Categories
from redis.asyncio import Redis
from schemas.categories import MenuOut
from utils.unitofwork import IUnitOfWork


class CategoriesService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_categories(self):
        async with self.uow:
            categories = await self.uow.categories.get_all()
            return categories

    async def get_menu(self, redis: Redis):
        cache = await redis.get("menu:full")
        if cache:
            logging.info("Меню взято из кэша")
            menu_scheme = MenuOut.model_validate_json(cache)
            return menu_scheme

        async with self.uow:
            categories_with_dishes = (
                await self.uow.categories.get_categories_with_active_dishes()
            )
            dishes_wo_categories = await self.uow.dishes.get_all(
                category_id=None,
                is_available=True,
            )
            menu_scheme = MenuOut(
                categories=categories_with_dishes,  # type:ignore
                uncategorized_dishes=dishes_wo_categories,  # type:ignore
            )
            menu_json_string = menu_scheme.model_dump_json()
            await redis.set("menu:full", value=menu_json_string, ex=3600)
            logging.info("Поместили меню в кэш")
            return menu_scheme

    async def add_category(self, name: str):
        async with self.uow:
            new_category = Categories(name=name)
            self.uow.categories.add(new_category)
            await self.uow.session.flush()
            return new_category

    async def get_category(self, dish_id: int):
        async with self.uow:
            category = await self.uow.categories.get_by_id(dish_id)
            if not category:
                raise ValueError("Категория не найдена")
            return category

    async def update_category(self, id: int, update_data: dict):
        async with self.uow:
            category = await self.get_category(id)
            self.uow.categories.update(category, **update_data)
            await self.uow.session.flush()
            return category

    async def delete_category(self, id: int):
        async with self.uow:
            category = await self.get_category(id)
            await self.uow.categories.delete(category)
            await self.uow.session.flush()
            return category
