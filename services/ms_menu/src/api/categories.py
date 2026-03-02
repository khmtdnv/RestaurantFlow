from api.dependencies import UOWDependency
from fastapi import APIRouter
from schemas.categories import (
    CategoryCreateIn,
    CategoryOut,
    CategoryUpdateIn,
    HTTPResponse,
)
from services.categories import CategoriesService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryOut])
async def get_categories(
    uow: UOWDependency,
):
    service = CategoriesService(uow)
    categories = await service.get_categories()
    return categories


@router.post("", response_model=HTTPResponse)
async def add_category(
    uow: UOWDependency,
    request_data: CategoryCreateIn,
):
    service = CategoriesService(uow)
    category = await service.add_category(name=request_data.name)
    return HTTPResponse(
        status="success",
        message=f"Создана новая категория '{category.name}'",
    )


@router.get("/{id}", response_model=CategoryOut)
async def get_category(
    id: int,
    uow: UOWDependency,
):
    service = CategoriesService(uow)
    category = await service.get_category(id)
    return category


@router.patch("/{id}", response_model=HTTPResponse)
async def update_category(
    id: int,
    uow: UOWDependency,
    request_data: CategoryUpdateIn,
):
    service = CategoriesService(uow)
    update_data = request_data.model_dump(exclude_none=True)
    category = await service.update_category(id=id, update_data=update_data)
    return HTTPResponse(
        status="success",
        message=f"Обновлена категория '{category.name}'",
    )


@router.delete("/{id}", response_model=HTTPResponse)
async def delete_category(
    id: int,
    uow: UOWDependency,
):
    service = CategoriesService(uow)
    category = await service.delete_category(id=id)
    return HTTPResponse(
        status="success",
        message=f"Удалена категория '{category.name}'",
    )
