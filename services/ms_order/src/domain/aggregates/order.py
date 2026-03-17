from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    CREATED = "Создан"
    IN_PROGRESS = "Готовится"
    READY = "Готов"
    FINISHED = "Выдан"
    CANCELED = "Отменён"


@dataclass
class OrderItem:
    dish_id: int
    quantity: int
    price: Decimal


@dataclass
class Order:
    id: int | None = None
    status: OrderStatus = OrderStatus.CREATED
    items: list[OrderItem] = field(default_factory=list)
    price: Decimal = Decimal("0.00")

    def _recalculate_total(self) -> None:
        # * Внутренний метод: перерасчет итоговой суммы
        total = sum(item.price * item.quantity for item in self.items)
        self.price = Decimal(total)

    def add_item(self, dish_id: int, quantity: int, price: Decimal) -> None:
        # * Бизнес метод: Добавление позиции в заказ
        if self.status not in [OrderStatus.CREATED, OrderStatus.IN_PROGRESS]:
            raise ValueError(f"Нельзя добавить блюдо! Заказ в статусе:{self.status}")

        if quantity <= 0:
            raise ValueError("Количество блюд должно быть больше нуля!")

        item = OrderItem(dish_id=dish_id, quantity=quantity, price=price)
        self.items.append(item)

        self._recalculate_total()

    def pay(self, amount: Decimal) -> Decimal:
        # * Бизнес метод: Оплата
        if not self.items:
            raise ValueError("Нельзя оплатить пустой заказ!")

        if self.status != OrderStatus.CREATED:
            raise ValueError(f"Оплата не принимается. Заказ в статусе: {self.status}")

        if amount < self.price:
            raise ValueError(f"Нужно доплатить {self.price - amount}")

        self.status = OrderStatus.IN_PROGRESS

        change = amount - self.price
        return change
