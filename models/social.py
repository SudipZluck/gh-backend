from datetime import datetime
from typing import Optional, Annotated

from sqlmodel import SQLModel, Field, Relationship
from models.user import User


class UserFollows(SQLModel, table=True):
    __tablename__ = "user_follows"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    follower_id: Annotated[int, Field(foreign_key="users.id")]
    following_id: Annotated[int, Field(foreign_key="users.id")]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]


class UserBlocks(SQLModel, table=True):
    __tablename__ = "user_blocks"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    blocker_id: Annotated[int, Field(foreign_key="users.id")]
    blocked_id: Annotated[int, Field(foreign_key="users.id")]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]