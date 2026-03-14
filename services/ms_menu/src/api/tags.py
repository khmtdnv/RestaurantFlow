from api.dependencies import UOWDependency
from fastapi import APIRouter, status
from schemas.tag import TagCreateIn, TagOut, TagUpdateIn
from services.tag import TagService

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/{id}", response_model=TagOut, status_code=status.HTTP_200_OK)
async def get_tag(
    uow: UOWDependency,
    id: int,
):
    service = TagService(uow)
    tag = await service.get_tag(id)
    return tag


@router.get("", response_model=list[TagOut], status_code=status.HTTP_200_OK)
async def get_tags(
    uow: UOWDependency,
):
    service = TagService(uow)
    # await service.fake()
    tags = await service.get_tags()
    return tags


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def add_tag(
    uow: UOWDependency,
    request_data: TagCreateIn,
):
    service = TagService(uow)
    tag = await service.add_tag(request_data)
    return tag


@router.patch("/{id}", response_model=TagOut, status_code=status.HTTP_200_OK)
async def update_tag(
    uow: UOWDependency,
    id: int,
    request_data: TagUpdateIn,
):
    service = TagService(uow)
    tag = await service.update_tag(id, request_data)
    return tag


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    uow: UOWDependency,
    id: int,
):
    service = TagService(uow)
    await service.delete_tag(id)
    return None
