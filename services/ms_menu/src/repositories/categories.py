from models import Category, Dish
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from utils.repository import SQLAlchemyRepository


class CategoriesRepository(SQLAlchemyRepository):
    model = Category

    async def with_available_dishes(self):
        statement = select(self.model).options(
            selectinload(
                self.model.dishes.and_(Dish.is_available.is_(True))
            ).selectinload(Dish.tags)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()
