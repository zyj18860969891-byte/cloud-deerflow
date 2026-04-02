"""Grafana dashboard definitions for DeerFlow Gateway.

Provides pre-configured dashboard templates for:
- System performance
- API performance
- Business metrics
- Security metrics
"""

import json
from typing import Any


class GrafanaDashboardGenerator:
    """Generate Grafana dashboard JSON configurations."""

    @staticmethod
    def system_dashboard() -> dict[str, Any]:
        """Generate system performance dashboard."""
        return {
            "dashboard": {
                "title": "DeerFlow System Performance",
                "tags": ["deerflow", "system"],
                "timezone": "browser",
                "schemaVersion": 36,
                "version": 1,
                "refresh": "10s",
                "time": {"from": "now-1h", "to": "now"},
                "panels": [
                    {
                        "id": 1,
                        "title": "CPU Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "deerflow_system_cpu_usage_percent",
                                "legendFormat": "CPU %",
                                "refId": "A",
                            }
                        ],
                        "yAxes": [
                            {"format": "percent", "min": 0, "max": 100},
                            {"format": "short"},
                        ],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                    },
                    {
                        "id": 2,
                        "title": "Memory Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "deerflow_system_memory_usage_bytes",
                                "legendFormat": "Memory bytes",
                                "refId": "A",
                            }
                        ],
                        "yAxes": [
                            {"format": "bytes"},
                            {"format": "short"},
                        ],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
                    },
                    {
                        "id": 3,
                        "title": "Disk Usage",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "deerflow_system_disk_usage_percent",
                                "legendFormat": "Disk %",
                                "refId": "A",
                            }
                        ],
                        "options": {
                            "colorMode": "background",
                            "graphMode": "area",
                            "justifyMode": "auto",
                            "orientation": "auto",
                            "reduceOptions": {
                                "values": False,
                                "calcs": ["lastNotNull"],
                                "fields": "",
                            },
                            "textMode": "auto",
                            "text": {"value": "Disk Usage", "color": "auto"},
                        },
                        "gridPos": {"x": 0, "y": 8, "w": 6, "h": 4},
                    },
                    {
                        "id": 4,
                        "title": "Active Connections",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "deerflow_database_connections_active",
                                "legendFormat": "Connections",
                                "refId": "A",
                            }
                        ],
                        "gridPos": {"x": 6, "y": 8, "w": 6, "h": 4},
                    },
                ],
            }
        }

    @staticmethod
    def api_performance_dashboard() -> dict[str, Any]:
        """Generate API performance dashboard."""
        return {
            "dashboard": {
                "title": "DeerFlow API Performance",
                "tags": ["deerflow", "api"],
                "timezone": "browser",
                "schemaVersion": 36,
                "version": 1,
                "refresh": "10s",
                "time": {"from": "now-1h", "to": "now"},
                "panels": [
                    {
                        "id": 1,
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(deerflow_http_requests_total[5m])",
                                "legendFormat": "{{method}} {{endpoint}}",
                                "refId": "A",
                            }
                        ],
                        "yAxes": [{"format": "short"}, {"format": "short"}],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                    },
                    {
                        "id": 2,
                        "title": "Response Time (p50, p95, p99)",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.50, sum(rate(deerflow_http_request_duration_seconds_bucket[5m])) by (le, method, endpoint))",
                                "legendFormat": "p50 {{method}} {{endpoint}}",
                                "refId": "A",
                            },
                            {
                                "expr": "histogram_quantile(0.95, sum(rate(deerflow_http_request_duration_seconds_bucket[5m])) by (le, method, endpoint))",
                                "legendFormat": "p95 {{method}} {{endpoint}}",
                                "refId": "B",
                            },
                            {
                                "expr": "histogram_quantile(0.99, sum(rate(deerflow_http_request_duration_seconds_bucket[5m])) by (le, method, endpoint))",
                                "legendFormat": "p99 {{method}} {{endpoint}}",
                                "refId": "C",
                            },
                        ],
                        "yAxes": [{"format": "s"}, {"format": "short"}],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
                    },
                    {
                        "id": 3,
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": 'rate(deerflow_http_requests_total{status_code=~"5.."}[5m])',
                                "legendFormat": "{{method}} {{endpoint}}",
                                "refId": "A",
                            }
                        ],
                        "yAxes": [{"format": "short"}, {"format": "short"}],
                        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
                    },
                    {
                        "id": 4,
                        "title": "In-Flight Requests",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "deerflow_http_requests_in_flight",
                                "legendFormat": "{{endpoint}}",
                                "refId": "A",
                            }
                        ],
                        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
                    },
                ],
            }
        }

    @staticmethod
    def business_metrics_dashboard() -> dict[str, Any]:
        """Generate business metrics dashboard."""
        return {
            "dashboard": {
                "title": "DeerFlow Business Metrics",
                "tags": ["deerflow", "business"],
                "timezone": "browser",
                "schemaVersion": 36,
                "version": 1,
                "refresh": "30s",
                "time": {"from": "now-24h", "to": "now"},
                "panels": [
                    {
                        "id": 1,
                        "title": "Tool Executions",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(deerflow_tool_executions_total[5m])",
                                "legendFormat": "{{tool_name}} ({{status}})",
                                "refId": "A",
                            }
                        ],
                        "yAxes": [{"format": "short"}, {"format": "short"}],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                    },
                    {
                        "id": 2,
                        "title": "Cache Hit Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(deerflow_cache_hits_total[5m]) / (rate(deerflow_cache_hits_total[5m]) + rate(deerflow_cache_misses_total[5m]))",
                                "legendFormat": "{{cache_type}}",
                                "refId": "A",
                            }
                        ],
                        "yAxes": [{"format": "percentunit", "min": 0, "max": 1}, {"format": "short"}],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
                    },
                    {
                        "id": 3,
                        "title": "Active Tenants",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "deerflow_tenants_active",
                                "legendFormat": "Active Tenants",
                                "refId": "A",
                            }
                        ],
                        "gridPos": {"x": 0, "y": 8, "w": 6, "h": 4},
                    },
                    {
                        "id": 4,
                        "title": "Total Tools",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(deerflow_tools_total)",
                                "legendFormat": "Total Tools",
                                "refId": "A",
                            }
                        ],
                        "gridPos": {"x": 6, "y": 8, "w": 6, "h": 4},
                    },
                ],
            }
        }

    @staticmethod
    def security_dashboard() -> dict[str, Any]:
        """Generate security metrics dashboard."""
        return {
            "dashboard": {
                "title": "DeerFlow Security Metrics",
                "tags": ["deerflow", "security"],
                "timezone": "browser",
                "schemaVersion": 36,
                "version": 1,
                "refresh": "30s",
                "time": {"from": "now-24h", "to": "now"},
                "panels": [
                    {
                        "id": 1,
                        "title": "Rate Limit Hits",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(deerflow_rate_limit_hits_total[5m])",
                                "legendFormat": "{{endpoint}}",
                                "refId": "A",
                            }
                        ],
                        "yAxes": [{"format": "short"}, {"format": "short"}],
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                    },
                    {
                        "id": 2,
                        "title": "Error Rate by Type",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(deerflow_errors_total[5m])",
                                "legendFormat": "{{error_type}}",
                                "refId": "A",
                            }
                        ],
                        "yAxes": [{"format": "short"}, {"format": "short"}],
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
                    },
                    {
                        "id": 3,
                        "title": "CSRF Failures",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": 'deerflow_errors_total{error_type="CSRFError"}',
                                "legendFormat": "CSRF Failures",
                                "refId": "A",
                            }
                        ],
                        "gridPos": {"x": 0, "y": 8, "w": 6, "h": 4},
                    },
                    {
                        "id": 4,
                        "title": "Authentication Failures",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": 'deerflow_errors_total{error_type="AuthenticationError"}',
                                "legendFormat": "Auth Failures",
                                "refId": "A",
                            }
                        ],
                        "gridPos": {"x": 6, "y": 8, "w": 6, "h": 4},
                    },
                ],
            }
        }

    @staticmethod
    def get_all_dashboards() -> dict[str, dict[str, Any]]:
        """Get all dashboard definitions."""
        return {
            "system": GrafanaDashboardGenerator.system_dashboard(),
            "api_performance": GrafanaDashboardGenerator.api_performance_dashboard(),
            "business_metrics": GrafanaDashboardGenerator.business_metrics_dashboard(),
            "security": GrafanaDashboardGenerator.security_dashboard(),
        }

    @staticmethod
    def export_dashboards(directory: str):
        """Export all dashboards to JSON files."""
        import os

        dashboards = GrafanaDashboardGenerator.get_all_dashboards()
        os.makedirs(directory, exist_ok=True)

        for name, dashboard in dashboards.items():
            filepath = os.path.join(directory, f"deerflow-{name}-dashboard.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dashboard, f, indent=2, ensure_ascii=False)

        print(f"Exported {len(dashboards)} dashboards to {directory}")
