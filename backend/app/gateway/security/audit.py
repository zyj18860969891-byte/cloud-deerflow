"""Audit logging for DeerFlow Gateway.

Provides comprehensive audit logging for security-relevant events.
Tracks user actions, authentication events, administrative changes, etc.
"""

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import Request
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware


class AuditEvent(BaseModel):
    """Audit event model."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    event_type: str
    user_id: str | None = None
    tenant_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    endpoint: str
    method: str
    status_code: int | None = None
    request_body: dict[str, Any] | None = None
    response_body: dict[str, Any] | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogger:
    """Audit logger with configurable handlers."""

    def __init__(self, logger_name: str = "audit"):
        self.logger = logging.getLogger(logger_name)
        self._setup_audit_logger()

    def _setup_audit_logger(self):
        """Configure audit logger."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "audit": %(message)s}',
                datefmt="%Y-%m-%dT%H:%M:%S.%fZ",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            self.logger.propagate = False

    def log_event(self, event: AuditEvent):
        """Log an audit event."""
        self.logger.info(event.json())

    def log_auth_event(
        self,
        event_type: str,
        user_id: str | None,
        success: bool,
        request: Request,
        details: dict[str, Any] | None = None,
    ):
        """Log authentication/authorization event."""
        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", ""),
            endpoint=str(request.url),
            method=request.method,
            metadata={"success": success, **(details or {})},
        )
        self.log_event(event)

    def log_admin_action(
        self,
        action: str,
        user_id: str,
        tenant_id: str | None,
        request: Request,
        target_resource: str | None = None,
        changes: dict[str, Any] | None = None,
    ):
        """Log administrative action."""
        event = AuditEvent(
            event_type="admin_action",
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", ""),
            endpoint=str(request.url),
            method=request.method,
            metadata={
                "action": action,
                "target_resource": target_resource,
                "changes": changes or {},
            },
        )
        self.log_event(event)

    def log_data_access(
        self,
        resource_type: str,
        resource_id: str,
        user_id: str,
        tenant_id: str | None,
        request: Request,
        action: str = "read",
    ):
        """Log data access event."""
        event = AuditEvent(
            event_type="data_access",
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", ""),
            endpoint=str(request.url),
            method=request.method,
            metadata={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
            },
        )
        self.log_event(event)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log all requests for audit purposes."""

    def __init__(
        self,
        app,
        audit_logger: AuditLogger | None = None,
        exclude_paths: list[str] | None = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        super().__init__(app)
        self.audit_logger = audit_logger or AuditLogger()
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/favicon.ico",
        ]
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next):
        """Log request and response for audit trail."""
        # Skip audit logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Extract user context
        user_id = getattr(request.state, "user_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)

        # Read request body if needed
        request_body = None
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_body = json.loads(body)
            except Exception:
                request_body = {"error": "Could not parse request body"}

        # Create audit event for request
        event = AuditEvent(
            event_type="api_request",
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", ""),
            endpoint=str(request.url),
            method=request.method,
            request_body=request_body,
        )

        try:
            response = await call_next(request)
            event.status_code = response.status_code

            # Read response body if needed
            if self.log_response_body and response.status_code >= 400:
                try:
                    # Note: This consumes the response body stream
                    # In production, you'd need to handle this more carefully
                    pass
                except Exception:
                    pass

            self.audit_logger.log_event(event)
            return response

        except Exception as e:
            event.error_message = str(e)
            event.status_code = 500
            self.audit_logger.log_event(event)
            raise
