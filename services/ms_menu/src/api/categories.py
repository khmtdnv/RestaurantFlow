from api.dependencies import RedisDependency, UOWDependency
from fastapi import APIRouter, status
from schemas.categories import (
    CategoryCreateIn,
    CategoryOut,
    CategoryUpdateIn,
    MenuOut,
)
from services.categories import CategoriesService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryOut], status_code=status.HTTP_200_OK)
async def get_categories(
    uow: UOWDependency,
):
    service = CategoriesService(uow)
    categories = await service.get_categories()
    return categories


@router.get("/menu", response_model=MenuOut, status_code=status.HTTP_200_OK)
async def get_menu(
    uow: UOWDependency,
    redis: RedisDependency,
):
    service = CategoriesService(uow)
    menu = await service.get_menu(redis)
    return menu


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def add_category(
    uow: UOWDependency,
    request_data: CategoryCreateIn,
):
    service = CategoriesService(uow)
    new_catgory = await service.add_category(name=request_data.name)
    return new_catgory


@router.get("/{id}", response_model=CategoryOut, status_code=status.HTTP_200_OK)
async def get_category(
    id: int,
    uow: UOWDependency,
):
    service = CategoriesService(uow)
    category = await service.get_category(id)
    return category


@router.patch("/{id}", response_model=CategoryOut, status_code=status.HTTP_200_OK)
async def update_category(
    id: int,
    uow: UOWDependency,
    request_data: CategoryUpdateIn,
):
    service = CategoriesService(uow)
    update_data = request_data.model_dump(exclude_none=True)
    updated_category = await service.update_category(id=id, update_data=update_data)
    return updated_category


@router.delete("/{id}", response_model=CategoryOut, status_code=status.HTTP_200_OK)
async def delete_category(
    id: int,
    uow: UOWDependency,
):
    service = CategoriesService(uow)
    deleted_category = await service.delete_category(id=id)
    return deleted_category
