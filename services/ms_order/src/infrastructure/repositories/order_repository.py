from domain.aggregates.order import Order, OrderItem
from domain.interfaces.repositories import IOrderRepository
from infrastructure.database.models.order import OrderItemModel, OrderModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyOrderRepository(IOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, order: Order) -> Order:
        db_items = [
            OrderItemModel(
                dish_id=item.dish_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in order.items
        ]

        db_order = OrderModel(
            status=order.status,
            price=order.price,
            items=db_items,
        )

        self.session.add(db_order)
        await self.session.flush()

        order.id = db_order.id
        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        result = await self.session.execute(stmt)
        db_order = result.unique().scalar_one_or_none()

        if not db_order:
            return None

        domain_items = [
            OrderItem(
                dish_id=item.dish_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in db_order.items
        ]

        return Order(
            id=db_order.id,
            status=db_order.status,
            price=db_order.price,
            items=domain_items,
        )

    async def update(self, order: Order) -> None:
        stmt = select(OrderModel).where(OrderModel.id == order.id)
        result = await self.session.execute(stmt)
        db_order = result.unique().scalar_one()

        db_order.status = order.status
        db_order.price = order.price

        db_order.items = [
            OrderItemModel(
                dish_id=item.dish_id,
                quantity=item.quantity,
                price=item.price,
            )
            for item in order.items
        ]
