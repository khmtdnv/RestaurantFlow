from api.dependencies import BrokerDependency, UOWDependency
from api.dto import DishCreateDTO, DishUpdateDTO
from fastapi import APIRouter, status
from schemas.dishes import DishCreateIn, DishOut, DishUpdateIn
from services.dishes import DishService

router = APIRouter(prefix="/dishes", tags=["Dishes"])


@router.get("", response_model=list[DishOut], status_code=status.HTTP_200_OK)
async def get_dishes(
    uow: UOWDependency,
    broker: BrokerDependency,
):
    service = DishService(uow, broker)
    dishes = await service.get_dishes()
    return dishes


@router.get("/{id}", response_model=DishOut, status_code=status.HTTP_200_OK)
async def get_dish(
    id: int,
    uow: UOWDependency,
    broker: BrokerDependency,
):
    service = DishService(uow, broker)
    dish = await service.get_dish(id)
    return dish


@router.post("", response_model=DishOut, status_code=status.HTTP_201_CREATED)
async def add_dish(
    uow: UOWDependency,
    broker: BrokerDependency,
    request_data: DishCreateIn,
):
    service = DishService(uow, broker)
    dish_dto = DishCreateDTO(
        name=request_data.name,
        price=request_data.price,
        description=request_data.description,
        category_id=request_data.category_id,
        is_available=request_data.is_available,
    )
    dish = await service.add_dish(dish_dto)
    return dish


@router.patch("/{id}", response_model=DishOut, status_code=status.HTTP_200_OK)
async def update_dish(
    id: int,
    uow: UOWDependency,
    broker: BrokerDependency,
    request_data: DishUpdateIn,
):
    service = DishService(uow, broker)
    dish_dto = DishUpdateDTO(
        id=id,
        name=request_data.name,
        price=request_data.price,
        description=request_data.description,
        category_id=request_data.category_id,
        is_available=request_data.is_available,
    )
    dish = await service.update_dish(dish_dto)
    return dish


@router.delete("/{id}", response_model=DishOut, status_code=status.HTTP_200_OK)
async def delete_dish(
    id: int,
    uow: UOWDependency,
    broker: BrokerDependency,
):
    service = DishService(uow, broker)
    dish = await service.delete_dish(id)
    return dish
