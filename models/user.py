from datetime import datetime
from typing import Optional, Annotated, List

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    email: Annotated[str, Field(index=True, unique=True, max_length=255)]
    profile_image_url: Annotated[str, Field(index=True, unique=True, max_length=255)]
    name: Annotated[str, Field(max_length=255)]
    password_hash: Annotated[str, Field(max_length=255)]
    profile_image_url: Annotated[Optional[str], Field(max_length=255, default=None)]
    is_active: Annotated[bool, Field(default=True)]
    about: Annotated[Optional[str], Field(max_length=255, default=None)]
    bio: Annotated[Optional[str], Field(default=None)]
    phone: Annotated[Optional[str], Field(max_length=255, default=None)]
    address: Annotated[Optional[str], Field(max_length=255, default=None)]
    location: Annotated[Optional[str], Field(max_length=255, default=None)]
    facebook_url: Annotated[Optional[str], Field(max_length=255, default=None)]
    instagram_url: Annotated[Optional[str], Field(max_length=255, default=None)]
    twitter_url: Annotated[Optional[str], Field(max_length=255, default=None)]
    linkedin_url: Annotated[Optional[str], Field(max_length=255, default=None)]
    youtube_url: Annotated[Optional[str], Field(max_length=255, default=None)]
    tiktok_url: Annotated[Optional[str], Field(max_length=255, default=None)]
    website_url: Annotated[Optional[str], Field(max_length=255, default=None)]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]
    updated_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]
    journals: List["Journal"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")

class ForgetPassword(SQLModel, table=True):
    __tablename__ = "forget_password"
    email: Annotated[str, Field(primary_key=True, max_length=255)]
    expiretime: datetime
    otp: Annotated[str, Field(max_length=100)]


class UserSocialLinks(SQLModel, table=True):
    __tablename__ = "user_social_links"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    platform: Annotated[str, Field(max_length=255)]
    url: str
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]


class UserNotifications(SQLModel, table=True):
    __tablename__ = "user_notifications"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    app_reminder: Annotated[bool, Field(default=True)]
    daily_prompts: Annotated[bool, Field(default=True)]
    follow_notification: Annotated[bool, Field(default=True)]
    react_notification: Annotated[bool, Field(default=True)]
    auto_renew_notification: Annotated[bool, Field(default=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]
    updated_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]

class UserReports(SQLModel, table=True):
    __tablename__ = "user_reports"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    reported_user_id: Annotated[int, Field(foreign_key="users.id")]
    reporter_id: Annotated[int, Field(foreign_key="users.id")]
    reason: str
    status: Annotated[str, Field(default="pending")]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]
    resolved_at: Optional[datetime] = None