"""Subscription and billing models for DeerFlow."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from deerflow.models.tool_models import Base


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration."""
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class SubscriptionPlan(str, Enum):
    """Subscription plan enumeration."""
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class TenantModel(Base):
    """Tenant model for multi-tenancy."""
    __tablename__ = "tenants"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    subscriptions = relationship("SubscriptionModel", back_populates="tenant", cascade="all, delete-orphan")


class SubscriptionModel(Base):
    """Subscription model."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String(255), nullable=False)

    # Stripe related fields
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    stripe_customer_id = Column(String(255), index=True)
    stripe_price_id = Column(String(255), nullable=True)

    # Alipay related fields
    alipay_trade_no = Column(String(255), unique=True, index=True, nullable=True)
    alipay_payment_id = Column(String(255), index=True, nullable=True)

    # Payment gateway
    payment_gateway = Column(String(50), default="stripe")  # stripe or alipay

    # Subscription information
    plan = Column(SQLEnum(SubscriptionPlan), nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.INCOMPLETE)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    # Billing information
    amount = Column(Float)  # Amount in the respective currency
    currency = Column(String(3), default="usd")  # usd or cny
    billing_cycle_days = Column(Integer, default=90)  # Quarterly billing

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    tenant = relationship("TenantModel", back_populates="subscriptions")
    invoices = relationship("InvoiceModel", back_populates="subscription", cascade="all, delete-orphan")


class InvoiceModel(Base):
    """Invoice model."""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    # Stripe related fields
    stripe_invoice_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # Alipay related fields
    alipay_trade_no = Column(String(255), unique=True, index=True, nullable=True)

    # Invoice information
    number = Column(String(255))
    amount = Column(Float)  # Amount in the respective currency
    currency = Column(String(3), default="usd")  # usd or cny
    status = Column(String(50))  # paid, open, void, etc.
    hosted_invoice_url = Column(String, nullable=True)
    invoice_pdf = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    subscription = relationship("SubscriptionModel", back_populates="invoices")


class UsageRecordModel(Base):
    """Usage tracking model for billing."""
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)

    # Usage metrics
    api_calls = Column(Integer, default=0)
    storage_bytes = Column(Integer, default=0)  # Bytes
    compute_seconds = Column(Float, default=0.0)

    # Billing period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    tenant = relationship("TenantModel")
    subscription = relationship("SubscriptionModel")