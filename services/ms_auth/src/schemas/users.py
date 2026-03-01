from typing import Any

from pydantic import BaseModel


class EditUserRequestDTO(BaseModel):
    id: int
    name: str | None
    phone_number: str | None


class EditUserResponseDTO(BaseModel):
    status: str
    message: str


class UserProfileUpdate(BaseModel):
    name: str | None
    phone_number: str | None


class UserSchema(BaseModel):
    id: int
    name: str
    phone_number: str

    class Config:
        from_attributes = True


class UserSchemaAdd(BaseModel):
    name: str
    phone_number: str


class UserSchemaEdit(BaseModel):
    is_phone_verified: bool | None
    refresh_token: str | None
    token_expires_at: Any | None
