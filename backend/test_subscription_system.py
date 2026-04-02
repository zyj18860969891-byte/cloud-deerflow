#!/usr/bin/env python3
"""Test script for subscription system."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test that all subscription modules can be imported."""
    print("🧪 Testing Subscription System Imports...")

    try:
        # Test model imports
        from deerflow.models.subscription import (
            TenantModel,
            SubscriptionModel,
            InvoiceModel,
            UsageRecordModel,
            SubscriptionStatus,
            SubscriptionPlan,
        )
        print("✅ Subscription models imported successfully")

        # Test service imports
        from deerflow.services.subscription_service import SubscriptionService
        print("✅ Subscription service imported successfully")

        # Test router imports
        from app.gateway.routes.subscription import router
        print("✅ Subscription router imported successfully")

        # Verify models have correct attributes
        assert hasattr(TenantModel, '__tablename__')
        assert TenantModel.__tablename__ == "tenants"
        print("✅ TenantModel table name correct")

        assert hasattr(SubscriptionModel, '__tablename__')
        assert SubscriptionModel.__tablename__ == "subscriptions"
        print("✅ SubscriptionModel table name correct")

        # Check enum values
        assert hasattr(SubscriptionStatus, 'ACTIVE')
        assert hasattr(SubscriptionPlan, 'BASIC')
        print("✅ Enum values present")

        print("\n🎉 All import tests passed!")
        print("\n📋 Next steps for full testing:")
        print("1. Set up Stripe test keys in .env")
        print("2. Run database initialization: uv run python -c 'from deerflow.services.database import init_db; import asyncio; asyncio.run(init_db())'")
        print("3. Test API endpoints: uv run uvicorn app.gateway.app:app")
        print("4. Create test subscription via Stripe Checkout")
        print("5. Test webhook handling with Stripe CLI")

        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)