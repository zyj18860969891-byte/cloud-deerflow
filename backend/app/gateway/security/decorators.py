"""Security decorators for API endpoints.

Provides decorators for common security concerns:
- Input validation
- Rate limiting per endpoint
- Permission checks
- Audit logging
"""

import functools
import inspect
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, ValidationError

from .audit import AuditLogger
from .input_validator import InputValidator


def validate_request_body(model: BaseModel):
    """
    Decorator to validate request body against a Pydantic model.

    Args:
        model: Pydantic model class to validate against
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the request body argument
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param.annotation == model or (hasattr(param.annotation, "__origin__") and model in getattr(param.annotation, "__args__", [])):
                    if param_name in kwargs:
                        try:
                            # Validate using Pydantic model
                            validated = model(**kwargs[param_name])
                            kwargs[param_name] = validated
                        except ValidationError as e:
                            raise HTTPException(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=e.errors(),
                            )
                    break
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def sanitize_inputs(func: Callable) -> Callable:
    """
    Decorator to sanitize string inputs in request body.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        validator = InputValidator()

        # Recursively sanitize string values in kwargs
        def sanitize_value(value: Any) -> Any:
            if isinstance(value, str):
                try:
                    return validator.sanitize_string(value)
                except ValueError as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e),
                    )
            elif isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_value(item) for item in value]
            else:
                return value

        sanitized_kwargs = {k: sanitize_value(v) for k, v in kwargs.items()}
        return await func(*args, **sanitized_kwargs)

    return wrapper


def require_permissions(required_permissions: list[str]):
    """
    Decorator to require specific permissions for an endpoint.

    Args:
        required_permissions: List of required permissions (e.g., ["tools:read", "tools:write"])
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get user context from request state (set by authentication middleware)
            user_permissions = getattr(request.state, "user_permissions", [])

            # Check if user has all required permissions
            for perm in required_permissions:
                if perm not in user_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required permission: {perm}",
                    )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def audit_action(action: str, resource_type: str = None):
    """
    Decorator to automatically log an audit event for an endpoint.

    Args:
        action: Action being performed (e.g., "create", "update", "delete")
        resource_type: Type of resource being accessed (e.g., "tool", "tenant")
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            audit_logger = AuditLogger()

            try:
                result = await func(request, *args, **kwargs)

                # Log successful action
                user_id = getattr(request.state, "user_id", None)
                tenant_id = getattr(request.state, "tenant_id", None)

                # Extract resource ID from path parameters if available
                resource_id = None
                if "resource_id" in kwargs:
                    resource_id = kwargs["resource_id"]
                elif "id" in kwargs:
                    resource_id = kwargs["id"]

                audit_logger.log_admin_action(
                    action=action,
                    user_id=user_id or "anonymous",
                    tenant_id=tenant_id,
                    request=request,
                    target_resource=f"{resource_type}:{resource_id}" if resource_type and resource_id else None,
                    changes={"result": "success"},
                )

                return result

            except HTTPException as e:
                # Log failed action
                audit_logger.log_admin_action(
                    action=action,
                    user_id=getattr(request.state, "user_id", None) or "anonymous",
                    tenant_id=getattr(request.state, "tenant_id", None),
                    request=request,
                    target_resource=resource_type,
                    changes={"error": str(e.detail), "status_code": e.status_code},
                )
                raise
            except Exception as e:
                # Log unexpected errors
                audit_logger.log_admin_action(
                    action=action,
                    user_id=getattr(request.state, "user_id", None) or "anonymous",
                    tenant_id=getattr(request.state, "tenant_id", None),
                    request=request,
                    target_resource=resource_type,
                    changes={"error": str(e), "status_code": 500},
                )
                raise

        return wrapper

    return decorator


def limit_request_size(max_size: int = 10 * 1024 * 1024):
    """
    Decorator to limit request body size.

    Args:
        max_size: Maximum request body size in bytes (default 10MB)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body too large. Maximum size: {max_size} bytes",
                )

            # Also check actual body size if possible
            body = await request.body()
            if len(body) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body too large. Maximum size: {max_size} bytes",
                )

            # Reconstruct request with body
            request._body = body
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
