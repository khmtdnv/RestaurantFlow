from pydantic import BaseModel, Field


class AddItemToCartRequestDTO(BaseModel):
    dish_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
