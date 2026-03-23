from domain.aggregates.order import Order, OrderItem
from infrastructure.database.models.order import OrderItemModel, OrderModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, order: Order) -> Order: ...

    async def get_by_id(self, order_id: int) -> Order | None: ...

    async def update(self, order: Order) -> None: ...
