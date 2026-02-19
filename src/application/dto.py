from pydantic import BaseModel, ConfigDict


class UserCreateDTO(BaseModel):
    name: str
    phone_number: str


class UserDTO(BaseModel):
    id: int
    name: str
    phone_number: str
    is_active: bool
    is_superuser: bool
    is_phone_verified: bool

    model_config = ConfigDict(from_attributes=True)
