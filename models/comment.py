from datetime import datetime
from typing import Optional, Annotated

from sqlmodel import SQLModel, Field, Relationship
from models.user import User
from models.journal import Journal


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    journal_id: Annotated[int, Field(foreign_key="journals.id")]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    text: str
    is_deleted: Annotated[bool, Field(default=False)]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]
    updated_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]

    user: Optional[User] = Relationship(back_populates="comments")
    journal: Optional[Journal] = Relationship(back_populates="comments")