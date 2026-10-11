"""
Rate limiting middleware.
"""
import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        # Clean old entries
        self.requests = {
            ip: [t for t in times if now - t < 60]
            for ip, times in self.requests.items()
        }

        # Check limit
        client_requests = self.requests.get(client_ip, [])
        if len(client_requests) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        client_requests.append(now)
        self.requests[client_ip] = client_requests

        response = await call_next(request)
        return response
