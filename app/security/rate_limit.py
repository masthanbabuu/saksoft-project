"""Limit HTTP requests per client."""

import math
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int, window: int) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.clients: dict[str, tuple[float, int]] = {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path.startswith("/health/"):
            return await call_next(request)

        now = time.monotonic()
        client = request.client.host if request.client else "unknown"

        self.clients = {key: value for key, value in self.clients.items() if value[0] > now}

        if client not in self.clients and len(self.clients) >= 10000:
            return JSONResponse(
                {"detail": "Server busy"},
                status_code=503,
            )

        expires, count = self.clients.get(client, (now + self.window, 0))

        if count >= self.limit:
            return JSONResponse(
                {"detail": "Too many requests"},
                status_code=429,
                headers={"Retry-After": str(max(1, math.ceil(expires - now)))},
            )

        self.clients[client] = (expires, count + 1)
        return await call_next(request)
