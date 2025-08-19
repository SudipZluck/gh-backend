from datetime import datetime
from typing import Optional, Annotated, List

from sqlmodel import SQLModel, Field, Relationship

from models.user import User


class JournalTagLink(SQLModel, table=True):
    __tablename__ = "journal_tag_link"
    journal_id: Annotated[
        Optional[int],
        Field(default=None, foreign_key="journals.id", primary_key=True),
    ]
    tag_id: Annotated[
        Optional[int], Field(default=None, foreign_key="tags.id", primary_key=True)
    ]


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    name: Annotated[str, Field(index=True, unique=True, max_length=100)]
    journals: List["Journal"] = Relationship(
        back_populates="tags", link_model=JournalTagLink
    )


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
    created_at: Annotated[
        datetime, Field(default_factory=datetime.utcnow, nullable=False)
    ]
    updated_at: Annotated[
        datetime, Field(default_factory=datetime.utcnow, nullable=False)
    ]

    user: Optional[User] = Relationship(back_populates="journals")
    comments: List["Comment"] = Relationship(back_populates="journal")
    tags: List[Tag] = Relationship(back_populates="journals", link_model=JournalTagLink)


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