"""API Rate Limiting Middleware for DeerFlow."""

import os
import time
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta, timezone

from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session

from deerflow.models.subscription import SubscriptionModel, SubscriptionPlan
from deerflow.services.database import get_session


class RateLimitConfig:
    """Rate limiting configuration per plan."""
    
    # Requests per minute limits
    LIMITS = {
        SubscriptionPlan.BASIC: 100,      # 100 req/min
        SubscriptionPlan.PRO: 500,        # 500 req/min
        SubscriptionPlan.ENTERPRISE: -1,  # Unlimited
    }
    
    # Burst limits (requests per second)
    BURST_LIMITS = {
        SubscriptionPlan.BASIC: 10,       # 10 req/sec
        SubscriptionPlan.PRO: 50,         # 50 req/sec
        SubscriptionPlan.ENTERPRISE: -1,  # Unlimited
    }


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self):
        # Store request counts: {tenant_id: (count, last_reset_time)}
        self._request_counts: Dict[str, Tuple[int, datetime]] = {}
        self._last_reset_time: Dict[str, datetime] = {}
        
    def _reset_if_needed(self, tenant_id: str, minute_window: int = 1) -> None:
        """Reset counter if time window has passed."""
        now = datetime.now(timezone.utc)
        if tenant_id not in self._last_reset_time:
            self._last_reset_time[tenant_id] = now
            self._request_counts[tenant_id] = 0
            return
        
        last_reset = self._last_reset_time[tenant_id]
        if (now - last_reset).total_seconds() > minute_window * 60:
            self._last_reset_time[tenant_id] = now
            self._request_counts[tenant_id] = 0
    
    def check_rate_limit(
        self,
        tenant_id: str,
        limit: int,
        burst_limit: int = None
    ) -> Tuple[bool, Dict[str, str]]:
        """
        Check if request is within rate limit.
        
        Args:
            tenant_id: Tenant identifier
            limit: Requests per minute limit (-1 for unlimited)
            burst_limit: Burst requests per second (-1 for unlimited)
            
        Returns:
            (allowed, headers) tuple
        """
        # Unlimited
        if limit == -1:
            return True, {}
        
        # Reset if needed
        self._reset_if_needed(tenant_id)
        
        # Get current count
        current_count = self._request_counts.get(tenant_id, 0)
        
        # Check limit
        if current_count >= limit:
            return False, {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "Retry-After": "60"
            }
        
        # Increment and return headers
        self._request_counts[tenant_id] = current_count + 1
        
        return True, {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(limit - current_count - 1),
            "X-RateLimit-Reset": str(int(self._last_reset_time[tenant_id].timestamp()) + 60)
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


async def apply_rate_limit(request: Request, call_next):
    """FastAPI middleware for rate limiting."""
    
    tenant_id = getattr(request.state, "tenant_id", None)
    
    # Skip rate limiting for unauthenticated requests or health checks
    if not tenant_id or request.url.path in ["/health", "/metrics"]:
        return await call_next(request)
    
    # Get tenant's subscription plan
    try:
        db = next(get_session())
        subscription = db.query(SubscriptionModel).filter(
            SubscriptionModel.tenant_id == tenant_id
        ).first()
        
        plan = subscription.plan if subscription else SubscriptionPlan.BASIC
        
        # Get rate limit for this plan
        limit = RateLimitConfig.LIMITS.get(plan, 100)
        burst_limit = RateLimitConfig.BURST_LIMITS.get(plan, 10)
        
        # Check rate limit
        allowed, headers = rate_limiter.check_rate_limit(tenant_id, limit, burst_limit)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers=headers
            )
        
        # Call next middleware/handler
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Rate limiting error: {str(e)}")
        # Allow request if rate limiting fails
        return await call_next(request)


async def get_rate_limit_status(db: Session, tenant_id: str) -> Dict:
    """Get current rate limit status for a tenant."""
    
    subscription = db.query(SubscriptionModel).filter(
        SubscriptionModel.tenant_id == tenant_id
    ).first()
    
    if not subscription:
        plan = SubscriptionPlan.BASIC
    else:
        plan = subscription.plan
    
    limit = RateLimitConfig.LIMITS.get(plan, 100)
    burst_limit = RateLimitConfig.BURST_LIMITS.get(plan, 10)
    
    current_count = rate_limiter._request_counts.get(tenant_id, 0)
    
    return {
        "plan": plan.value,
        "limit": limit,
        "burst_limit": burst_limit,
        "current_requests": current_count,
        "remaining_requests": max(0, limit - current_count) if limit > 0 else -1,
        "next_reset": rate_limiter._last_reset_time.get(tenant_id, datetime.now(timezone.utc)) + timedelta(minutes=1)
    }
