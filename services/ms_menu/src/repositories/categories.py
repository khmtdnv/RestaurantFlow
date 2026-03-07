from models.categories import Categories
from models.dishes import Dishes
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from utils.repository import SQLAlchemyRepository


class CategoriesRepository(SQLAlchemyRepository):
    model = Categories

    async def get_categories_with_active_dishes(self):
        statement = select(self.model).options(
            selectinload(self.model.dishes.and_(Dishes.is_available == True))  # noqa
        )
        result = await self.session.execute(statement)
        return result.scalars().all()
