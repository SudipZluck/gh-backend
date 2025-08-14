from datetime import datetime, timedelta, timezone
from random import choices, random
import string
from typing import Annotated, List

from fastapi import APIRouter, Body, Depends,  HTTPException, status
from passlib.context import CryptContext
from sqlmodel import Session, select

from db.sqlmodel import get_session
from models.user import ForgetPassword, User, UserNotifications, UserReports, UserSocialLinks
from schemas.common import APIResponse
from schemas.user import ForgetPasswordReset, SignupRequest, LoginRequest, SignupResponse, UserNotificationResponse, UserNotificationUpdate, UserReportCreate, UserReportResponse, UserResponse, LoginResponse, ForgetPasswordRequest, UserSocialLinkCreate, UserSocialLinkResponse
from security.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from security.dependencies import get_current_user
from services.mail_service import send_mail

router = APIRouter(prefix="/user", tags=["user"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def user_to_response(user: User) -> APIResponse[SignupResponse]:
    payload = SignupResponse(id=user.id, email=user.email, name=user.name)
    return APIResponse[SignupResponse](message="User created successfully", data=payload)


async def _signup_user(data: SignupRequest, session: Session) -> APIResponse[SignupResponse]:
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=data.email, name=data.full_name, password_hash=hash_password(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user_to_response(user)


@router.post("/signup", response_model=APIResponse[SignupResponse])
async def signup(payload: Annotated[SignupRequest,...], session: Annotated[Session, Depends(get_session)]):
    return await _signup_user(payload, session)


@router.post("/login", response_model=APIResponse[UserResponse])
async def login(payload: Annotated[LoginRequest, ...], session: Annotated[Session, Depends(get_session)]):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    user_payload = UserResponse(id=user.id, email=user.email, name=user.name, token=token, about=user.about)

    return APIResponse[UserResponse](message="Login successful", data=user_payload)

@router.post("/forget-password", response_model=APIResponse, response_model_exclude_none=True)
async def forget_password(
    request: ForgetPasswordRequest,
    session: Annotated[Session, Depends(get_session)],
):
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    otp = "".join(choices(string.digits, k=6))
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=10)

    forget_password_entry = session.get(ForgetPassword, request.email)
    if forget_password_entry:
        forget_password_entry.otp = otp
        forget_password_entry.expiretime = expire_time
    else:
        forget_password_entry = ForgetPassword(
            email=request.email, otp=otp, expiretime=expire_time
        )
    session.add(forget_password_entry)
    session.commit()
    await send_mail(otp, user.name, user.email)

    # Here you would send the OTP to the user's email.
    # For this example, we will just return it in the response.
    return APIResponse(
        message="OTP sent to your email",
    )

@router.post("/reset-password", response_model=APIResponse, response_model_exclude_none=True)
async def reset_password(
    request: ForgetPasswordReset,
    session: Annotated[Session, Depends(get_session)],
):
    forget_password_entry = session.get(ForgetPassword, request.email)
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not forget_password_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid request"
        )

    if (
        forget_password_entry.otp != request.otp
        or forget_password_entry.expiretime < datetime.utcnow()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP"
        )

    user.password_hash = hash_password(request.new_password)
    session.add(user)
    session.delete(forget_password_entry)
    session.commit()
    return APIResponse(message="Password reset successfully")


@router.post("/social-links", response_model=APIResponse[UserSocialLinkResponse])
async def create_social_link(
    social_link_data: UserSocialLinkCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    social_link = UserSocialLinks(
        **social_link_data.model_dump(), user_id=current_user.id
    )
    session.add(social_link)
    session.commit()
    session.refresh(social_link)
    return APIResponse(
        message="Social link created successfully",
        data=social_link,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )


@router.get("/social-links", response_model=APIResponse[List[UserSocialLinkResponse]])
async def get_social_links(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    social_links = session.exec(
        select(UserSocialLinks).where(UserSocialLinks.user_id == current_user.id)
    ).all()
    return APIResponse(
        message="Social links retrieved successfully",
        data=social_links,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.delete("/social-links/{social_link_id}", response_model=APIResponse)
async def delete_social_link(
    social_link_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    social_link = session.get(UserSocialLinks, social_link_id)
    if not social_link or social_link.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Social link not found"
        )

    session.delete(social_link)
    session.commit()
    return APIResponse(
        message="Social link deleted successfully",
        data={},
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.put(
    "/notifications", response_model=APIResponse[UserNotificationResponse]
)
async def update_notifications(
    notification_data: UserNotificationUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    notification_settings = session.exec(
        select(UserNotifications).where(UserNotifications.user_id == current_user.id)
    ).first()

    if not notification_settings:
        notification_settings = UserNotifications(user_id=current_user.id)

    for key, value in notification_data.model_dump(exclude_unset=True).items():
        setattr(notification_settings, key, value)

    session.add(notification_settings)
    session.commit()
    session.refresh(notification_settings)
    return APIResponse(
        message="Notification settings updated successfully",
        data=notification_settings,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )


@router.get(
    "/notifications", response_model=APIResponse[UserNotificationResponse]
)
async def get_notifications(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    notification_settings = session.exec(
        select(UserNotifications).where(UserNotifications.user_id == current_user.id)
    ).first()

    if not notification_settings:
        notification_settings = UserNotifications(user_id=current_user.id)
        session.add(notification_settings)
        session.commit()
        session.refresh(notification_settings)

    return APIResponse(
        message="Notification settings retrieved successfully",
        data=notification_settings,
        success=True,
        status="success",
        code=status.HTTP_200_OK,
    )

@router.post("/user-reports", response_model=APIResponse[UserReportResponse])
async def create_user_report(
    user_report_data: UserReportCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    user_report = UserReports(
        **user_report_data.model_dump(), reporter_id=current_user.id
    )
    session.add(user_report)
    session.commit()
    session.refresh(user_report)
    return APIResponse(
        message="User report created successfully",
        data=user_report,
        success=True,
        status="success",
        code=status.HTTP_201_CREATED,
    )