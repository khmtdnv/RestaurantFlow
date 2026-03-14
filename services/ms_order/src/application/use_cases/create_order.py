from application.dto.orders import OrderCreateIn, OrderOut
from domain.aggregates.order import Order
from domain.interfaces.uow import IUnitOfWork


class CreateOrderUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, dto: OrderCreateIn) -> OrderOut:
        order_entity = Order(
            dishes=dto.dishes,
            price=dto.price,
        )

        async with self.uow:
            saved_entity = await self.uow.orders.add(order_entity)
            await self.uow.commit()

        order_out = OrderOut.model_validate(saved_entity)
        # * Если нужен брокер вызываем его здесь
        # * await self.broker.publish("order.created", order_out.model_dump())

        return order_out
