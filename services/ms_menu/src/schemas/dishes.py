from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator
from schemas.tag import TagOut


class DishBase(BaseModel):
    name: str
    price: Decimal
    description: str | None = None
    is_available: bool
    category_id: int | None = None


class DishCreateIn(DishBase):
    tag_ids: list[int] = []

    @field_validator("tag_ids")
    @classmethod
    def check_unique_tags(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("Массив тэгов содержит дубликаты")
        return v


class DishUpdateIn(BaseModel):
    name: str | None = None
    price: Decimal | None = None
    description: str | None = None
    is_available: bool | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None

    @field_validator("tag_ids")
    @classmethod
    def check_unique_tags(cls, v: list[int]) -> list[int]:
        if len(v) != len(set(v)):
            raise ValueError("Массив тэгов содержит дубликаты")
        return v


class DishOut(DishBase):
    id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DishOutWithTags(DishOut):
    tags: list[TagOut] = []
