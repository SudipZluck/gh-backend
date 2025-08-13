from datetime import datetime
from typing import Optional, Annotated

from sqlmodel import SQLModel, Field


class Prompts(SQLModel, table=True):
    __tablename__ = "prompts"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    text: str
    category: Optional[str] = None
    is_active: Annotated[bool, Field(default=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]


class UserPrompts(SQLModel, table=True):
    __tablename__ = "user_prompts"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    prompt_text: str
    is_active: Annotated[bool, Field(default=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]