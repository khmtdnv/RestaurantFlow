from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    name: str
    phone_number: str

    class Config:
        from_attributes = True


class UserSchemaAdd(BaseModel):
    name: str
    phone_number: str
