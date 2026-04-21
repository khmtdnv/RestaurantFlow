from decimal import Decimal

from domain.aggregates.order import OrderStatus
from pydantic import BaseModel, ConfigDict, field_serializer


class OrderItemResponseDTO(BaseModel):
    dish_id: int
    quantity: int
    price: Decimal

    @field_serializer("price")
    def serialize_price(self, price: Decimal) -> str:
        return f"{price:.2f}"

    model_config = ConfigDict(from_attributes=True)


class OrderResponseDTO(BaseModel):
    status: OrderStatus
    items: list[OrderItemResponseDTO]
    total_price: Decimal
    payment_url: str | None

    @field_serializer("total_price")
    def serialize_total_price(self, price: Decimal) -> str:
        return f"{price:.2f}"

    model_config = ConfigDict(from_attributes=True)


class OrderWithUrlResponseDTO(BaseModel):
    order: OrderResponseDTO
    payment_url: str | None
