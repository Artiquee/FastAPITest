from pydantic import BaseModel
from typing import Optional


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    autoreply: Optional[bool] = None
    autoreply_delay: Optional[int] = 0
    autoreply_msg: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class PostScheme(PostBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
