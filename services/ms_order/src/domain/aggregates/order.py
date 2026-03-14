from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Order:
    dishes: list[int]
    price: Decimal
    id: int | None = None
