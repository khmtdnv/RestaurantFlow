from models.users import Users
from sqlalchemy import select, update
from utils.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = Users

    async def find_one(self, **filter_by):
        statement = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(statement)
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_phone(self, phone_number: int):
        user = await self.find_one(phone_number=phone_number)
        return user

    async def update(self, id: int, data: dict) -> int | None:
        statement = (
            update(self.model).values(**data).filter_by(id=id).returning(self.model.id)
        )
        res = await self.session.execute(statement)
        await self.session.flush()
        return res.scalar_one_or_none()

    async def get_user_by_refresh_token(self, refresh_token: str):
        user = await self.find_one(refresh_token=refresh_token)
        return user
