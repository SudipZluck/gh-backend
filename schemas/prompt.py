from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PromptCreate(BaseModel):
    text: str


class PromptResponse(BaseModel):
    id: int
    text: str
    user_id: Optional[int] = None
    is_active: bool
    created_at: datetime


class UserPromptCreate(BaseModel):
    text: str


class UserPromptResponse(BaseModel):
    id: int
    user_id: int
    text: str
    is_active: bool