from decimal import Decimal

from pydantic import BaseModel


class AddItemToCartRequest(BaseModel):
    dish_id: int
    quantity: int
