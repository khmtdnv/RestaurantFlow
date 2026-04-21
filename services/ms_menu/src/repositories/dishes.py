from models import Dish
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload
from utils.repository import SQLAlchemyRepository


class DishesRepository(SQLAlchemyRepository):
    model = Dish

    async def get_dishes(self):
        statement = select(self.model).options(selectinload(self.model.tags))
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_dish_by_id(self, id: int):
        statement = (
            select(self.model).where(self.model.id == id).options(selectinload(self.model.tags))
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def available_wo_categories(self):
        statement = (
            select(self.model)
            .where(
                self.model.is_available.is_(True),
                self.model.category_id.is_(None),
            )
            .options(selectinload(self.model.tags))
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def menu(self):
        stmt = (
            select(self.model)
            .where(self.model.is_available.is_(True))
            .options(
                joinedload(self.model.category),
                selectinload(self.model.tags),
                selectinload(self.model.combos),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def menu_offset(self, offset: int, limit: int):
        stmt = (
            select(self.model)
            .where(self.model.is_available.is_(True))
            .options(
                joinedload(self.model.category),
                selectinload(self.model.tags),
                selectinload(self.model.combos),
            )
        )
        result = await self.session.execute(stmt.offset(offset).limit(limit))
        return result.scalars().all()

    async def menu_offset_count(self):
        stmt = select(func.count(self.model.id)).where(self.model.is_available.is_(True))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def menu_cursor(self, last_id: int, size: int):
        stmt = (
            select(self.model)
            .where(self.model.is_available.is_(True), self.model.id > last_id)
            .options(
                joinedload(self.model.category),
                selectinload(self.model.tags),
                selectinload(self.model.combos),
            )
            .order_by(self.model.id)
        )
        result = await self.session.execute(stmt.limit(size))
        return result.scalars().all()
