import datetime

from pydantic import BaseModel, ConfigDict
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
    dishes: list[DishOut]


class MenuOut(BaseModel):
    categories: list[CategoryWithDishesOut]
    uncategorized_dishes: list[DishOut]

    model_config = ConfigDict(from_attributes=True)
