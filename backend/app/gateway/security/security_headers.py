"""Security headers middleware for DeerFlow Gateway.

Adds security-related HTTP headers to protect against common attacks:
- XSS protection
- Content Security Policy (CSP)
- HSTS (HTTPS enforcement)
- Frame options (clickjacking protection)
- Content type options
- Referrer policy
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""

    def __init__(
        self,
        app,
        csp_policy: str | None = None,
        hsts_max_age: int = 31536000,  # 1 year
        allow_frame: bool = False,
    ):
        super().__init__(app)
        self.csp_policy = csp_policy or self._default_csp()
        self.hsts_max_age = hsts_max_age
        self.allow_frame = allow_frame

    def _default_csp(self) -> str:
        """Default Content Security Policy."""
        return "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'self';"

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)

        # X-Content-Type-Options: Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        if self.allow_frame:
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
        else:
            response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Enable XSS filter in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content-Security-Policy
        response.headers["Content-Security-Policy"] = self.csp_policy

        # Strict-Transport-Security (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = f"max-age={self.hsts_max_age}; includeSubDomains; preload"

        # Permissions-Policy: Restrict browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=(), ambient-light-sensor=()"

        return response
