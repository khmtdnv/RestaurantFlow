import logging

from domain.aggregates.order import OrderStatus
from domain.interfaces.uow import IUnitOfWork

log = logging.getLogger(__name__)


class UpdateOrderStatusUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, order_id: str, new_status: OrderStatus) -> None:
        async with self.uow:
            order = await self.uow.order_repo.get_by_id(int(order_id))
            if not order:
                log.error(f"Ошибка: Заказ {order_id} не найден")
                return

            order.change_status(new_status)

            await self.uow.order_repo.update_status(order)
            await self.uow.commit()
