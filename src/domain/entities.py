from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class UserDomain(BaseModel):
    id: Optional[int] = None
    name: str
    phone_number: str
    is_active: bool = True
    is_superuser: bool = False
    is_phone_verified: bool = False
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    def verify_phone(self):
        if self.is_phone_verified:
            raise ValueError("Телефон уже верифицирован")
        self.is_phone_verified = True
        self.is_active = True

    def set_refresh_token(self, token: str, expires_in: timedelta):
        """Метод для обновления токена в доменной модели"""
        self.refresh_token = token
        self.token_expires_at = datetime.now(timezone.utc) + expires_in

    def block_user(self):
        self.is_active = False


def get_expiration_time() -> datetime:
    return datetime.now() + timedelta(minutes=5)


class PhoneVerification(BaseModel):
    id: int | None = None
    phone_number: str
    code: str
    is_used: bool = False
    expires_at: datetime = Field(default_factory=get_expiration_time)
    attempts_count: int = 0
    max_attempts: int = 5

    model_config = ConfigDict(from_attributes=True)

    def verify(self, input_code: str, current_time: datetime):
        if self.is_used:
            raise ValueError("Этот код уже был использован")
        if current_time > self.expires_at:
            raise ValueError("Время действия кода истекло")
        if self.attempts_count >= self.max_attempts:
            raise ValueError("Превышено максимальное количество попыток")
        if input_code != self.code:
            self.attempts_count += 1
            raise ValueError("Неверный код")

        self.attempts_count = 0
        self.is_used = True
