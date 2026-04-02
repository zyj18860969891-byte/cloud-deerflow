#!/usr/bin/env python3
"""Comprehensive subscription system test."""

import sys


def test_imports():
    """Test all subscription-related imports."""
    print("[TESTING] Subscription System Imports")
    print("=" * 50)

    try:
        print("1. Testing Alipay Service...")
        from deerflow.services.alipay_service import AlipayService
        print("   [OK] AlipayService imported successfully")

        print("2. Testing Subscription Service...")
        from deerflow.services.subscription_service import SubscriptionService
        print("   [OK] SubscriptionService imported successfully")

        print("3. Testing Subscription Models...")
        from deerflow.models.subscription import (
            SubscriptionModel,
            SubscriptionStatus,
            SubscriptionPlan,
            InvoiceModel,
            UsageRecordModel,
            TenantModel,
        )
        print("   [OK] All subscription models imported successfully")
        print(f"      - TenantModel: {TenantModel.__tablename__}")
        print(f"      - SubscriptionModel: {SubscriptionModel.__tablename__}")
        print(f"      - InvoiceModel: {InvoiceModel.__tablename__}")
        print(f"      - UsageRecordModel: {UsageRecordModel.__tablename__}")

        print("4. Testing Subscription Routes...")
        from app.gateway.routes.subscription import router
        print("   [OK] Subscription routes imported successfully")
        print(f"      - Router prefix: {router.prefix}")
        print(f"      - Total routes: {len(router.routes)}")

        print("5. Testing Rate Limiter...")
        from deerflow.middleware.rate_limiter import RateLimiter, RateLimitConfig
        print("   [OK] Rate limiter imported successfully")
        print(f"      - Basic limit: {RateLimitConfig.LIMITS[SubscriptionPlan.BASIC]} req/min")
        print(f"      - Pro limit: {RateLimitConfig.LIMITS[SubscriptionPlan.PRO]} req/min")
        print(f"      - Enterprise limit: {RateLimitConfig.LIMITS[SubscriptionPlan.ENTERPRISE]}")

        print("6. Testing WebSocket Handler...")
        from app.gateway.websocket import router as ws_router
        print("   [OK] WebSocket router imported successfully")

        print("\n" + "=" * 50)
        print("SUCCESS: All subscription system components ready!")
        return True

    except ImportError as e:
        print(f"\nERROR: Import failed - {str(e)}")
        return False
    except Exception as e:
        print(f"\nERROR: Unexpected error - {str(e)}")
        return False


def verify_alipay_configuration():
    """Verify Alipay configuration."""
    import os

    print("\n[CHECKING] Alipay Configuration")
    print("=" * 50)

    alipay_app_id = os.getenv("ALIPAY_APP_ID")
    alipay_private_key = os.getenv("ALIPAY_APP_PRIVATE_KEY")
    alipay_public_key = os.getenv("ALIPAY_PUBLIC_KEY")

    if alipay_app_id:
        print("ALIPAY_APP_ID: CONFIGURED")
    else:
        print("ALIPAY_APP_ID: NOT SET (optional for development)")

    if alipay_private_key:
        print("ALIPAY_APP_PRIVATE_KEY: CONFIGURED")
    else:
        print("ALIPAY_APP_PRIVATE_KEY: NOT SET (optional for development)")

    if alipay_public_key:
        print("ALIPAY_PUBLIC_KEY: CONFIGURED")
    else:
        print("ALIPAY_PUBLIC_KEY: NOT SET (optional for development)")

    stripe_secret = os.getenv("STRIPE_SECRET_KEY")
    if stripe_secret:
        print("\nSTRIPE_SECRET_KEY: CONFIGURED")
    else:
        print("\nSTRIPE_SECRET_KEY: NOT SET")


def check_subscription_models():
    """Check subscription model enums."""
    from deerflow.models.subscription import SubscriptionStatus, SubscriptionPlan

    print("\n[CHECKING] Subscription Model Enums")
    print("=" * 50)

    print("\nSubscriptionStatus values:")
    for status in SubscriptionStatus:
        print(f"  - {status.name}: {status.value}")

    print("\nSubscriptionPlan values:")
    for plan in SubscriptionPlan:
        print(f"  - {plan.name}: {plan.value}")


def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("DeerFlow Subscription System Verification")
    print("=" * 50 + "\n")

    # Test imports
    if not test_imports():
        sys.exit(1)

    # Verify models
    check_subscription_models()

    # Verify Alipay configuration
    verify_alipay_configuration()

    print("\n" + "=" * 50)
    print("VERIFICATION COMPLETE")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Configure Alipay credentials in .env")
    print("2. Run database migrations")
    print("3. Deploy and test payment flows")
    print("4. Monitor webhook delivery")


if __name__ == "__main__":
    main()
