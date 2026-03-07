from dataclasses import dataclass
from decimal import Decimal


@dataclass
class DishCreateDTO:
    name: str
    price: Decimal
    description: str | None
    category_id: int | None
    is_available: bool


@dataclass
class DishUpdateDTO:
    id: int
    name: str | None
    price: Decimal | None
    description: str | None
    category_id: int | None
    is_available: bool | None
