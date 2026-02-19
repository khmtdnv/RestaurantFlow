from pydantic import BaseModel


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
