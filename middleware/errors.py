import logging
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.errors")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception(
                "Unhandled error",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                },
            )
            raise