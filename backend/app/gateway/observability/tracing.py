"""Distributed tracing for DeerFlow Gateway.

Provides lightweight distributed tracing with context propagation.
Supports trace and span IDs for request correlation across services.
"""

import time
import uuid
from contextvars import ContextVar
from typing import Any

from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .structured_logging import structured_logger

# Context variables for trace propagation
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
span_id_var: ContextVar[str] = ContextVar("span_id", default="")
parent_span_id_var: ContextVar[str] = ContextVar("parent_span_id", default="")


class Span(BaseModel):
    """A single trace span."""

    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: str | None = None
    trace_id: str = ""
    name: str
    start_time: float = Field(default_factory=time.time)
    end_time: float | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    events: list[dict[str, Any]] = Field(default_factory=list)

    def duration(self) -> float:
        """Get span duration in milliseconds."""
        if self.end_time is None:
            return 0
        return (self.end_time - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary for logging."""
        return {
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "trace_id": self.trace_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration(),
            "attributes": self.attributes,
            "events": self.events,
        }


class Trace:
    """A complete trace containing multiple spans."""

    def __init__(self, trace_id: str | None = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.spans: list[Span] = []
        self.start_time = time.time()
        self.end_time: float | None = None

    def create_span(self, name: str, parent_span_id: str | None = None, attributes: dict[str, Any] | None = None) -> Span:
        """Create a new span within this trace."""
        span = Span(
            trace_id=self.trace_id,
            parent_span_id=parent_span_id,
            name=name,
            attributes=attributes or {},
        )
        self.spans.append(span)
        return span

    def end_span(self, span: Span):
        """End a span."""
        span.end_time = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert trace to dictionary."""
        return {
            "trace_id": self.trace_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": (self.end_time or time.time() - self.start_time) * 1000,
            "spans": [span.to_dict() for span in self.spans],
        }


class Tracer:
    """Distributed tracer."""

    def __init__(self):
        self._current_trace: Trace | None = None
        self._span_stack: list[Span] = []

    def start_trace(self, name: str, attributes: dict[str, Any] | None = None) -> Trace:
        """Start a new trace."""
        self._current_trace = Trace()
        span = self._current_trace.create_span(name, attributes=attributes)
        self._span_stack.append(span)

        # Set context variables
        trace_id_var.set(self._current_trace.trace_id)
        span_id_var.set(span.span_id)

        return self._current_trace

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Span:
        """Start a new child span."""
        if self._current_trace is None:
            self.start_trace(name, attributes)
            return self._span_stack[-1]

        parent_span = self._span_stack[-1] if self._span_stack else None
        span = self._current_trace.create_span(
            name,
            parent_span_id=parent_span.span_id if parent_span else None,
            attributes=attributes,
        )
        self._span_stack.append(span)

        # Update context variables
        span_id_var.set(span.span_id)
        if parent_span:
            parent_span_id_var.set(parent_span.span_id)

        return span

    def end_span(self, span: Span | None = None):
        """End the current or specified span."""
        if span is None:
            if not self._span_stack:
                return
            span = self._span_stack.pop()

        if self._current_trace:
            self._current_trace.end_span(span)

        # Update context variables
        if self._span_stack:
            span_id_var.set(self._span_stack[-1].span_id)
            parent_span_id_var.set(self._span_stack[-2].span_id if len(self._span_stack) > 1 else "")
        else:
            span_id_var.set("")
            parent_span_id_var.set("")

    def get_current_trace(self) -> Trace | None:
        """Get current trace."""
        return self._current_trace

    def inject_context(self, headers: dict[str, str]) -> dict[str, str]:
        """Inject trace context into headers for propagation."""
        if self._current_trace is None:
            return headers

        current_span = self._span_stack[-1] if self._span_stack else None

        headers["X-Trace-ID"] = self._current_trace.trace_id
        if current_span:
            headers["X-Span-ID"] = current_span.span_id
            if current_span.parent_span_id:
                headers["X-Parent-Span-ID"] = current_span.parent_span_id

        return headers

    def extract_context(self, headers: dict[str, str]) -> Trace | None:
        """Extract trace context from headers."""
        trace_id = headers.get("X-Trace-ID") or headers.get("X-B3-TraceId")
        if not trace_id:
            return None

        trace = Trace(trace_id)
        self._current_trace = trace

        # Set context variables
        trace_id_var.set(trace_id)

        span_id = headers.get("X-Span-ID") or headers.get("X-B3-SpanId")
        if span_id:
            span_id_var.set(span_id)

        parent_span_id = headers.get("X-Parent-Span-ID") or headers.get("X-B3-ParentSpanId")
        if parent_span_id:
            parent_span_id_var.set(parent_span_id)

        return trace


# Global tracer instance
tracer = Tracer()


class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically trace HTTP requests."""

    def __init__(self, app, service_name: str = "deerflow-gateway"):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        """Trace incoming HTTP request."""
        # Extract trace context from headers
        tracer.extract_context(dict(request.headers))

        # Start root span for this request
        span = tracer.start_span(
            f"HTTP {request.method} {request.url.path}",
            attributes={
                "http.method": request.method,
                "http.url": str(request.url),
                "http.user_agent": request.headers.get("user-agent", ""),
                "service.name": self.service_name,
            },
        )

        # Add request ID from headers if present
        request_id = request.headers.get("X-Request-ID", "")
        if request_id:
            span.attributes["request_id"] = request_id

        try:
            response = await call_next(request)
            span.attributes["http.status_code"] = response.status_code

            # Inject trace headers into response
            tracer.inject_context(response.headers)

            return response

        except Exception as e:
            span.attributes["error"] = True
            span.attributes["error.message"] = str(e)
            span.attributes["error.type"] = type(e).__name__
            raise

        finally:
            tracer.end_span(span)

            # Log trace completion
            if tracer.get_current_trace():
                structured_logger.info(
                    "Trace completed",
                    extra={
                        "trace_id": tracer.get_current_trace().trace_id,
                        "duration_ms": span.duration(),
                        "span_name": span.name,
                    },
                )


def get_tracer() -> Tracer:
    """Get global tracer instance."""
    return tracer


def trace_span(name: str, attributes: dict[str, Any] | None = None):
    """Decorator to create a trace span for a function."""

    def decorator(func):
        import functools

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            span = tracer.start_span(name, attributes)
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                span.attributes["error"] = True
                span.attributes["error.message"] = str(e)
                raise
            finally:
                tracer.end_span(span)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            span = tracer.start_span(name, attributes)
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                span.attributes["error"] = True
                span.attributes["error.message"] = str(e)
                raise
            finally:
                tracer.end_span(span)

        # Determine if function is async
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
