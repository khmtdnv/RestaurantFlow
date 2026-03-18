from decimal import Decimal
from typing import List

from pydantic import BaseModel


class Menu(BaseModel):
    id: int
    name: str
    price: Decimal
    is_available: bool


class MenuSyncEvent(BaseModel):
    menu: List[Menu]
