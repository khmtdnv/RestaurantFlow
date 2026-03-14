import datetime

from pydantic import BaseModel, ConfigDict


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


class MenuCategoryOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# class CategoryWithDishesOut(CategoryOut):
#     dishes: list[DishOutWithTags]


# class MenuOut(BaseModel):
#     available_categorized_dishes: list[CategoryWithDishesOut]
#     available_uncategorized_dishes: list[DishOutWithTags]

#     model_config = ConfigDict(from_attributes=True)
