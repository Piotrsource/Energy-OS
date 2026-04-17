"""
In-memory sliding-window rate limiter (per-user or per-IP).
Phase 2 replaces this with a Redis-backed implementation.
"""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int | None = None, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests or settings.rate_limit_per_minute
        self.window = window_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def _client_key(self, request: Request) -> str:
        # Prefer user id from state (set after auth), fall back to IP
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        forwarded = request.headers.get("X-Forwarded-For")
        ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
        return f"ip:{ip}"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        key = self._client_key(request)
        now = time.time()
        cutoff = now - self.window

        timestamps = self._buckets[key]
        self._buckets[key] = [t for t in timestamps if t > cutoff]

        if len(self._buckets[key]) >= self.max_requests:
            retry_after = int(self.window - (now - self._buckets[key][0])) + 1
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "code": "RATE_LIMITED", "retry_after": retry_after},
                headers={"Retry-After": str(retry_after)},
            )

        self._buckets[key].append(now)
        return await call_next(request)
