"""
Validation utilities.

Canonical import: from django_fusion.core.utils.validation import validate_email, validate_phone, validate_password, validate_uuid
"""

import re
import uuid as uuid_lib
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number."""
    # Simple validation - adjust for your needs
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, None


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID string."""
    try:
        uuid_lib.UUID(uuid_string)
        return True
    except ValueError:
        return False
