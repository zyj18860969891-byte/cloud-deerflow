"""Prometheus metrics for DeerFlow Gateway.

Provides comprehensive metrics collection for:
- HTTP requests (latency, count, errors)
- System resources (CPU, memory, disk)
- Business metrics (tools, tenants, cache)
- Custom application metrics
"""

import asyncio
import time
from contextvars import ContextVar

import psutil
from prometheus_client import (
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    start_http_server,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Request-scoped context for metrics
request_start_time: ContextVar[float] = ContextVar("request_start_time", default=0.0)


class GatewayMetrics:
    """Centralized metrics collector for DeerFlow Gateway."""

    def __init__(self, metrics_port: int = 9090):
        """Initialize metrics collector.

        Args:
            metrics_port: Port to expose Prometheus metrics endpoint
        """
        self.metrics_port = metrics_port
        self._setup_metrics()
        self._server_started = False

    def _setup_metrics(self):
        """Initialize all Prometheus metrics."""

        # HTTP Request Metrics
        self.http_requests_total = Counter(
            "deerflow_http_requests_total",
            "Total number of HTTP requests",
            ["method", "endpoint", "status_code", "tenant_id"],
        )

        self.http_request_duration_seconds = Histogram(
            "deerflow_http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint", "status_code"],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
        )

        self.http_requests_in_flight = Gauge(
            "deerflow_http_requests_in_flight",
            "Current number of HTTP requests in flight",
            ["endpoint"],
        )

        # System Metrics
        self.system_cpu_usage = Gauge(
            "deerflow_system_cpu_usage_percent",
            "System CPU usage percentage",
        )

        self.system_memory_usage = Gauge(
            "deerflow_system_memory_usage_bytes",
            "System memory usage in bytes",
        )

        self.system_disk_usage = Gauge(
            "deerflow_system_disk_usage_percent",
            "System disk usage percentage",
        )

        # Business Metrics
        self.tools_total = Gauge(
            "deerflow_tools_total",
            "Total number of tools",
            ["tool_type", "tenant_id"],
        )

        self.tool_executions_total = Counter(
            "deerflow_tool_executions_total",
            "Total number of tool executions",
            ["tool_id", "tool_name", "tenant_id", "status"],
        )

        self.tenants_active = Gauge(
            "deerflow_tenants_active",
            "Number of active tenants",
        )

        self.cache_hits_total = Counter(
            "deerflow_cache_hits_total",
            "Total number of cache hits",
            ["cache_type", "tenant_id"],
        )

        self.cache_misses_total = Counter(
            "deerflow_cache_misses_total",
            "Total number of cache misses",
            ["cache_type", "tenant_id"],
        )

        # Database Metrics
        self.database_connections_active = Gauge(
            "deerflow_database_connections_active",
            "Number of active database connections",
        )

        self.database_queries_total = Counter(
            "deerflow_database_queries_total",
            "Total number of database queries",
            ["operation", "table", "status"],
        )

        # Error Metrics
        self.errors_total = Counter(
            "deerflow_errors_total",
            "Total number of errors",
            ["error_type", "endpoint", "tenant_id"],
        )

        # Rate Limit Metrics
        self.rate_limit_hits_total = Counter(
            "deerflow_rate_limit_hits_total",
            "Total number of rate limit hits",
            ["endpoint", "tenant_id"],
        )

        # Custom Application Metrics
        self.custom_metric_counter = Counter(
            "deerflow_custom_counter",
            "Custom counter metric",
            ["metric_name", "labels"],
        )

        self.custom_metric_gauge = Gauge(
            "deerflow_custom_gauge",
            "Custom gauge metric",
            ["metric_name", "labels"],
        )

    async def start_server(self):
        """Start Prometheus metrics HTTP server."""
        if not self._server_started:
            try:
                # Start Prometheus HTTP server in background
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: start_http_server(self.metrics_port, registry=REGISTRY))
                self._server_started = True
                print(f"Prometheus metrics server started on port {self.metrics_port}")
            except OSError as e:
                print(f"Failed to start metrics server: {e}")

    def update_system_metrics(self):
        """Update system resource metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.system_cpu_usage.set(cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        self.system_memory_usage.set(memory.used)

        # Disk usage
        disk = psutil.disk_usage("/")
        self.disk_usage_percent = disk.percent
        self.system_disk_usage.set(disk.percent)

    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        tenant_id: str | None = None,
    ):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            tenant_id=tenant_id or "unknown",
        ).inc()

        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
        ).observe(duration)

    def record_tool_execution(
        self,
        tool_id: str,
        tool_name: str,
        tenant_id: str | None,
        status: str,
    ):
        """Record tool execution."""
        self.tool_executions_total.labels(
            tool_id=tool_id,
            tool_name=tool_name,
            tenant_id=tenant_id or "unknown",
            status=status,
        ).inc()

    def record_cache_hit(self, cache_type: str, tenant_id: str | None):
        """Record cache hit."""
        self.cache_hits_total.labels(
            cache_type=cache_type,
            tenant_id=tenant_id or "unknown",
        ).inc()

    def record_cache_miss(self, cache_type: str, tenant_id: str | None):
        """Record cache miss."""
        self.cache_misses_total.labels(
            cache_type=cache_type,
            tenant_id=tenant_id or "unknown",
        ).inc()

    def record_error(
        self,
        error_type: str,
        endpoint: str,
        tenant_id: str | None = None,
    ):
        """Record application error."""
        self.errors_total.labels(
            error_type=error_type,
            endpoint=endpoint,
            tenant_id=tenant_id or "unknown",
        ).inc()

    def record_rate_limit_hit(self, endpoint: str, tenant_id: str | None):
        """Record rate limit hit."""
        self.rate_limit_hits_total.labels(
            endpoint=endpoint,
            tenant_id=tenant_id or "unknown",
        ).inc()

    def update_business_metrics(
        self,
        tools_count: dict[str, int] | None = None,
        active_tenants: int | None = None,
        db_connections: int | None = None,
    ):
        """Update business-related metrics."""
        if tools_count:
            for tool_type, count in tools_count.items():
                self.tools_total.labels(
                    tool_type=tool_type,
                    tenant_id="all",
                ).set(count)

        if active_tenants is not None:
            self.tenants_active.set(active_tenants)

        if db_connections is not None:
            self.database_connections_active.set(db_connections)

    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format."""
        return generate_latest(REGISTRY).decode("utf-8")


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically collect HTTP metrics."""

    def __init__(self, app, metrics: GatewayMetrics):
        super().__init__(app)
        self.metrics = metrics

    async def dispatch(self, request: Request, call_next):
        """Collect metrics for each HTTP request."""
        # Get tenant ID from request state
        tenant_id = getattr(request.state, "tenant_id", None)

        # Record in-flight requests
        endpoint = request.url.path
        self.metrics.http_requests_in_flight.labels(endpoint=endpoint).inc()

        # Start timing
        start_time = time.time()
        request_start_time.set(start_time)

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Record metrics
            self.metrics.record_http_request(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration,
                tenant_id=tenant_id,
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_error(
                error_type=type(e).__name__,
                endpoint=endpoint,
                tenant_id=tenant_id,
            )
            raise

        finally:
            # Decrement in-flight requests
            self.metrics.http_requests_in_flight.labels(endpoint=endpoint).dec()


# Global metrics instance
gateway_metrics: GatewayMetrics | None = None


def get_metrics() -> GatewayMetrics:
    """Get or create global metrics instance."""
    global gateway_metrics
    if gateway_metrics is None:
        gateway_metrics = GatewayMetrics()
    return gateway_metrics


async def start_metrics_server(port: int = 9090):
    """Start Prometheus metrics server."""
    metrics = get_metrics()
    await metrics.start_server()
