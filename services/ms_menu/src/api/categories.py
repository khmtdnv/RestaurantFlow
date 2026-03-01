from api.dependencies import UOWDependency
from fastapi import APIRouter
from schemas.categories import CategoryOut
from services.categories import CategoriesService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryOut])
async def get_categories(
    uow: UOWDependency,
):
    service = CategoriesService(uow)
    categories = await service.get_categories()
    return categories
