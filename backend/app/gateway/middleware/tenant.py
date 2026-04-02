"""Tenant Middleware for DeerFlow Gateway

This middleware extracts tenant identification from incoming requests
and injects it into the request context for multi-tenancy support.
"""

from collections.abc import Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Tenant identification middleware.

    Extracts tenant ID from various sources (subdomain, query param, header, JWT)
    and stores it in request.state.tenant_id for downstream use.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and extract tenant ID."""
        tenant_id = self._extract_tenant_id(request)

        if not tenant_id:
            # In development mode, allow a default tenant
            # In production, this should return an error
            import os

            if os.getenv("ENVIRONMENT") == "development":
                tenant_id = "default"
            else:
                raise HTTPException(status_code=400, detail="Missing tenant identification. Provide X-Tenant-ID header, query parameter ?tenant_id=, or use subdomain.")

        # Store tenant_id in request state
        request.state.tenant_id = tenant_id

        # Continue processing
        response = await call_next(request)
        return response

    def _extract_tenant_id(self, request: Request) -> str | None:
        """Extract tenant ID from request.

        Priority order:
        1. X-Tenant-ID header (explicit)
        2. Query parameter ?tenant_id=
        3. Subdomain (first part of host)
        4. JWT token claims (if implemented)
        """
        # Method 1: X-Tenant-ID header (most explicit)
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            return tenant_id.strip()

        # Method 2: Query parameter
        tenant_id = request.query_params.get("tenant_id")
        if tenant_id:
            return tenant_id.strip()

        # Method 3: Subdomain extraction
        host = request.headers.get("host", "")
        if host:
            # Remove port if present
            host_without_port = host.split(":")[0]
            # Get first segment before first dot
            parts = host_without_port.split(".")
            if len(parts) > 1 and parts[0] not in ["localhost", "127", "0"]:
                return parts[0]

        # Method 4: JWT token (future implementation)
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # TODO: Implement JWT parsing and tenant claim extraction
            # For now, return None to indicate no tenant found
            pass

        return None
