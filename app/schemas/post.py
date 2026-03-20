from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(PostCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
