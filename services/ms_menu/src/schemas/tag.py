from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    name: str


class TagOut(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TagCreateIn(TagBase):
    pass


class TagUpdateIn(BaseModel):
    name: str | None = None


class TagSimpleOut(BaseModel):
    id: int
    name: str | None
