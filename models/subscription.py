from datetime import datetime
from typing import Optional, Annotated

from sqlmodel import SQLModel, Field


class UserSubscriptions(SQLModel, table=True):
    __tablename__ = "user_subscriptions"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    package_name: Annotated[str, Field(max_length=255)]
    status: Annotated[str, Field(default="active")]
    start_date: Annotated[datetime, Field(default_factory=datetime.utcnow)]
    end_date: Optional[datetime] = None
    auto_renew: Annotated[bool, Field(default=True)]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]


class UserPaymentMethods(SQLModel, table=True):
    __tablename__ = "user_payment_methods"

    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    user_id: Annotated[int, Field(foreign_key="users.id")]
    card_type: Optional[str] = None
    card_number_hash: Optional[str] = None
    expiry_date: Optional[str] = None
    cvv_hash: Optional[str] = None
    is_default: Annotated[bool, Field(default=False)]
    created_at: Annotated[datetime, Field(default_factory=datetime.utcnow, nullable=False)]