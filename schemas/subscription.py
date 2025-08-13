from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserSubscriptionCreate(BaseModel):
    package_name: str
    end_date: Optional[datetime] = None
    auto_renew: bool = True


class UserSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    package_name: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool


class UserPaymentMethodCreate(BaseModel):
    card_type: Optional[str] = None
    card_number: str
    expiry_date: str
    cvv: str
    is_default: bool = False


class UserPaymentMethodResponse(BaseModel):
    id: int
    user_id: int
    card_type: Optional[str] = None
    card_number_mask: str
    expiry_date: Optional[str] = None
    is_default: bool