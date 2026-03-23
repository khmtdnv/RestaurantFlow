from decimal import Decimal

from domain.aggregates.order import OrderStatus
from pydantic import BaseModel


class AddItemRequest(BaseModel):
    dish_id: int
    quantity: int
    price: Decimal


class OrderItemOut(BaseModel):
    dish_id: int
    quantity: int
    price: Decimal


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    price: Decimal
    items: list[OrderItemOut]
