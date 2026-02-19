from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserDomain(BaseModel):
    id: Optional[int] = None
    name: str
    phone_number: str
    is_active: bool = True
    is_superuser: bool = False
    is_phone_verified: bool = False
    created_at: Optional[datetime] = None

    # Бизнес-логика находится прямо в модели
    def verify_phone(self):
        if self.is_phone_verified:
            raise ValueError(
                "Телефон уже верифицирован"
            )  # Лучше использовать кастомные exceptions
        self.is_phone_verified = True
        self.is_active = True

    def block_user(self):
        self.is_active = False
