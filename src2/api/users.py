from api.dependencies import UOWDependency
from fastapi import APIRouter
from schemas.users import UserSchemaAdd
from services.users import UsersService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("")
async def add_user(user: UserSchemaAdd, uow: UOWDependency):
    user_id = await UsersService().add_user(uow, user)
    return {"user_id": user_id}


@router.get("")
async def get_users(uow: UOWDependency):
    users = await UsersService().get_users(uow)
    return users
