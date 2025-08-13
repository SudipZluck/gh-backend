from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user import User
from models.subscription import UserSubscriptions, UserPaymentMethods
from schemas.subscription import (
    UserSubscriptionCreate,
    UserSubscriptionResponse,
    UserPaymentMethodCreate,
    UserPaymentMethodResponse,
)
from security.dependencies import get_current_user
from db.sqlmodel import get_session
from schemas.common import APIResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/", response_model=APIResponse[UserSubscriptionResponse])
async def create_subscription(
    subscription_data: UserSubscriptionCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    subscription = UserSubscriptions(
        **subscription_data.model_dump(), user_id=current_user.id
    )
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return APIResponse(
        message="Subscription created successfully",
        data=subscription,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.get("/", response_model=APIResponse[List[UserSubscriptionResponse]])
async def get_subscriptions(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    subscriptions = session.exec(
        select(UserSubscriptions).where(UserSubscriptions.user_id == current_user.id)
    ).all()
    return APIResponse(
        message="Subscriptions retrieved successfully",
        data=subscriptions,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.post(
    "/payment-methods", response_model=APIResponse[UserPaymentMethodResponse]
)
async def create_payment_method(
    payment_method_data: UserPaymentMethodCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    payment_method = UserPaymentMethods(
        user_id=current_user.id,
        card_type=payment_method_data.card_type,
        card_number_hash=f"hashed_{payment_method_data.card_number[-4:]}",
        expiry_date=payment_method_data.expiry_date,
        cvv_hash="hashed_cvv",
        is_default=payment_method_data.is_default,
    )
    session.add(payment_method)
    session.commit()
    session.refresh(payment_method)
    return APIResponse(
        message="Payment method created successfully",
        data=payment_method,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.get(
    "/payment-methods", response_model=APIResponse[List[UserPaymentMethodResponse]]
)
async def get_payment_methods(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    payment_methods = session.exec(
        select(UserPaymentMethods).where(UserPaymentMethods.user_id == current_user.id)
    ).all()
    return APIResponse(
        message="Payment methods retrieved successfully",
        data=payment_methods,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )