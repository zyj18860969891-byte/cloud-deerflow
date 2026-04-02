"""Structured logging for DeerFlow Gateway.

Provides JSON-formatted structured logging with context enrichment.
Integrates with distributed tracing systems.
"""

import json
import logging
import sys
import traceback
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

# Context variables for request-scoped data
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)
tenant_id_var: ContextVar[str | None] = ContextVar("tenant_id", default=None)


class LogContext(BaseModel):
    """Context information for structured logs."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None
    tenant_id: str | None = None
    correlation_id: str | None = None
    span_id: str | None = None
    trace_id: str | None = None


class StructuredLogger:
    """Enhanced structured logger with context support."""

    def __init__(self, name: str = "deerflow"):
        self.logger = logging.getLogger(name)
        self._setup_structured_logging()

    def _setup_structured_logging(self):
        """Configure structured logging output."""
        if self.logger.handlers:
            return

        # Create handler that outputs JSON
        handler = logging.StreamHandler(sys.stdout)
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

    def _get_context(self) -> dict[str, Any]:
        """Get current logging context."""
        return {
            "request_id": request_id_var.get(),
            "user_id": user_id_var.get(),
            "tenant_id": tenant_id_var.get(),
        }

    def log(
        self,
        level: int,
        message: str,
        extra: dict[str, Any] | None = None,
        exc_info: bool | Exception = False,
    ) -> None:
        """Log a message with structured context."""
        context = self._get_context()
        log_data = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "level": logging.getLevelName(level),
            "message": message,
            "service": "deerflow-gateway",
            **context,
        }

        if extra:
            log_data.update(extra)

        if exc_info:
            if isinstance(exc_info, Exception):
                log_data["exception"] = {
                    "type": type(exc_info).__name__,
                    "message": str(exc_info),
                    "traceback": traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__),
                }
            else:
                log_data["exception"] = {
                    "traceback": traceback.format_exc(),
                }

        self.logger.log(level, json.dumps(log_data))

    def info(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self.log(logging.INFO, message, extra)

    def warning(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self.log(logging.WARNING, message, extra)

    def error(self, message: str, extra: dict[str, Any] | None = None, exc_info: bool | Exception = False) -> None:
        self.log(logging.ERROR, message, extra, exc_info)

    def debug(self, message: str, extra: dict[str, Any] | None = None) -> None:
        self.log(logging.DEBUG, message, extra)

    def critical(self, message: str, extra: dict[str, Any] | None = None, exc_info: bool | Exception = False) -> None:
        self.log(logging.CRITICAL, message, extra, exc_info)


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        # Build the base log entry
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "service": "deerflow-gateway",
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_entry[key] = value

        return json.dumps(log_entry, ensure_ascii=False, default=str)


# Global structured logger instance
structured_logger = StructuredLogger()


def get_logger(name: str = None) -> StructuredLogger:
    """Get a structured logger instance."""
    if name:
        return StructuredLogger(name)
    return structured_logger


# Context managers for request logging
class LogContextManager:
    """Context manager for request-scoped logging context."""

    def __init__(self, request_id: str, user_id: str | None = None, tenant_id: str | None = None):
        self.request_id = request_id
        self.user_id = user_id
        self.tenant_id = tenant_id
        self._tokens = []

    def __enter__(self):
        self._tokens = [
            request_id_var.set(self.request_id),
            user_id_var.set(self.user_id),
            tenant_id_var.set(self.tenant_id),
        ]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for token in self._tokens:
            request_id_var.reset(token)


def log_request(logger: StructuredLogger, request: Any, **kwargs):
    """Log an incoming request."""
    logger.info(
        "Request received",
        extra={
            "method": getattr(request, "method", "UNKNOWN"),
            "path": getattr(request, "url", {}).path if hasattr(request, "url") else "UNKNOWN",
            "query_params": dict(getattr(request, "query_params", {})),
            "client": getattr(request, "client", {}).host if hasattr(request, "client") else "unknown",
            "user_agent": getattr(request, "headers", {}).get("user-agent", ""),
            **kwargs,
        },
    )


def log_response(logger: StructuredLogger, response: Any, duration_ms: float, **kwargs):
    """Log an outgoing response."""
    logger.info("Response sent", extra={"status_code": getattr(response, "status_code", 0), "duration_ms": duration_ms, "content_length": getattr(response, "headers", {}).get("content-length", 0), **kwargs})


def log_error(logger: StructuredLogger, error: Exception, **kwargs):
    """Log an error with full context."""
    logger.error(f"Error occurred: {type(error).__name__}", extra={"error_type": type(error).__name__, "error_message": str(error), **kwargs}, exc_info=error)
