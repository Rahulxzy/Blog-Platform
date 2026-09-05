from datetime import datetime
from pydantic import BaseModel, ConfigDict,EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=1, max_length=10000)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int

    model_config = ConfigDict(from_attributes=True)


class PostDetailResponse(PostResponse):
    comments: list[CommentResponse] = Field(default_factory=list)