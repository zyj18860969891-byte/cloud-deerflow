"""Subscription management API routes."""

import os
import stripe
from datetime import datetime, timezone
from typing import Dict, Any
from urllib.parse import parse_qs, unquote

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from deerflow.services.database import get_session
from deerflow.services.subscription_service import SubscriptionService, SubscriptionPlan
from deerflow.services.alipay_service import AlipayService
from deerflow.models.subscription import SubscriptionStatus

router = APIRouter(prefix="/api", tags=["subscription"])


def get_tenant_id(request: Request) -> str:
    """Get tenant ID from request."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant ID required")
    return tenant_id


@router.post("/checkout")
async def create_checkout_session(
    request: Request,
    plan_id: str,
    price_id: str,
    db: Session = Depends(get_session)
):
    """Create Stripe Checkout Session."""
    tenant_id = get_tenant_id(request)
    user_id = getattr(request.state, "user_id", None)

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    service = SubscriptionService(db)

    # Check if already has active subscription
    existing = service.get_subscription(tenant_id)
    if existing and existing.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already has an active subscription")

    # Validate plan_id matches price_id
    try:
        price = stripe.Price.retrieve(price_id)
        if price.product != plan_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan ID does not match price ID")
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid price ID: {str(e)}")

    # Create subscription with quarterly billing (90 days)
    result = service.create_subscription(
        tenant_id=tenant_id,
        user_id=user_id,
        price_id=price_id,
        trial_days=14 if plan_id == "price_basic_quarterly" else 0
    )

    return result


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    db: Session = Depends(get_session)
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    service = SubscriptionService(db)
    service.handle_webhook(event)

    return {"status": "success"}


@router.post("/checkout-alipay")
async def create_alipay_checkout(
    request: Request,
    plan: str,
    return_url: str = None,
    db: Session = Depends(get_session)
):
    """Create Alipay payment URL for subscription."""
    tenant_id = get_tenant_id(request)
    user_id = getattr(request.state, "user_id", None)
    email = getattr(request.state, "email", f"{user_id}@deerflow.local")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        # Validate plan
        plan_enum = SubscriptionPlan[plan.upper()]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid plan: {plan}")

    service = AlipayService(db)

    # Check if already has active subscription
    existing = service.db.query(type(service.db.query(type).first())) if False else None
    # Simple check
    from deerflow.models.subscription import SubscriptionModel
    existing = db.query(SubscriptionModel).filter(
        SubscriptionModel.tenant_id == tenant_id
    ).first()
    
    if existing and existing.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already has an active subscription")

    try:
        payment_url = service.create_payment_url(
            tenant_id=tenant_id,
            user_id=user_id,
            plan=plan_enum,
            email=email,
            return_url=return_url
        )
        return {"payment_url": payment_url, "plan": plan, "currency": "cny"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create Alipay payment: {str(e)}")


@router.post("/webhook-alipay")
async def handle_alipay_webhook(
    request: Request,
    db: Session = Depends(get_session)
):
    """Handle Alipay webhook notifications."""
    # Parse form data
    body = await request.body()
    params = {}
    
    try:
        # Parse query string from body
        if isinstance(body, bytes):
            body_str = body.decode('utf-8')
        else:
            body_str = body
        
        # Parse form-encoded body
        for item in body_str.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                params[unquote(key)] = unquote(value)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request format")

    if not params:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No parameters provided")

    service = AlipayService(db)
    
    try:
        success = service.handle_webhook_notify(params)
        if success:
            return {"result": "success"}
        else:
            return {"result": "failed"}, status.HTTP_400_BAD_REQUEST
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Webhook processing error: {str(e)}")


@router.get("/current")
async def get_current_subscription(
    request: Request,
    db: Session = Depends(get_session)
):
    """Get current subscription information."""
    tenant_id = get_tenant_id(request)
    service = SubscriptionService(db)
    subscription = service.get_subscription(tenant_id)

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subscription found")

    return {
        "id": subscription.id,
        "plan": subscription.plan.value,
        "status": subscription.status.value,
        "current_period_start": subscription.current_period_start.isoformat(),
        "current_period_end": subscription.current_period_end.isoformat(),
        "amount": subscription.amount,
        "currency": subscription.currency,
        "cancel_at_period_end": subscription.cancel_at_period_end
    }


@router.post("/cancel")
async def cancel_subscription(
    request: Request,
    db: Session = Depends(get_session)
):
    """Cancel subscription."""
    tenant_id = get_tenant_id(request)
    service = SubscriptionService(db)
    subscription = service.get_subscription(tenant_id)

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subscription found")

    if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subscription cannot be cancelled in current status")

    success = service.cancel_subscription(subscription.id, at_period_end=True)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to cancel subscription")

    return {
        "status": "cancelled",
        "effective_at": subscription.current_period_end.isoformat()
    }


@router.get("/usage")
async def get_usage_metrics(
    request: Request,
    db: Session = Depends(get_session)
):
    """Get current usage metrics."""
    tenant_id = get_tenant_id(request)
    service = SubscriptionService(db)
    metrics = service.get_usage_metrics(tenant_id)

    return metrics


@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans (quarterly billing)."""
    return {
        "plans": [
            {
                "id": "basic",
                "name": "Basic",
                "description": "Get started with DeerFlow",
                "billing_cycle": "quarterly",
                "billing_days": 90,
                "pricing": [
                    {
                        "gateway": "stripe",
                        "price": 39.00,
                        "currency": "usd",
                        "price_id": "price_basic_quarterly"
                    },
                    {
                        "gateway": "alipay",
                        "price": 99.00,
                        "currency": "cny",
                        "price_id": None
                    }
                ],
                "features": [
                    "30,000 API calls/quarter",
                    "3 GB storage",
                    "Email support",
                    "1 user",
                    "Basic analytics"
                ]
            },
            {
                "id": "pro",
                "name": "Pro",
                "description": "For growing teams",
                "billing_cycle": "quarterly",
                "billing_days": 90,
                "pricing": [
                    {
                        "gateway": "stripe",
                        "price": 249.00,
                        "currency": "usd",
                        "price_id": "price_pro_quarterly"
                    },
                    {
                        "gateway": "alipay",
                        "price": 399.00,
                        "currency": "cny",
                        "price_id": None
                    }
                ],
                "features": [
                    "300,000 API calls/quarter",
                    "30 GB storage",
                    "Priority support",
                    "5 users",
                    "Advanced analytics",
                    "Custom integrations"
                ]
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "description": "For large organizations",
                "billing_cycle": "quarterly",
                "billing_days": 90,
                "pricing": [
                    {
                        "gateway": "stripe",
                        "price": 749.00,
                        "currency": "usd",
                        "price_id": "price_enterprise_quarterly"
                    },
                    {
                        "gateway": "alipay",
                        "price": 1299.00,
                        "currency": "cny",
                        "price_id": None
                    }
                ],
                "features": [
                    "Unlimited API calls",
                    "Unlimited storage",
                    "24/7 dedicated support",
                    "Unlimited users",
                    "Custom integrations",
                    "SLA guarantee",
                    "Dedicated account manager",
                    "Advanced security features"
                ]
            }
        ],
        "payment_methods": [
            {
                "gateway": "stripe",
                "name": "Stripe",
                "description": "Credit/Debit cards, Apple Pay, Google Pay",
                "currencies": ["usd"],
                "regions": ["Global"]
            },
            {
                "gateway": "alipay",
                "name": "Alipay",
                "description": "Chinese payment method",
                "currencies": ["cny"],
                "regions": ["China"]
            }
        ]
    }