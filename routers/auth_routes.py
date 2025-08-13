# from typing import Annotated

# from fastapi import APIRouter, Depends, HTTPException, status
# from passlib.context import CryptContext
# from sqlmodel import Session, select

# from db.sqlmodel import get_session
# from models.user import User
# from schemas.common import APIResponse
# from schemas.user import SignupRequest, LoginRequest, UserResponse, LoginResponse, ForgetPasswordRequest
# from security.jwt import create_access_token

# router = APIRouter(prefix="/auth", tags=["auth"])

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)


# def verify_password(password: str, password_hash: str) -> bool:
#     return pwd_context.verify(password, password_hash)


# def build_user_response(user: User, token: str | None = None) -> UserResponse:
#     return UserResponse(
#         id=user.id,  # type: ignore[arg-type]
#         email=user.email,
#         name=user.name,
#         token=token or "",
#         phone=user.phone,
#         address=user.address,
#         facebook_url=user.facebook_url,
#         instagram_url=user.instagram_url,
#         twitter_url=user.twitter_url,
#         linkedin_url=user.linkedin_url,
#         youtube_url=user.youtube_url,
#         tiktok_url=user.tiktok_url,
#         website_url=user.website_url,
#         is_active=user.is_active,
#     )


# async def _signup_user(data: SignupRequest, session: Session) -> APIResponse[UserResponse]:
#     existing = session.exec(select(User).where(User.email == data.email)).first()
#     if existing:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

#     user = User(email=data.email, name=data.full_name, password_hash=hash_password(data.password))
#     session.add(user)
#     session.commit()
#     session.refresh(user)
#     payload = build_user_response(user)
#     return APIResponse[UserResponse](message="User created successfully", data=payload)


# @router.post("/signup", response_model=APIResponse[UserResponse])
# async def signup(payload: Annotated[SignupRequest, Depends()], session: Annotated[Session, Depends(get_session)]):
#     return await _signup_user(payload, session)


# @router.post("/login", response_model=APIResponse[LoginResponse])
# async def login(payload: Annotated[LoginRequest, Depends()], session: Annotated[Session, Depends(get_session)]):
#     user = session.exec(select(User).where(User.email == payload.email)).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")
#     if not verify_password(payload.password, user.password_hash):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

#     token = create_access_token(subject=str(user.id))
#     user_payload = build_user_response(user, token=token)
#     login_payload = LoginResponse(user=user_payload, access_token=token)
#     return APIResponse[LoginResponse](message="Login successful", data=login_payload)