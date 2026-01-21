"""
Schema for Comment operations
"""
from pydantic import BaseModel
from datetime import datetime


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    request_id: int
    author_email: str
    author_name: str
    author_role: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
