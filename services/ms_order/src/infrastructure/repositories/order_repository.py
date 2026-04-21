from domain.aggregates.order import Order, OrderItem
from domain.interfaces.order_repository import IOrderRepository
from infrastructure.database.models.order import OrderItemModel, OrderModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


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

    async def get_by_id(self, order_id: int) -> Order | None:
        stmt = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == order_id)
        )
        result = await self.session.execute(stmt)
        order_orm = result.scalar_one_or_none()

        if not order_orm:
            return None

        domain_items = [
            OrderItem(
                dish_id=item_orm.dish_id,
                quantity=item_orm.quantity,
                price=item_orm.price,
            )
            for item_orm in order_orm.items
        ]

        order = Order(
            user_id=order_orm.user_id,
            status=order_orm.status,
            total_price=order_orm.total_price,
        )
        order.set_id(order_orm.id)
        order.add_items(domain_items)

        return order

    async def update_status(self, order: Order) -> None:

        stmt = select(OrderModel).where(OrderModel.id == order.id)
        result = await self.session.execute(stmt)
        order_orm = result.scalar_one_or_none()

        if order_orm:
            order_orm.status = order.status
