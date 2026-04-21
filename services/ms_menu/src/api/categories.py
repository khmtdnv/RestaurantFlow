from api.dependencies import BrokerDependency, UOWDependency
from fastapi import APIRouter, status
from schemas.categories import CategoryCreateIn, CategoryOut, CategoryUpdateIn
from services.categories import CategoriesService

category_router = APIRouter(prefix="/categories", tags=["Categories"])


@category_router.get("", response_model=list[CategoryOut], status_code=status.HTTP_200_OK)
async def get_categories(
    uow: UOWDependency,
    broker: BrokerDependency,
):
    service = CategoriesService(uow, broker)
    categories = await service.get_categories()
    return categories


@category_router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def add_category(
    uow: UOWDependency,
    broker: BrokerDependency,
    request_data: CategoryCreateIn,
):
    service = CategoriesService(uow, broker)
    new_catgory = await service.add_category(name=request_data.name)
    return new_catgory


@category_router.get("/{id}", response_model=CategoryOut, status_code=status.HTTP_200_OK)
async def get_category(
    id: int,
    uow: UOWDependency,
    broker: BrokerDependency,
):
    service = CategoriesService(uow, broker)
    category = await service.get_category(id)
    return category


@category_router.patch("/{id}", response_model=CategoryOut, status_code=status.HTTP_200_OK)
async def update_category(
    id: int,
    uow: UOWDependency,
    broker: BrokerDependency,
    request_data: CategoryUpdateIn,
):
    service = CategoriesService(uow, broker)
    update_data = request_data.model_dump(exclude_none=True)
    updated_category = await service.update_category(id=id, update_data=update_data)
    return updated_category


@category_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    id: int,
    uow: UOWDependency,
    broker: BrokerDependency,
):
    service = CategoriesService(uow, broker)
    await service.delete_category(id=id)
    return None
