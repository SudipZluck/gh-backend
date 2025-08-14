#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiaWF0IjoxNzU1MTQ3NjgxfQ.SiIyJwZMB7OyyepOajnKLowgxvENlzAJspSblGnyetk
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    status: bool = True
    message: str = "OK"
    data: Optional[T] = None