from api.dependencies import (
    BrokerDependency,
    RedisDependency,
    S3Dependency,
    UOWDependency,
)
from fastapi import APIRouter, Query, UploadFile, status
from schemas.dishes import DishCreateIn, DishOut, DishOutWithTags, DishUpdateIn
from schemas.menu import CursorResponse, LimitOffsetResponse, MenuOut, PaginatedResponse
from services.dishes import DishService

router = APIRouter(prefix="/dishes", tags=["Dishes"])

bucket_name = "menu-images"


@router.post("/dishes/{id}/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    uow: UOWDependency,
    broker: BrokerDependency,
    id: int,
    file: UploadFile,
    s3: S3Dependency,
):
    service = DishService(uow, broker)
    file_url = await service.upload_image(id, file, s3)
    return file_url


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


@router.post("", response_model=DishOutWithTags, status_code=status.HTTP_201_CREATED)
async def add_dish(
    uow: UOWDependency,
    broker: BrokerDependency,
    request_data: DishCreateIn,
):
    service = DishService(uow, broker)
    dish = await service.add_dish(request_data)
    return dish


@router.patch("/{id}", response_model=DishOutWithTags, status_code=status.HTTP_200_OK)
async def update_dish(
    id: int,
    uow: UOWDependency,
    broker: BrokerDependency,
    request_data: DishUpdateIn,
):
    service = DishService(uow, broker)
    dish = await service.update_dish(id, request_data)
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


menu_router = APIRouter(prefix="/menu", tags=["Menu"])


@menu_router.get("", response_model=MenuOut, status_code=status.HTTP_200_OK)
async def get_menu(
    uow: UOWDependency,
    redis: RedisDependency,
    broker: BrokerDependency,
):
    service = DishService(uow, broker)
    menu = await service.get_menu(redis)
    return menu


@menu_router.get(
    "/offset",
    response_model=LimitOffsetResponse[MenuOut],
    status_code=status.HTTP_200_OK,
)
async def get_menu_offset(
    uow: UOWDependency,
    broker: BrokerDependency,
    offset: int = Query(0, ge=0, le=100, description="Количество записей для пропуска"),
    limit: int = Query(10, ge=1, le=100, description="Количество записей для возврата"),
):
    service = DishService(uow, broker)
    menu = await service.get_menu_offset(offset, limit)
    return menu


@menu_router.get(
    "/page", response_model=PaginatedResponse[MenuOut], status_code=status.HTTP_200_OK
)
async def get_menu_page(
    uow: UOWDependency,
    broker: BrokerDependency,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Записей на странице"),
):
    service = DishService(uow, broker)
    menu = await service.get_menu_page(page, per_page)
    return menu


@menu_router.get(
    "/cursor", response_model=CursorResponse[MenuOut], status_code=status.HTTP_200_OK
)
async def get_menu_cursor(
    uow: UOWDependency,
    broker: BrokerDependency,
    cursor: str | None = Query(None, description="Курсор для следующей страницы"),
    size: int = Query(10, ge=1, le=100, description="Количество записей"),
):
    service = DishService(uow, broker)
    menu = await service.get_menu_cursor(cursor, size)
    return menu
