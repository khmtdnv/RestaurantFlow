from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Item:
    id: int
    name: str
    price: Decimal
    is_available: bool
