import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    full_name: Annotated[str, Field(min_length=1, max_length=255)]
    email: Annotated[EmailStr, Field(description="User email")]
    password: Annotated[str, Field(min_length=6, max_length=6)]


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    profile_image_url: str | None = None
    name: str
    token: str | None = None
    about: str | None = None
    bio: str | None = None
    phone: str | None = None
    address: str | None = None
    location: str | None = None
    facebook_url: str | None = None
    instagram_url: str | None = None
    twitter_url: str | None = None
    linkedin_url: str | None = None
    youtube_url: str | None = None
    tiktok_url: str| None = None
    website_url: str | None = None
    is_active: bool | None = None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None

class SignupResponse(BaseModel):
    id: int
    email: EmailStr
    name: str

class APIResponse(BaseModel):
    message: str
    data: dict
    status: str
    code: int
    success: bool


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(description="User email")]
    password: Annotated[str, Field(min_length=6, max_length=6)]


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str    # token_type: str = "bearer"
    # expires_in: int


class ForgetPasswordRequest(BaseModel):
    email: EmailStr

class ForgetPasswordReset(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class UserSocialLinkCreate(BaseModel):
    platform: str
    url: str


class UserSocialLinkResponse(BaseModel):
    id: int
    user_id: int
    platform: str
    url: str


class UserNotificationUpdate(BaseModel):
    app_reminder: Optional[bool] = None
    daily_prompts: Optional[bool] = None
    follow_notification: Optional[bool] = None
    react_notification: Optional[bool] = None
    auto_renew_notification: Optional[bool] = None


class UserNotificationResponse(BaseModel):
    id: int
    user_id: int
    app_reminder: bool
    daily_prompts: bool
    follow_notification: bool
    react_notification: bool
    auto_renew_notification: bool

class UserReportCreate(BaseModel):
    reported_user_id: int
    reason: str


class UserReportResponse(BaseModel):
    id: int
    reported_user_id: int
    reporter_id: int
    reason: str
    status: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    about: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    twitter_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    youtube_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    website_url: Optional[str] = None
    is_active: Optional[bool] = None