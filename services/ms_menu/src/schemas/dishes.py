from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DishBase(BaseModel):
    name: str
    price: Decimal
    description: str | None = None
    is_available: bool
    category_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class DishCreateIn(DishBase):
    pass


class DishUpdateIn(BaseModel):
    name: str | None = None
    price: Decimal | None = None
    description: str | None = None
    is_available: bool | None = None
    category_id: int | None = None
    model_config = ConfigDict(from_attributes=True)


class DishOut(DishBase):
    id: int
