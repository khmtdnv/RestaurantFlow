from api.dependencies import UOWDependency
from fastapi import APIRouter
from schemas.dishes import DishCreateIn, DishOut, DishUpdateIn, HTTPResponse
from services.dishes import DishService

router = APIRouter(prefix="/dishes", tags=["Dishes"])


@router.get("", response_model=list[DishOut])
async def get_dishes(
    uow: UOWDependency,
):
    service = DishService(uow)
    dishes = await service.get_dishes()
    return dishes


@router.get("/{id}", response_model=DishOut)
async def get_dish(
    id: int,
    uow: UOWDependency,
):
    service = DishService(uow)
    dishes = await service.get_dish(id)
    return dishes


@router.post("", response_model=HTTPResponse)
async def add_dish(
    uow: UOWDependency,
    request_data: DishCreateIn,
):
    service = DishService(uow)
    dish = await service.add_dish(
        name=request_data.name,
        price=request_data.price,
        description=request_data.description,
        category_id=request_data.category_id,
        is_available=request_data.is_available,
    )
    return HTTPResponse(
        status="success",
        message=f"Создано новое блюдо '{dish.name}'",
    )


@router.patch("/{id}", response_model=HTTPResponse)
async def update_dish(
    id: int,
    uow: UOWDependency,
    request_data: DishUpdateIn,
):
    service = DishService(uow)
    update_data = request_data.model_dump(exclude_none=True)
    dish = await service.update_dish(id=id, update_data=update_data)
    return HTTPResponse(
        status="success",
        message=f"Обновлено блюдо '{dish.name}'",
    )


@router.delete("/{id}", response_model=HTTPResponse)
async def delete_dish(
    id: int,
    uow: UOWDependency,
):
    service = DishService(uow)
    dish = await service.delete_dish(id=id)
    return HTTPResponse(
        status="success",
        message=f"Удалено блюдо '{dish.name}'",
    )
