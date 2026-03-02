import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from schemas.dishes import DishOut


class CategoryBase(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class CategoryCreateIn(CategoryBase):
    pass


class CategoryUpdateIn(BaseModel):
    name: str | None = None


class CategoryOut(CategoryBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class CategoryWithDishesOut(CategoryOut):
    dishes: list["DishOut"]


class HTTPResponse(BaseModel):
    status: str
    message: str
