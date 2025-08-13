from datetime import datetime
from typing import Optional, Annotated, List

from sqlmodel import SQLModel, Field, Relationship
from models.user import User


class Journal(SQLModel, table=True):
    __tablename__ = "journals"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    title: Annotated[str, Field(max_length=255)]
    body_snippet: Annotated[Optional[str], Field(default=None)]
    html_content: Annotated[Optional[str], Field(default=None)]
    is_private: Annotated[bool, Field(default=False)]
    image_url: Annotated[Optional[str], Field(default=None)]
    is_deleted: Annotated[bool, Field(default=False)]
    deleted_at: Annotated[Optional[datetime], Field(default=None)]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]
    updated_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]

    user: Optional[User] = Relationship(back_populates="journals")
    comments: List["Comment"] = Relationship(back_populates="journal")

class JournalTags(SQLModel, table=True):
    __tablename__ = "journal_tags"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    journal_id: Annotated[int, Field(foreign_key="journals.id")]
    tag: Annotated[str, Field(max_length=100)]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]


class JournalReactions(SQLModel, table=True):
    __tablename__ = "journal_reactions"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    journal_id: Annotated[int, Field(foreign_key="journals.id")]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    reaction_type: str
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]


class JournalFavorites(SQLModel, table=True):
    __tablename__ = "journal_favorites"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    journal_id: Annotated[int, Field(foreign_key="journals.id")]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]


class JournalShares(SQLModel, table=True):
    __tablename__ = "journal_shares"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    journal_id: Annotated[int, Field(foreign_key="journals.id")]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    share_type: Annotated[str, Field(default="internal")]
    shared_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]


class JournalReports(SQLModel, table=True):
    __tablename__ = "journal_reports"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    journal_id: Annotated[int, Field(foreign_key="journals.id")]
    reporter_id: Annotated[int, Field(foreign_key="users.id")]
    reason: str
    status: Annotated[str, Field(default="pending")]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]
    resolved_at: Optional[datetime] = None