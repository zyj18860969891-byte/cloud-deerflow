"""Input validation and sanitization for DeerFlow Gateway.

Provides comprehensive input validation to prevent injection attacks
and ensure data integrity.
"""

import html
import json
import re
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError


class ValidationErrorDetail(BaseModel):
    """Detailed validation error."""

    field: str
    message: str
    value: Any


class InputValidator:
    """Comprehensive input validator."""

    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        # SQL injection patterns
        r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute|script)\s+",
        # Command injection patterns
        r"[;&|`$(){}]",
        # Path traversal patterns
        r"\.\.[/\\]",
        # XSS patterns
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        # LDAP injection
        r"[()|&*]",
    ]

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize a string input."""
        if not isinstance(value, str):
            raise ValueError("Value must be a string")

        # Trim whitespace
        value = value.strip()

        # Limit length
        if len(value) > max_length:
            raise ValueError(f"String too long (max {max_length} chars)")

        # Escape HTML entities to prevent XSS
        value = html.escape(value)

        # Check for dangerous patterns
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potentially dangerous content detected")

        return value

    @staticmethod
    def validate_json(value: str) -> dict[str, Any]:
        """Validate and parse JSON safely."""
        try:
            parsed = json.loads(value)
            if not isinstance(parsed, dict):
                raise ValueError("JSON must be an object")
            return parsed
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    @staticmethod
    def validate_identifier(value: str, pattern: str = r"^[a-zA-Z0-9_-]+$") -> str:
        """Validate identifiers (names, IDs, etc.)."""
        if not isinstance(value, str):
            raise ValueError("Identifier must be a string")

        value = value.strip()

        if not re.match(pattern, value):
            raise ValueError(f"Invalid format. Must match pattern: {pattern}")

        if len(value) > 100:
            raise ValueError("Identifier too long (max 100 chars)")

        return value

    @staticmethod
    def validate_email(value: str) -> str:
        """Validate email address."""
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email address")
        return value.lower().strip()

    @staticmethod
    def validate_url(value: str, allowed_schemes: list[str] = None) -> str:
        """Validate URL."""
        from urllib.parse import urlparse

        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]

        try:
            parsed = urlparse(value)
            if not parsed.scheme or parsed.scheme not in allowed_schemes:
                raise ValueError(f"URL must use one of: {', '.join(allowed_schemes)}")
            if not parsed.netloc:
                raise ValueError("Invalid URL: missing host")
            return value
        except Exception as e:
            raise ValueError(f"Invalid URL: {e}")

    @staticmethod
    def validate_json_schema(value: Any) -> dict[str, Any]:
        """Validate that value is a valid JSON object."""
        if isinstance(value, str):
            return InputValidator.validate_json(value)
        elif isinstance(value, dict):
            return value
        else:
            raise ValueError("Must be a JSON object or string")

    @staticmethod
    def sanitize_html_content(value: str) -> str:
        """Sanitize HTML content while preserving safe tags."""
        # Basic sanitization - escape dangerous patterns
        dangerous_tags = ["script", "iframe", "object", "embed", "form"]
        dangerous_attrs = ["onerror", "onload", "onclick", "onmouseover"]

        # Escape all HTML by default for maximum security
        # In production, you might want to use a library like bleach
        return html.escape(value)

    @classmethod
    def validate_model(cls, model_class: BaseModel, data: dict[str, Any]) -> BaseModel:
        """Validate data against a Pydantic model."""
        try:
            return model_class(**data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                errors.append(
                    ValidationErrorDetail(
                        field=field,
                        message=error["msg"],
                        value=error.get("input"),
                    )
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[err.dict() for err in errors],
            )


def validate_input_schema(schema: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate input data against a JSON schema.

    This is a simple implementation. For production, consider using
    a full JSON Schema validator like jsonschema.
    """
    validator = InputValidator()

    # Check required fields
    required_fields = schema.get("required", [])
    for field in required_fields:
        if field not in data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required field: {field}",
            )

    # Validate field types
    properties = schema.get("properties", {})
    for field_name, field_value in data.items():
        if field_name in properties:
            expected_type = properties[field_name].get("type")
            if expected_type:
                # Simple type checking
                type_map = {
                    "string": str,
                    "number": (int, float),
                    "integer": int,
                    "boolean": bool,
                    "array": list,
                    "object": dict,
                }
                if expected_type in type_map:
                    if not isinstance(field_value, type_map[expected_type]):
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Field '{field_name}' must be {expected_type}",
                        )

    return data
