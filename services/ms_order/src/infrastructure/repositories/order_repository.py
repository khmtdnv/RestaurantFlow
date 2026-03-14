from domain.aggregates.order import Order
from domain.interfaces.repositories import IOrderRepository
from infrastructure.database.models.order import Order as OrderORM
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyOrderRepository(IOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, order: Order) -> Order:
        order_orm = OrderORM(
            dishes=order.dishes,
            price=order.price,
        )

        self.session.add(order_orm)
        await self.session.flush()

        order.id = order_orm.id
        return order
