from domain.entities.menu_item import MenuItem
from domain.interfaces.menu_repository import IMenuItemRepository
from infrastructure.database.models.menu_item import MenuItemOrm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyMenuItemRepository(IMenuItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, item_id: int) -> MenuItem | None:
        stmt = select(MenuItemOrm).where(MenuItemOrm.id == item_id)
        result = await self.session.execute(stmt)

        db_model = result.scalar_one_or_none()

        if not db_model:
            return None

        domain_model = MenuItem(
            id=db_model.id,
            price=db_model.price,
            is_available=db_model.is_available,
        )

        return domain_model
