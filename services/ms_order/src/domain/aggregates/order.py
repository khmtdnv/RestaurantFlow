from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from domain.entities.order_item import OrderItem


class OrderStatus(str, Enum):
    CREATED = "Создан"
    IN_PROGRESS = "Готовится"
    READY = "Готов"
    FINISHED = "Выдан"
    CANCELED = "Отменён"


@dataclass
class Order:
    user_id: int
    id: int | None = None
    status: OrderStatus = OrderStatus.CREATED
    items: list[OrderItem] = field(default_factory=list)
    total_price: Decimal = Decimal("0.00")

    def _recalculate_total(self) -> None:
        # * Внутренний метод: перерасчет итоговой суммы
        total = sum(item.price * item.quantity for item in self.items)
        self.total_price = Decimal(total)

    def add_items(self, items: list[OrderItem]) -> None:
        if not items:
            return

        self.items.extend(items)
        self._recalculate_total()

    def set_id(self, id: int) -> None:
        if not id:
            return

        self.id = id
