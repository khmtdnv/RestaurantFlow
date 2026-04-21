from api.dependencies import UOWDependency
from fastapi import APIRouter, status
from schemas.combo import ComboCreateIn, ComboOut, ComboUpdateIn
from services.combo import ComboService

router = APIRouter(prefix="/combos", tags=["Combos"])


@router.get("/{id}", response_model=ComboOut, status_code=status.HTTP_200_OK)
async def get_combo(
    uow: UOWDependency,
    id: int,
):
    service = ComboService(uow)
    combo = await service.get_combo(id)
    return combo


@router.get("", response_model=list[ComboOut], status_code=status.HTTP_200_OK)
async def get_combos(
    uow: UOWDependency,
):
    service = ComboService(uow)
    combos = await service.get_combos()
    return combos


@router.post("", response_model=ComboOut, status_code=status.HTTP_201_CREATED)
async def add_combo(
    uow: UOWDependency,
    request_data: ComboCreateIn,
):
    service = ComboService(uow)
    combo = await service.add_combo(request_data)
    return combo


@router.patch("/{id}", response_model=ComboOut, status_code=status.HTTP_200_OK)
async def update_combo(
    uow: UOWDependency,
    id: int,
    request_data: ComboUpdateIn,
):
    service = ComboService(uow)
    combo = await service.update_combo(id, request_data)
    return combo


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_combo(
    uow: UOWDependency,
    id: int,
):
    service = ComboService(uow)
    await service.delete_combo(id)
    return None
