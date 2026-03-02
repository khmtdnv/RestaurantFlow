from models.categories import Categories
from utils.unitofwork import IUnitOfWork


class CategoriesService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_categories(self):
        async with self.uow:
            categories = await self.uow.categories.get_all()
            return categories

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
