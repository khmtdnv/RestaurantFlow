from pydantic import BaseModel, EmailStr


# То, что юзер шлет нам при регистрации
class UserCreate(BaseModel):
    name: str
    phone_number: str


# То, что мы отдаем юзеру (без пароля!)
class UserRead(BaseModel):
    id: int
    name: str
    phone_number: str
    is_active: bool
    is_superuser: bool
    is_phone_verified: bool

    # Нужно для конвертации SQLAlchemy модели -> Pydantic
    class Config:
        from_attributes = True
