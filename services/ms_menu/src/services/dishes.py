from decimal import Decimal

from models.dishes import Dishes
from utils.unitofwork import IUnitOfWork


class DishService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_dishes(self):
        async with self.uow:
            dishes = await self.uow.dishes.get_all()
            return dishes

    async def get_dish(self, dish_id: int):
        async with self.uow:
            dish = await self.uow.dishes.get_by_id(dish_id)
            if not dish:
                raise ValueError("Блюдо не найдено")
            return dish

    async def add_dish(
        self,
        name: str,
        price: Decimal,
        description: str | None,
        category_id: int,
        is_available: bool,
    ):
        async with self.uow:
            new_dish = Dishes(
                name=name,
                price=price,
                description=description,
                category_id=category_id,
                is_available=is_available,
            )
            self.uow.dishes.add(new_dish)
            await self.uow.session.flush()
            return new_dish

    async def update_dish(self, id: int, update_data: dict):
        async with self.uow:
            dish = await self.get_dish(id)
            self.uow.dishes.update(dish, **update_data)
            await self.uow.session.flush()
            return dish

    async def delete_dish(self, id: int):
        async with self.uow:
            dish = await self.get_dish(id)
            await self.uow.dishes.delete(dish)
            await self.uow.session.flush()
            return dish
