"""Security configuration for DeerFlow Gateway.

Centralized security configuration that can be overridden via environment variables.
"""

import os
from dataclasses import dataclass


@dataclass
class SecurityConfig:
    """Security configuration settings."""

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # requests per window
    rate_limit_window_seconds: int = 60
    rate_limit_exclude_paths: list[str] = None

    # CSRF Protection
    csrf_enabled: bool = True
    csrf_cookie_name: str = "csrf_token"
    csrf_header_name: str = "X-CSRF-Token"
    csrf_cookie_secure: bool = True
    csrf_cookie_httponly: bool = True
    csrf_cookie_samesite: str = "Strict"
    csrf_exempt_paths: list[str] = None

    # Security Headers
    security_headers_enabled: bool = True
    hsts_max_age: int = 31536000  # 1 year
    content_security_policy: str | None = None
    allow_frame: bool = False

    # Input Validation
    input_validation_enabled: bool = True
    max_request_body_size: int = 10 * 1024 * 1024  # 10MB
    max_string_length: int = 1000

    # Audit Logging
    audit_enabled: bool = True
    audit_log_request_body: bool = False
    audit_log_response_body: bool = False
    audit_exclude_paths: list[str] = None

    # SQL Injection Protection
    sql_injection_protection: bool = True

    # XSS Protection
    xss_protection: bool = True

    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.rate_limit_exclude_paths is None:
            self.rate_limit_exclude_paths = [
                "/health",
                "/metrics",
                "/docs",
                "/redoc",
                "/openapi.json",
            ]
        if self.csrf_exempt_paths is None:
            self.csrf_exempt_paths = [
                "/health",
                "/metrics",
                "/docs",
                "/redoc",
                "/openapi.json",
                "/api/tenants/current",  # Tenant endpoint needs special handling
                "/api/subscription/checkout-alipay",  # Alipay payment endpoint (no CSRF token from external client)
                "/api/subscription/webhook-alipay",  # Alipay webhook (external callback)
            ]
        if self.audit_exclude_paths is None:
            self.audit_exclude_paths = [
                "/health",
                "/metrics",
                "/favicon.ico",
            ]

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Load configuration from environment variables."""
        return cls(
            rate_limit_enabled=os.getenv("SECURITY_RATE_LIMIT_ENABLED", "true").lower() == "true",
            rate_limit_requests=int(os.getenv("SECURITY_RATE_LIMIT_REQUESTS", "100")),
            rate_limit_window_seconds=int(os.getenv("SECURITY_RATE_LIMIT_WINDOW", "60")),
            csrf_enabled=os.getenv("SECURITY_CSRF_ENABLED", "true").lower() == "true",
            security_headers_enabled=os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true",
            hsts_max_age=int(os.getenv("SECURITY_HSTS_MAX_AGE", "31536000")),
            input_validation_enabled=os.getenv("SECURITY_INPUT_VALIDATION_ENABLED", "true").lower() == "true",
            max_request_body_size=int(os.getenv("SECURITY_MAX_REQUEST_BODY_SIZE", "10485760")),
            audit_enabled=os.getenv("SECURITY_AUDIT_ENABLED", "true").lower() == "true",
        )


# Global security configuration
security_config = SecurityConfig.from_env()
