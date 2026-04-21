from api.dependencies import UOWDependency
from fastapi import APIRouter
from schemas.users import EditUserRequestDTO, EditUserResponseDTO
from services.users import UsersService

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/update-profile", response_model=EditUserResponseDTO)
async def edit_user_profile(
    request_data: EditUserRequestDTO,
    uow: UOWDependency,
):
    service = UsersService(uow)
    await service.edit_user_profile(
        user_id=request_data.id,
        name=request_data.name,
        phone_number=request_data.phone_number,
    )
    return EditUserResponseDTO(status="success", message="Ваши данные изменились")
