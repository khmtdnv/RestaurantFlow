from models.categories import Categories
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from utils.repository import SQLAlchemyRepository


class CategoriesRepository(SQLAlchemyRepository):
    model = Categories

    # async def get_with_dishes(self, **filters):
    #     statement = (
    #         select(self.model)
    #         .filter_by(**filters)
    #         .options(selectinload(self.model.dishes))
    #     )
    #     result = await self.session.execute(statement)
    #     return result.scalar_one_or_none()
