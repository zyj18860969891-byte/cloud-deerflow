"""CSRF protection middleware for DeerFlow Gateway.

Provides CSRF token generation and validation for state-changing operations.
Uses double-submit cookie pattern for stateless CSRF protection.
"""

import secrets

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware for CSRF protection using double-submit cookie pattern."""

    def __init__(
        self,
        app,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: str = "Strict",
        exempt_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite
        self.exempt_paths = exempt_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request with CSRF protection."""
        # Skip CSRF check for exempt paths and safe methods (GET, HEAD, OPTIONS)
        if any(request.url.path.startswith(path) for path in self.exempt_paths) or request.method.upper() in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)

        # Check CSRF token for state-changing requests
        cookie_token = request.cookies.get(self.cookie_name)
        header_token = request.headers.get(self.header_name)

        if not cookie_token or not header_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing",
            )

        if cookie_token != header_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token invalid",
            )

        response = await call_next(request)
        return response


def generate_csrf_token() -> str:
    """Generate a secure CSRF token."""
    return secrets.token_urlsafe(32)


def validate_csrf_token(cookie_token: str, request_token: str) -> bool:
    """Validate CSRF token using constant-time comparison."""
    return secrets.compare_digest(cookie_token, request_token)


async def get_csrf_token_dependency(
    request: Request,
    response: Response,
    cookie_name: str = "csrf_token",
) -> str:
    """Dependency to generate and set CSRF token."""
    token = request.cookies.get(cookie_name)
    if not token:
        token = generate_csrf_token()
        response.set_cookie(
            key=cookie_name,
            value=token,
            httponly=True,
            secure=request.url.scheme == "https",
            samesite="Strict",
            max_age=86400,  # 24 hours
        )
    return token
