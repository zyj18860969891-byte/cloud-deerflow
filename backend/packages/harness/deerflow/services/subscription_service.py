"""Subscription management service for DeerFlow."""

import os
import stripe
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session
from sqlalchemy import select, update

from deerflow.models.subscription import (
    SubscriptionModel,
    SubscriptionStatus,
    SubscriptionPlan,
    InvoiceModel,
    UsageRecordModel,
    TenantModel
)
from deerflow.services.database import get_session


# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY environment variable is required")


class SubscriptionService:
    """Subscription management service."""

    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, tenant_id: str, user_id: str, email: str) -> str:
        """Create a Stripe customer."""
        customer = stripe.Customer.create(
            email=email,
            metadata={
                "tenant_id": tenant_id,
                "user_id": user_id
            }
        )
        return customer.id

    def create_subscription(
        self,
        tenant_id: str,
        user_id: str,
        price_id: str,
        trial_days: int = 0,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new subscription."""
        try:
            # Get or create customer
            if not customer_id:
                customer_id = self.create_customer(tenant_id, user_id, f"{user_id}@deerflow.local")

            # Prepare subscription parameters
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"],
            }

            if trial_days > 0:
                subscription_params["trial_period_days"] = trial_days

            # Create Stripe subscription
            subscription = stripe.Subscription.create(**subscription_params)

            # Determine plan from price ID
            plan = self._determine_plan_from_price(price_id)

            # Save to database
            db_subscription = SubscriptionModel(
                tenant_id=tenant_id,
                user_id=user_id,
                stripe_subscription_id=subscription.id,
                stripe_customer_id=customer_id,
                stripe_price_id=price_id,
                plan=plan,
                status=SubscriptionStatus.INCOMPLETE,
                current_period_start=datetime.fromtimestamp(subscription.current_period_start, tz=timezone.utc),
                current_period_end=datetime.fromtimestamp(subscription.current_period_end, tz=timezone.utc),
                amount=self._get_price_amount(price_id),
                currency=subscription.items.data[0].price.currency,
                billing_cycle_days=90,  # Quarterly billing
                payment_gateway="stripe"
            )

            self.db.add(db_subscription)
            self.db.commit()
            self.db.refresh(db_subscription)

            return {
                "subscription_id": db_subscription.id,
                "stripe_subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }

        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    def _determine_plan_from_price(self, price_id: str) -> SubscriptionPlan:
        """Determine subscription plan from Stripe price ID."""
        # This mapping should be configured based on your Stripe prices
        price_plan_map = {
            "price_basic_quarterly": SubscriptionPlan.BASIC,
            "price_pro_quarterly": SubscriptionPlan.PRO,
            "price_enterprise_quarterly": SubscriptionPlan.ENTERPRISE,
            # Keep legacy monthly prices for backward compatibility
            "price_basic_monthly": SubscriptionPlan.BASIC,
            "price_pro_monthly": SubscriptionPlan.PRO,
            "price_enterprise_monthly": SubscriptionPlan.ENTERPRISE,
        }
        return price_plan_map.get(price_id, SubscriptionPlan.BASIC)

    def _get_price_amount(self, price_id: str) -> float:
        """Get price amount from Stripe price ID."""
        try:
            price = stripe.Price.retrieve(price_id)
            return price.unit_amount / 100.0 if price.unit_amount else 0.0
        except stripe.error.StripeError:
            return 0.0

    def handle_webhook(self, event_data: Dict[str, Any]) -> None:
        """Handle Stripe webhook events."""
        event_type = event_data["type"]
        event = event_data["data"]["object"]

        if event_type == "invoice.payment_succeeded":
            self._handle_payment_succeeded(event)
        elif event_type == "invoice.payment_failed":
            self._handle_payment_failed(event)
        elif event_type == "customer.subscription.updated":
            self._handle_subscription_updated(event)
        elif event_type == "customer.subscription.deleted":
            self._handle_subscription_deleted(event)

    def _handle_payment_succeeded(self, invoice: Dict[str, Any]) -> None:
        """Handle successful payment."""
        subscription_id = invoice.get("subscription")
        if not subscription_id:
            return

        # Find subscription
        subscription = self.db.query(SubscriptionModel).filter(
            SubscriptionModel.stripe_subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.current_period_start = datetime.fromtimestamp(
                invoice["period_start"], tz=timezone.utc
            )
            subscription.current_period_end = datetime.fromtimestamp(
                invoice["period_end"], tz=timezone.utc
            )

            # Create invoice record
            invoice_record = InvoiceModel(
                subscription_id=subscription.id,
                stripe_invoice_id=invoice["id"],
                number=invoice.get("number"),
                amount=invoice["amount_paid"] / 100,
                currency=invoice["currency"],
                status="paid",
                hosted_invoice_url=invoice.get("hosted_invoice_url"),
                invoice_pdf=invoice.get("invoice_pdf"),
                paid_at=datetime.fromtimestamp(invoice["status_transitions"]["paid_at"], tz=timezone.utc) if invoice.get("status_transitions") else None
            )
            self.db.add(invoice_record)
            self.db.commit()

    def _handle_payment_failed(self, invoice: Dict[str, Any]) -> None:
        """Handle failed payment."""
        subscription_id = invoice.get("subscription")
        if not subscription_id:
            return

        subscription = self.db.query(SubscriptionModel).filter(
            SubscriptionModel.stripe_subscription_id == subscription_id
        ).first()

        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
            self.db.commit()

    def _handle_subscription_updated(self, stripe_subscription: Dict[str, Any]) -> None:
        """Handle subscription update."""
        subscription = self.db.query(SubscriptionModel).filter(
            SubscriptionModel.stripe_subscription_id == stripe_subscription["id"]
        ).first()

        if subscription:
            subscription.status = self._map_stripe_status(stripe_subscription["status"])
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_subscription["current_period_start"], tz=timezone.utc
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_subscription["current_period_end"], tz=timezone.utc
            )
            subscription.cancel_at_period_end = stripe_subscription.get("cancel_at_period_end", False)
            self.db.commit()

    def _handle_subscription_deleted(self, stripe_subscription: Dict[str, Any]) -> None:
        """Handle subscription deletion."""
        subscription = self.db.query(SubscriptionModel).filter(
            SubscriptionModel.stripe_subscription_id == stripe_subscription["id"]
        ).first()

        if subscription:
            subscription.status = SubscriptionStatus.CANCELED
            subscription.canceled_at = datetime.now(timezone.utc)
            self.db.commit()

    def _map_stripe_status(self, stripe_status: str) -> SubscriptionStatus:
        """Map Stripe status to internal status."""
        status_map = {
            "trialing": SubscriptionStatus.TRIALING,
            "active": SubscriptionStatus.ACTIVE,
            "past_due": SubscriptionStatus.PAST_DUE,
            "canceled": SubscriptionStatus.CANCELED,
            "unpaid": SubscriptionStatus.UNPAID,
            "incomplete": SubscriptionStatus.INCOMPLETE,
            "incomplete_expired": SubscriptionStatus.INCOMPLETE_EXPIRED,
        }
        return status_map.get(stripe_status, SubscriptionStatus.INCOMPLETE)

    def get_subscription(self, tenant_id: str) -> Optional[SubscriptionModel]:
        """Get subscription for a tenant."""
        return self.db.query(SubscriptionModel).filter(
            SubscriptionModel.tenant_id == tenant_id
        ).order_by(SubscriptionModel.created_at.desc()).first()

    def cancel_subscription(self, subscription_id: int, at_period_end: bool = True) -> bool:
        """Cancel a subscription."""
        subscription = self.db.query(SubscriptionModel).filter(
            SubscriptionModel.id == subscription_id
        ).first()

        if not subscription:
            return False

        try:
            # Update Stripe
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=at_period_end
            )

            # Update local state
            subscription.cancel_at_period_end = at_period_end
            if not at_period_end:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.now(timezone.utc)

            self.db.commit()
            return True

        except stripe.error.StripeError:
            return False

    def create_usage_record(
        self,
        tenant_id: str,
        api_calls: int = 0,
        storage_bytes: int = 0,
        compute_seconds: float = 0.0
    ) -> UsageRecordModel:
        """Create a usage record for billing."""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            raise ValueError(f"No subscription found for tenant {tenant_id}")

        # Determine billing period
        period_start = subscription.current_period_start
        period_end = subscription.current_period_end

        # Check if usage record exists for this period
        existing = self.db.query(UsageRecordModel).filter(
            UsageRecordModel.tenant_id == tenant_id,
            UsageRecordModel.subscription_id == subscription.id,
            UsageRecordModel.period_start == period_start,
            UsageRecordModel.period_end == period_end
        ).first()

        if existing:
            # Update existing record
            existing.api_calls += api_calls
            existing.storage_bytes += storage_bytes
            existing.compute_seconds += compute_seconds
            existing.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            return existing
        else:
            # Create new record
            usage_record = UsageRecordModel(
                tenant_id=tenant_id,
                subscription_id=subscription.id,
                api_calls=api_calls,
                storage_bytes=storage_bytes,
                compute_seconds=compute_seconds,
                period_start=period_start,
                period_end=period_end
            )
            self.db.add(usage_record)
            self.db.commit()
            self.db.refresh(usage_record)
            return usage_record

    def get_usage_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Get current usage metrics for a tenant."""
        subscription = self.get_subscription(tenant_id)
        if not subscription:
            return {}

        # Get current period usage
        usage = self.db.query(UsageRecordModel).filter(
            UsageRecordModel.tenant_id == tenant_id,
            UsageRecordModel.subscription_id == subscription.id,
            UsageRecordModel.period_start == subscription.current_period_start
        ).first()

        if not usage:
            return {
                "api_calls_used": 0,
                "api_calls_limit": self._get_plan_limit(subscription.plan, "api_calls"),
                "storage_used": 0.0,
                "storage_limit": self._get_plan_limit(subscription.plan, "storage_gb"),
                "compute_hours_used": 0.0,
                "compute_hours_limit": self._get_plan_limit(subscription.plan, "compute_hours")
            }

        # Convert storage to GB
        storage_gb = usage.storage_bytes / (1024 ** 3)

        return {
            "api_calls_used": usage.api_calls,
            "api_calls_limit": self._get_plan_limit(subscription.plan, "api_calls"),
            "storage_used": round(storage_gb, 2),
            "storage_limit": self._get_plan_limit(subscription.plan, "storage_gb"),
            "compute_hours_used": usage.compute_seconds / 3600.0,
            "compute_hours_limit": self._get_plan_limit(subscription.plan, "compute_hours")
        }

    def _get_plan_limit(self, plan: SubscriptionPlan, metric: str) -> int:
        """Get plan limits for different metrics (quarterly limits)."""
        # Limits are for 90-day quarterly periods
        limits = {
            SubscriptionPlan.BASIC: {
                "api_calls": 30000,        # 10k/month * 3
                "storage_gb": 3,           # 1GB/month * 3
                "compute_hours": 300      # 100h/month * 3
            },
            SubscriptionPlan.PRO: {
                "api_calls": 300000,       # 100k/month * 3
                "storage_gb": 30,          # 10GB/month * 3
                "compute_hours": 1500     # 500h/month * 3
            },
            SubscriptionPlan.ENTERPRISE: {
                "api_calls": -1,  # Unlimited
                "storage_gb": -1,  # Unlimited
                "compute_hours": -1  # Unlimited
            }
        }
        return limits.get(plan, {}).get(metric, 0)


# Convenience function to get subscription service
def get_subscription_service() -> SubscriptionService:
    """Get subscription service instance."""
    db = next(get_session())
    return SubscriptionService(db)