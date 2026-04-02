"""Observability package for DeerFlow Gateway.

Provides comprehensive observability features:
- Structured logging (JSON format)
- Prometheus metrics collection
- Distributed tracing
- Grafana dashboard templates
"""

from .metrics import (
    GatewayMetrics,
    MetricsMiddleware,
    get_metrics,
    start_metrics_server,
)
from .structured_logging import (
    LogContextManager,
    StructuredLogger,
    get_logger,
    log_error,
    log_request,
    log_response,
    structured_logger,
)
from .tracing import (
    Span,
    Trace,
    Tracer,
    TracingMiddleware,
    get_tracer,
    trace_span,
)

__all__ = [
    # Structured Logging
    "StructuredLogger",
    "get_logger",
    "LogContextManager",
    "log_request",
    "log_response",
    "log_error",
    "structured_logger",
    # Metrics
    "GatewayMetrics",
    "MetricsMiddleware",
    "get_metrics",
    "start_metrics_server",
    # Tracing
    "Tracer",
    "Trace",
    "Span",
    "TracingMiddleware",
    "get_tracer",
    "trace_span",
]
