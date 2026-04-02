"""Dashboard API routes for DeerFlow Gateway.

Provides administrative and user dashboard data.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from deerflow.services.database import get_database_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class AdminDashboardResponse(BaseModel):
    """Admin dashboard data response."""

    total_users: int
    active_users: int
    api_calls_today: int
    error_rate: float
    system_health: float
    cache_hit_rate: float
    total_cost: float
    avg_response_time: int
    system_metrics: list[dict[str, Any]]
    recent_errors: list[dict[str, Any]]
    top_users: list[dict[str, Any]]


class UserDashboardResponse(BaseModel):
    """User dashboard data response."""

    tool_executions: int
    cache_hit_rate: float
    storage_used: float
    storage_quota: float
    api_quota: int
    api_used: int
    avg_response_time: int
    success_rate: float
    api_usage: list[dict[str, Any]]
    top_tools: list[dict[str, Any]]
    recent_activity: list[dict[str, Any]]


@router.get("/admin", response_model=AdminDashboardResponse)
async def get_admin_dashboard(request: Request):
    """
    Get admin dashboard data.

    Requires admin permissions.
    """
    # Check permissions (implement based on your auth system)
    user_id = getattr(request.state, "user_id", None)
    tenant_id = getattr(request.state, "tenant_id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        db = await get_database_service()

        # Get total and active users
        total_users = await db.fetch_val("SELECT COUNT(*) FROM users")
        active_users = await db.fetch_val(
            "SELECT COUNT(*) FROM users WHERE last_seen > :cutoff",
            {"cutoff": datetime.now(UTC) - timedelta(days=7)},
        )

        # Get API calls today
        today = datetime.now(UTC).date()
        api_calls_today = await db.fetch_val(
            "SELECT COUNT(*) FROM api_logs WHERE DATE(created_at) = :today",
            {"today": today},
        )

        # Calculate error rate (5xx responses in last 24h)
        error_count = await db.fetch_val(
            "SELECT COUNT(*) FROM api_logs WHERE status_code >= 500 AND created_at > :cutoff",
            {"cutoff": datetime.now(UTC) - timedelta(hours=24)},
        )
        total_requests = await db.fetch_val(
            "SELECT COUNT(*) FROM api_logs WHERE created_at > :cutoff",
            {"cutoff": datetime.now(UTC) - timedelta(hours=24)},
        )
        error_rate = error_count / total_requests if total_requests > 0 else 0

        # Get cache hit rate
        cache_hits = (
            await db.fetch_val(
                "SELECT SUM(hits) FROM cache_metrics WHERE created_at > :cutoff",
                {"cutoff": datetime.now(UTC) - timedelta(hours=24)},
            )
            or 0
        )
        cache_misses = (
            await db.fetch_val(
                "SELECT SUM(misses) FROM cache_metrics WHERE created_at > :cutoff",
                {"cutoff": datetime.now(UTC) - timedelta(hours=24)},
            )
            or 0
        )
        total_cache = cache_hits + cache_misses
        cache_hit_rate = cache_hits / total_cache if total_cache > 0 else 0

        # Get system health (average response time)
        avg_response_time = (
            await db.fetch_val(
                "SELECT AVG(duration_ms) FROM api_logs WHERE created_at > :cutoff",
                {"cutoff": datetime.now(UTC) - timedelta(hours=24)},
            )
            or 0
        )

        # Get total cost (estimate based on usage)
        total_cost = (
            await db.fetch_val(
                "SELECT SUM(cost) FROM usage_records WHERE created_at >= :start_date",
                {"start_date": datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)},
            )
            or 0
        )

        # System metrics
        system_metrics = [
            {
                "name": "CPU Usage",
                "value": await db.fetch_val("SELECT value FROM system_metrics WHERE metric = 'cpu' ORDER BY created_at DESC LIMIT 1") or 0,
                "status": "healthy",
            },
            {
                "name": "Memory Usage",
                "value": await db.fetch_val("SELECT value FROM system_metrics WHERE metric = 'memory' ORDER BY created_at DESC LIMIT 1") or 0,
                "status": "healthy",
            },
            {
                "name": "Disk Usage",
                "value": await db.fetch_val("SELECT value FROM system_metrics WHERE metric = 'disk' ORDER BY created_at DESC LIMIT 1") or 0,
                "status": "warning" if (await db.fetch_val("SELECT value FROM system_metrics WHERE metric = 'disk' ORDER BY created_at DESC LIMIT 1") or 0) > 80 else "healthy",
            },
            {
                "name": "Database Connections",
                "value": await db.fetch_val("SELECT COUNT(*) FROM pg_stat_activity") if db.dialect == "postgresql" else 0,
                "status": "healthy",
            },
        ]

        # Recent errors
        recent_errors = await db.fetch_all(
            """
            SELECT error_type, COUNT(*) as count, MAX(created_at) as last_seen
            FROM error_logs
            WHERE created_at > :cutoff
            GROUP BY error_type
            ORDER BY count DESC
            LIMIT 5
            """,
            {"cutoff": datetime.now(UTC) - timedelta(hours=24)},
        )

        # Top users by API usage
        top_users = await db.fetch_all(
            """
            SELECT user_id, COUNT(*) as api_calls, SUM(cost) as cost
            FROM api_logs
            WHERE created_at >= :start_date
            GROUP BY user_id
            ORDER BY api_calls DESC
            LIMIT 10
            """,
            {"start_date": datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)},
        )

        # Get user names for top users
        user_ids = [user["user_id"] for user in top_users]
        if user_ids:
            users_map = await db.fetch_all(
                "SELECT id, name FROM users WHERE id IN :ids",
                {"ids": user_ids},
            )
            users_dict = {user["id"]: user["name"] for user in users_map}
            for user in top_users:
                user["name"] = users_dict.get(user["user_id"], f"User {user['user_id'][:8]}")
        else:
            top_users = []

        return AdminDashboardResponse(
            total_users=total_users or 0,
            active_users=active_users or 0,
            api_calls_today=api_calls_today or 0,
            error_rate=round(error_rate, 4),
            system_health=round((1 - error_rate) * 100, 1),
            cache_hit_rate=round(cache_hit_rate * 100, 1),
            total_cost=round(total_cost or 0, 2),
            avg_response_time=int(avg_response_time or 0),
            system_metrics=system_metrics,
            recent_errors=[
                {
                    "type": err["error_type"],
                    "count": err["count"],
                    "last_seen": format_time_ago(err["last_seen"]),
                }
                for err in recent_errors
            ],
            top_users=[
                {
                    "id": user["user_id"],
                    "name": user["name"],
                    "api_calls": user["api_calls"],
                    "cost": round(user["cost"] or 0, 2),
                }
                for user in top_users
            ],
        )

    except Exception as e:
        logger.exception(f"Error fetching admin dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch admin dashboard data",
        )


@router.get("/user", response_model=UserDashboardResponse)
async def get_user_dashboard(request: Request):
    """
    Get user dashboard data.

    Returns dashboard data for the current user.
    """
    user_id = getattr(request.state, "user_id", None)
    tenant_id = getattr(request.state, "tenant_id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        db = await get_database_service()

        # Get tool executions count
        tool_executions = (
            await db.fetch_val(
                "SELECT COUNT(*) FROM tool_executions WHERE user_id = :user_id AND created_at >= :cutoff",
                {"user_id": user_id, "cutoff": datetime.now(UTC) - timedelta(days=30)},
            )
            or 0
        )

        # Get cache hit rate for user
        cache_hits = (
            await db.fetch_val(
                "SELECT SUM(hits) FROM cache_metrics WHERE user_id = :user_id AND created_at > :cutoff",
                {"user_id": user_id, "cutoff": datetime.now(UTC) - timedelta(hours=24)},
            )
            or 0
        )
        cache_misses = (
            await db.fetch_val(
                "SELECT SUM(misses) FROM cache_metrics WHERE user_id = :user_id AND created_at > :cutoff",
                {"user_id": user_id, "cutoff": datetime.now(UTC) - timedelta(hours=24)},
            )
            or 0
        )
        total_cache = cache_hits + cache_misses
        cache_hit_rate = cache_hits / total_cache if total_cache > 0 else 0

        # Get storage usage (estimate from artifacts/uploads)
        storage_used = (
            await db.fetch_val(
                "SELECT SUM(size_bytes) FROM files WHERE user_id = :user_id",
                {"user_id": user_id},
            )
            or 0
        )
        storage_used_gb = storage_used / (1024**3)  # Convert to GB

        # Get API quota and usage
        api_quota = (
            await db.fetch_val(
                "SELECT quota FROM api_quotas WHERE user_id = :user_id AND period = :period",
                {"user_id": user_id, "period": "monthly"},
            )
            or 10000
        )  # Default quota

        api_used = (
            await db.fetch_val(
                "SELECT COUNT(*) FROM api_logs WHERE user_id = :user_id AND created_at >= :start_date",
                {"user_id": user_id, "start_date": datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)},
            )
            or 0
        )

        # Get average response time
        avg_response_time = (
            await db.fetch_val(
                "SELECT AVG(duration_ms) FROM api_logs WHERE user_id = :user_id AND created_at > :cutoff",
                {"user_id": user_id, "cutoff": datetime.now(UTC) - timedelta(hours=24)},
            )
            or 0
        )

        # Get success rate
        success_count = (
            await db.fetch_val(
                "SELECT COUNT(*) FROM api_logs WHERE user_id = :user_id AND status_code < 400 AND created_at > :cutoff",
                {"user_id": user_id, "cutoff": datetime.now(UTC) - timedelta(hours=24)},
            )
            or 0
        )
        total_count = (
            await db.fetch_val(
                "SELECT COUNT(*) FROM api_logs WHERE user_id = :user_id AND created_at > :cutoff",
                {"user_id": user_id, "cutoff": datetime.now(UTC) - timedelta(hours=24)},
            )
            or 0
        )
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        # API usage by period
        api_usage = [
            {
                "period": "Today",
                "used": await db.fetch_val(
                    "SELECT COUNT(*) FROM api_logs WHERE user_id = :user_id AND DATE(created_at) = :today",
                    {"user_id": user_id, "today": datetime.now(UTC).date()},
                )
                or 0,
                "quota": api_quota // 30,  # Daily quota
            },
            {
                "period": "This Week",
                "used": await db.fetch_val(
                    "SELECT COUNT(*) FROM api_logs WHERE user_id = :user_id AND created_at >= :week_start",
                    {"user_id": user_id, "week_start": datetime.now(UTC) - timedelta(days=datetime.now(UTC).weekday())},
                )
                or 0,
                "quota": api_quota // 4,  # Weekly quota
            },
            {
                "period": "This Month",
                "used": api_used,
                "quota": api_quota,
            },
        ]

        # Top tools used by user
        top_tools = await db.fetch_all(
            """
            SELECT tool_id, tool_name, COUNT(*) as executions,
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
            FROM tool_executions
            WHERE user_id = :user_id AND created_at >= :cutoff
            GROUP BY tool_id, tool_name
            ORDER BY executions DESC
            LIMIT 5
            """,
            {"user_id": user_id, "cutoff": datetime.now(UTC) - timedelta(days=30)},
        )

        # Recent activity
        recent_activity = await db.fetch_all(
            """
            SELECT id, action, tool_name, status, created_at
            FROM activity_logs
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT 10
            """,
            {"user_id": user_id},
        )

        return UserDashboardResponse(
            tool_executions=tool_executions,
            cache_hit_rate=round(cache_hit_rate * 100, 1),
            storage_used=round(storage_used_gb, 1),
            storage_quota=10.0,  # Default 10GB
            api_quota=api_quota,
            api_used=api_used,
            avg_response_time=int(avg_response_time),
            success_rate=round(success_rate, 1),
            api_usage=api_usage,
            top_tools=[
                {
                    "name": tool["tool_name"],
                    "executions": tool["executions"],
                    "success_rate": round(tool["success_rate"], 1),
                }
                for tool in top_tools
            ],
            recent_activity=[
                {
                    "id": activity["id"],
                    "action": activity["action"],
                    "tool": activity["tool_name"],
                    "time": format_time_ago(activity["created_at"]),
                    "status": activity["status"],
                }
                for activity in recent_activity
            ],
        )

    except Exception as e:
        logger.exception(f"Error fetching user dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user dashboard data",
        )


@router.get("/export/{type}")
async def export_dashboard_data(type: str, request: Request):
    """
    Export dashboard data as CSV.

    Args:
        type: "admin" or "user"
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    # Check permissions based on type
    if type == "admin":
        # Verify user has admin role (implement based on your auth system)
        pass

    try:
        db = await get_database_service()

        # Generate CSV data based on type
        if type == "admin":
            # Fetch admin data
            data = await db.fetch_all("SELECT * FROM users")
            headers = ["ID", "Name", "Email", "Created At", "Last Seen"]
        else:
            # Fetch user-specific data
            data = await db.fetch_all(
                "SELECT * FROM api_logs WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1000",
                {"user_id": user_id},
            )
            headers = ["ID", "Endpoint", "Method", "Status", "Duration", "Created At"]

        # Create CSV content
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in data:
            writer.writerow([str(row[col]) for col in row])

        csv_content = output.getvalue()
        output.close()

        from fastapi.responses import PlainTextResponse

        return PlainTextResponse(
            content=csv_content,
            headers={"Content-Disposition": f"attachment; filename=dashboard-{type}-{datetime.now(UTC).strftime('%Y-%m-%d')}.csv"},
        )

    except Exception as e:
        logger.exception(f"Error exporting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export dashboard data",
        )


def format_time_ago(dt: datetime) -> str:
    """Format datetime as relative time (e.g., '2 min ago')."""
    now = datetime.now(UTC)
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} min{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"
