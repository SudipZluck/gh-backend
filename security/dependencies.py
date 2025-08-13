from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from db.sqlmodel import get_session
from models.user import User
from security.jwt import decode_access_token


def get_bearer_token(authorization: Annotated[str | None, Header(alias="Authorization")]) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    return parts[1]


async def get_current_user(
    token: Annotated[str, Depends(get_bearer_token)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    claims = decode_access_token(token)
    subject = claims.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    try:
        user_id = int(subject)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user