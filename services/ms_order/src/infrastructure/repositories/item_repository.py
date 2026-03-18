from domain.aggregates.item import Item
from domain.interfaces.repositories import IItemRepository
from infrastructure.database.models.item import ItemModel
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyItemRepository(IItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, item: Item) -> Item:
        db_item = ItemModel(**item.__dict__)
        self.session.add(db_item)
        await self.session.flush()
        return item

    async def upsert_many(self, items: list[Item]) -> None:
        if not items:
            return

        items_data = [item.__dict__ for item in items]

        stmt = pg_insert(ItemModel).values(items_data)

        update_stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name": stmt.excluded.name,
                "price": stmt.excluded.price,
                "is_available": stmt.excluded.is_available,
            },
        )
        await self.session.execute(update_stmt)
