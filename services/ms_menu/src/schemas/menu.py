from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from schemas.categories import MenuCategoryOut
from schemas.combo import ComboSimpleOut
from schemas.tag import TagOut

T = TypeVar("T")


class DishFullOut(BaseModel):
    id: int
    name: str
    price: Decimal
    description: str | None = None
    category: MenuCategoryOut | None
    combos: list[ComboSimpleOut]
    tags: list[TagOut]
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MenuOut(BaseModel):
    menu: list[DishFullOut]

    model_config = ConfigDict(from_attributes=True)


class LimitOffsetResponse(BaseModel, Generic[T]):
    data: T
    limit: int
    offset: int
    total: int
    returned_count: int
    has_next: bool
    has_prev: bool
    next_offset: int | None
    prev_offset: int | None


class PaginatedResponse(BaseModel, Generic[T]):
    data: T
    current_page: int
    per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class CursorResponse(BaseModel, Generic[T]):
    data: T
    next_cursor: str
    size: int
