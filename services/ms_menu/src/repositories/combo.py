from models import Combo
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from utils.repository import SQLAlchemyRepository


class ComboRepository(SQLAlchemyRepository):
    model = Combo

    async def get_combos(self):
        statement = select(self.model).options(selectinload(self.model.dishes))
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_combo_by_id(self, id: int):
        statement = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(self.model.dishes))
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
