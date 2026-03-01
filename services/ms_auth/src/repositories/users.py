from models.users import Users
from sqlalchemy import select, update
from utils.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = Users

    async def get_user_by_phone(self, phone_number: int):
        user = await self.read_one(phone_number=phone_number)
        return user

    async def get_user_by_refresh_token(self, refresh_token: str):
        user = await self.read_one(refresh_token=refresh_token)
        return user
