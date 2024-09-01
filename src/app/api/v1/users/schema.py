from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserWithPosts(User):
    posts: List["Post"] = []


# To avoid circular import issues, use forward references
from app.api.v1.posts.schema import Post

UserWithPosts.model_rebuild()
