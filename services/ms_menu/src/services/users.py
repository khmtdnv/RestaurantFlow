from fastapi import HTTPException
from schemas.users import UserProfileUpdate
from utils.unitofwork import IUnitOfWork


class UsersService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def edit_user_profile(
        self,
        user_id: int,
        name: str | None,
        phone_number: str | None,
    ):
        if not name and not phone_number:
            raise HTTPException(status_code=400, detail="Нечего менять")

        async with self.uow:
            updated_user = UserProfileUpdate(name=name, phone_number=phone_number)
            updated_user_dict = updated_user.model_dump(exclude_none=True)
            await self.uow.users.update_one(data=updated_user_dict, id=user_id)  # type: ignore
            await self.uow.commit()
