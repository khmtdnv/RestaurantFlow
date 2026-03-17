from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class CartItem:
    dish_id: int
    quantity: int
    price: Decimal


# def generate_uuid():
#     return str(uuid.uuid4())


# @dataclass
# class Cart:
#     # Фабрика будет каждый раз вызывать нашу функцию!
#     owner_id: str = field(default_factory=generate_uuid)


@dataclass
class Cart:
    user: str
    items: list[CartItem] = field(default_factory=list)
    total_price: Decimal = Decimal("0.00")

    def _recalculate_total(self) -> None:
        # * Внутренний метод: перерасчет итоговой суммы
        total = sum(item.price * item.quantity for item in self.items)
        self.price = Decimal(total)

    def add_item(self, dish_id: int, quantity: int, price: Decimal) -> None:
        if quantity <= 0:
            raise ValueError("Количество блюда должно быть больше нуля!")

        existing_item = next(
            (item for item in self.items if item.dish_id == dish_id), None
        )

        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = CartItem(dish_id=dish_id, quantity=quantity, price=price)
            self.items.append(new_item)

        self._recalculate_total()
