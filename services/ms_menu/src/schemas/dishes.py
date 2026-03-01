from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DishBase(BaseModel):
    name: str
    price: Decimal
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DishCreateIn(DishBase):
    category_id: int


class DishOut(DishBase):
    id: int
    category_id: int
