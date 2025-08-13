from pydantic import BaseModel
from typing import Annotated
from datetime import datetime


class CommentCreate(BaseModel):
    text: Annotated[str, "The text of the comment"]
    journal_id: int


class CommentUpdate(BaseModel):
    text: str


class CommentResponse(BaseModel):
    id: int
    user_id: int
    journal_id: int
    text: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime