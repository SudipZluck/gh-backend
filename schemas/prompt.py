from pydantic import BaseModel
from typing import Optional


class PromptCreate(BaseModel):
    text: str
    category: Optional[str] = None


class PromptResponse(BaseModel):
    id: int
    text: str
    category: Optional[str] = None
    is_active: bool


class UserPromptCreate(BaseModel):
    prompt_text: str


class UserPromptResponse(BaseModel):
    id: int
    user_id: int
    prompt_text: str
    is_active: bool