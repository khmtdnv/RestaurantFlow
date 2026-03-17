from application.dto.order import AddItemRequest
from domain.interfaces.uow import IUnitOfWork


class AddItemToOrderUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, order_id: int, request: AddItemRequest) -> None:
        async with self.uow:
            order = await self.uow.order.get_by_id(order_id)

            if not order:
                raise ValueError(f"Заказ с ID {order_id} не найден")

            order.add_item(
                dish_id=request.dish_id,
                quantity=request.quantity,
                price=request.price,
            )
            await self.uow.commit()
