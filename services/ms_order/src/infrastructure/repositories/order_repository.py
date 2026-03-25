from domain.aggregates.order import Order
from domain.interfaces.order_repository import IOrderRepository
from infrastructure.database.models.order import OrderItemModel, OrderModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyOrderRepository(IOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: Order) -> int:
        order_items_orm = [
            OrderItemModel(
                dish_id=item.dish_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in order.items
        ]

        order_orm = OrderModel(
            user_id=order.user_id,
            status=order.status,
            total_price=order.total_price,
            items=order_items_orm,
        )

        self.session.add(order_orm)

        await self.session.flush()

        return order_orm.id
