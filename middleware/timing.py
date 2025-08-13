import time
import logging
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.timing")


class TimingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, slow_ms: int = 500):
        super().__init__(app)
        self.slow_ms = slow_ms

    async def dispatch(self, request: Request, call_next: Callable):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Process-Time"] = str(duration_ms)
        if duration_ms >= self.slow_ms:
            logger.warning("slow request", extra={"path": request.url.path, "ms": duration_ms})
        return response