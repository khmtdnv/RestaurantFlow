from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CartItem:
    """Single cart item entity."""

    # dish_id and quantity comes from frontend
    dish_id: int
    quantity: int
    # price needs to be taken from DB
    price: Decimal
