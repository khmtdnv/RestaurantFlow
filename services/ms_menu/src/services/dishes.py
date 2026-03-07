import logging

from api.dto import DishCreateDTO, DishUpdateDTO
from models.dishes import Dishes
from schemas.dishes import DishOut
from utils.rabbitmq import RabbitMQClient
from utils.unitofwork import IUnitOfWork


class DishService:
    def __init__(self, uow: IUnitOfWork, broker: RabbitMQClient):
        self.uow = uow
        self.broker = broker

    async def get_dishes(self):
        async with self.uow:
            dishes = await self.uow.dishes.get_all()
            return dishes

    async def get_dish(self, id: int):
        async with self.uow:
            dish = await self.uow.dishes.get_by_id(id)
            if not dish:
                raise ValueError("Блюдо не найдено")
            return dish

    async def add_dish(self, dto: DishCreateDTO):
        async with self.uow:
            dish_orm = Dishes(
                name=dto.name,
                price=dto.price,
                description=dto.description,
                category_id=dto.category_id,
                is_available=dto.is_available,
            )
            self.uow.dishes.add(dish_orm)
            await self.uow.session.flush()
            # ORM Object -> model_validate -> pydantic scheme
            # pydantic scheme -> model_dump > python dict
            dish_scheme = DishOut.model_validate(dish_orm)
            dish_dict = dish_scheme.model_dump(mode="json")

        await self.broker.publish(
            routing_key="ms_menu.dishes.add_dish",
            payload=dish_dict,
        )
        logging.info("Создано событие: ms_menu.dishes.delete_dish")
        return dish_scheme

    async def update_dish(self, dto: DishUpdateDTO):
        async with self.uow:
            dish_orm = await self.get_dish(dto.id)
            self.uow.dishes.update(dish_orm, **dto)
            await self.uow.session.flush()
            dish_scheme = DishOut.model_validate(dish_orm)
            dish_dict = dish_scheme.model_dump(mode="json")

        await self.broker.publish(
            routing_key="ms_menu.dishes.update_dish",
            payload=dish_dict,
        )
        logging.info("Создано событие: ms_menu.dishes.delete_dish")
        return dish_scheme

    async def delete_dish(self, id: int):
        async with self.uow:
            dish_orm = await self.get_dish(id)
            await self.uow.dishes.delete(dish_orm)
            await self.uow.session.flush()
            dish_scheme = DishOut.model_validate(dish_orm)
            dish_dict = dish_scheme.model_dump(mode="json")

        await self.broker.publish(
            routing_key="ms_menu.dishes.delete_dish",
            payload=dish_dict,
        )
        logging.info("Создано событие: ms_menu.dishes.delete_dish")
        return dish_scheme
