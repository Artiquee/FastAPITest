from pydantic import BaseModel
from typing import Optional


class CommentBase(BaseModel):
    content: str
    post_id: int


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class CommentScheme(CommentBase):
    id: int
    post_id: int
    author_id: int

    class Config:
        orm_mode = True


class ResponseStatus(BaseModel):
    status: str
    data: Optional[CommentScheme] = None
    detail: Optional[str] = None


class DailyCommentSummary(BaseModel):
    date: str
    total_comments: int
    blocked_comments: int
