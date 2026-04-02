"""Rate limiting middleware for DeerFlow Gateway.

Provides configurable rate limiting using sliding window algorithm.
Supports both global and per-endpoint rate limits.
"""

import asyncio
import hashlib
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """Sliding window rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store request timestamps: {key: [(timestamp, count), ...]}
        self.requests: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    def _get_client_key(self, request: Request) -> str:
        """Generate a unique key for the client."""
        # Use IP address and optionally user agent
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")[:50]
        key_data = f"{client_ip}:{user_agent}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed based on rate limit."""
        async with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Clean old entries
            if key in self.requests:
                self.requests[key] = [(ts, count) for ts, count in self.requests[key] if ts > window_start]

            # Count requests in current window
            total_requests = sum(count for _, count in self.requests[key])

            if total_requests >= self.max_requests:
                return False

            # Record this request
            self.requests[key].append((now, 1))
            return True

    async def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window."""
        async with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            if key not in self.requests:
                return self.max_requests

            # Clean old entries
            self.requests[key] = [(ts, count) for ts, count in self.requests[key] if ts > window_start]

            total_requests = sum(count for _, count in self.requests[key])
            return max(0, self.max_requests - total_requests)

    async def get_reset_time(self, key: str) -> float:
        """Get seconds until rate limit resets."""
        async with self._lock:
            if key not in self.requests or not self.requests[key]:
                return 0

            oldest_timestamp = min(ts for ts, _ in self.requests[key])
            reset_time = oldest_timestamp + self.window_seconds - time.time()
            return max(0, reset_time)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting."""

    def __init__(
        self,
        app,
        max_requests: int = 100,
        window_seconds: int = 60,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.limiter = RateLimiter(max_requests, window_seconds)
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        key = self.limiter._get_client_key(request)

        if not await self.limiter.is_allowed(key):
            reset_time = await self.limiter.get_reset_time(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(self.limiter.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time)),
                    "Retry-After": str(int(reset_time)),
                },
            )

        remaining = await self.limiter.get_remaining(key)
        reset_time = await self.limiter.get_reset_time(key)

        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(self.limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))

        return response
