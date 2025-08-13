from pydantic import BaseModel
from typing import Optional, Annotated
from datetime import datetime


class JournalCreate(BaseModel):
    title: Annotated[str, "The title of the journal"]
    body_snippet: Optional[str] = None
    html_content: Optional[str] = None
    is_private: bool = False
    image_url: Optional[str] = None


class JournalUpdate(BaseModel):
    title: Optional[str] = None
    body_snippet: Optional[str] = None
    html_content: Optional[str] = None
    is_private: Optional[bool] = None
    image_url: Optional[str] = None


class JournalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    body_snippet: Optional[str] = None
    html_content: Optional[str] = None
    is_private: bool
    image_url: Optional[str] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class JournalTagCreate(BaseModel):
    journal_id: int
    tag: str


class JournalTagResponse(BaseModel):
    id: int
    journal_id: int
    tag: str


class JournalReactionCreate(BaseModel):
    journal_id: int
    reaction_type: str


class JournalReactionResponse(BaseModel):
    id: int
    journal_id: int
    user_id: int
    reaction_type: str


class JournalFavoriteCreate(BaseModel):
    journal_id: int


class JournalFavoriteResponse(BaseModel):
    id: int
    journal_id: int
    user_id: int


class JournalShareCreate(BaseModel):
    journal_id: int
    share_type: str = "internal"


class JournalShareResponse(BaseModel):
    id: int
    journal_id: int
    user_id: int
    share_type: str


class JournalReportCreate(BaseModel):
    journal_id: int
    reason: str


class JournalReportResponse(BaseModel):
    id: int
    journal_id: int
    reporter_id: int
    reason: str
    status: str
