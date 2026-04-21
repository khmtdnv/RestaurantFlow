from dataclasses import dataclass
from decimal import Decimal


@dataclass
class OrderItem:
    dish_id: int
    quantity: int
    price: Decimal
