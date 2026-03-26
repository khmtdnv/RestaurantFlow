from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ItemSyncDTO(BaseModel):
    id: int
    name: str
    price: Decimal
    is_available: bool = True
    updated_at: datetime


class MenuSyncEventDTO(BaseModel):
    menu: list[ItemSyncDTO]
