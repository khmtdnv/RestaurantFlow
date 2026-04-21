from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class AddItemToCartRequestDTO(BaseModel):
    dish_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class CartItemResponseDTO(BaseModel):
    dish_id: int
    quantity: int
    price: Decimal

    @field_serializer("price")
    def serialize_price(self, price: Decimal) -> str:
        return f"{price:.2f}"

    model_config = ConfigDict(from_attributes=True)


class CartResponseDTO(BaseModel):
    total_price: Decimal
    items: list[CartItemResponseDTO]

    @field_serializer("total_price")
    def serialize_total_price(self, price: Decimal) -> str:
        return f"{price:.2f}"

    model_config = ConfigDict(from_attributes=True)
