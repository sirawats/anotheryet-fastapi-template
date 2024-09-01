from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class Post(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class PostWithAuthor(Post):
    author: "User"


# To avoid circular import issues, use forward references
from app.api.v1.users.schema import User

PostWithAuthor.model_rebuild()
