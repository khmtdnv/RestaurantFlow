from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator
from schemas.dishes import DishOut


class ComboBase(BaseModel):
    name: str
    price: Decimal


class ComboOut(ComboBase):
    id: int
    dishes: list[DishOut]
    model_config = ConfigDict(from_attributes=True)


class ComboSimpleOut(ComboBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ComboCreateIn(ComboBase):
    dishes_ids: list[int] = []

    @field_validator("dishes_ids")
    @classmethod
    def check_unique_dishes(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("Массив блюд содержит дубликаты")
        return v


class ComboUpdateIn(BaseModel):
    name: str | None = None
    price: Decimal | None = None
    dishes_ids: list[int] | None = None

    @field_validator("dishes_ids")
    @classmethod
    def check_unique_dishes(cls, v: list[int] | None) -> list[int] | None:
        if v is not None and len(v) != len(set(v)):
            raise ValueError("Массив блюд содержит дубликаты")
        return v
