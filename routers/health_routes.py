from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, text

from db.sqlmodel import get_session
from schemas.common import APIResponse

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/db", response_model=APIResponse[dict[str, str]])
def health_db(session: Annotated[Session, Depends(get_session)]):
    session.exec(text("SELECT 1"))
    return APIResponse(message="Database healthy", data={"db": "ok"})


