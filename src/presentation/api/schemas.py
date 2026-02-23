import re

from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    name: str
    phone_number: str


class UserRead(BaseModel):
    id: int
    name: str
    phone_number: str
    is_active: bool
    is_superuser: bool
    is_phone_verified: bool

    class Config:
        from_attributes = True


class VerifyCodeRequest(BaseModel):
    phone_number: str = Field(..., examples=["+79991234567"])
    code: str = Field(..., min_length=4, max_length=4, examples=["1234"])

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^(\+7|8)9\d{9}$", v):
            raise ValueError("Неверный формат российского номера телефона")
        return v


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class PhoneRequest(BaseModel):
    phone_number: str


class ResendCodeRequest(BaseModel):
    phone_number: str
