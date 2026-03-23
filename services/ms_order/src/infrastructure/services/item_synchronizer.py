from infrastructure.database.models.menu_item import MenuItemOrm
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession


class ItemSynchronizer:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def sync_batch(self, items_data: list[dict]) -> None:
        if not items_data:
            return

        stmt = pg_insert(MenuItemOrm).values(items_data)
        update_stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name": stmt.excluded.name,
                "price": stmt.excluded.price,
                "is_available": stmt.excluded.is_available,
            },
        )
        await self.session.execute(update_stmt)
