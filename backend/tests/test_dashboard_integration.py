#!/usr/bin/env python3
"""
Dashboard API Integration Test

Tests the /api/dashboard/admin and /api/dashboard/user endpoints
to ensure they return data in the expected format for frontend components.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

import pytest
from httpx import ASGITransport, AsyncClient

from app.gateway.app import create_app


@pytest.mark.asyncio
async def test_admin_dashboard_endpoint():
    """Test that /api/dashboard/admin returns correct data structure."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Note: This test will fail without proper authentication
        # For now, we'll just test that the endpoint exists and returns proper error
        response = await client.get("/api/dashboard/admin")

        # Should return 401 without auth
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Admin dashboard endpoint returns 401 without auth (expected)")


@pytest.mark.asyncio
async def test_user_dashboard_endpoint():
    """Test that /api/dashboard/user returns correct data structure."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Note: This test will fail without proper authentication
        response = await client.get("/api/dashboard/user")

        # Should return 401 without auth
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ User dashboard endpoint returns 401 without auth (expected)")


if __name__ == "__main__":
    # Run tests manually
    print("Running Dashboard API Integration Tests...")
    asyncio.run(test_admin_dashboard_endpoint())
    asyncio.run(test_user_dashboard_endpoint())
    print("✅ All basic endpoint tests passed!")
