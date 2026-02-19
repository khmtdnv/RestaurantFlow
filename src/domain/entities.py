from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserDomain(BaseModel):

    id: Optional[int] = None
    name: str
    phone_number: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_phone_verified: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

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
