"""
Validation utility functions for django-fusion.

Provides email and data validation utilities.
Canonical merge of django_fusion.services.validators and django_grep.utils.validators.
"""

import re
from typing import List


def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid, False otherwise

    Example:
        >>> validate_email_format("user@example.com")
        True
        >>> validate_email_format("invalid-email")
        False
    """
    if not email:
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_email_domain(email: str, allowed_domains: List[str]) -> bool:
    """
    Validate email domain against whitelist.

    Args:
        email: Email address to validate
        allowed_domains: List of allowed domain names

    Returns:
        True if email domain is in allowed list, False otherwise

    Example:
        >>> validate_email_domain("user@example.com", ["example.com", "test.com"])
        True
        >>> validate_email_domain("user@other.com", ["example.com"])
        False
    """
    if not email or "@" not in email:
        return False

    domain = email.split("@")[1].lower()
    return domain in [d.lower() for d in allowed_domains]


def validate_phone_number(phone: str, country_code: str = None) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate
        country_code: Optional country code (e.g., 'US', 'UK')

    Returns:
        True if phone number format is valid, False otherwise

    Example:
        >>> validate_phone_number("+1-555-123-4567")
        True
        >>> validate_phone_number("invalid")
        False
    """
    if not phone:
        return False

    # Remove common separators
    cleaned = re.sub(r"[\s\-\(\)\.]", "", phone)

    # Check if it contains only digits and optional + at start
    pattern = r"^\+?\d{10,15}$"
    return bool(re.match(pattern, cleaned))


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if URL format is valid, False otherwise

    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("not-a-url")
        False
    """
    if not url:
        return False

    pattern = r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$"
    return bool(re.match(pattern, url))


def validate_username(username: str, min_length: int = 3, max_length: int = 30) -> bool:
    """
    Validate username format.

    Args:
        username: Username to validate
        min_length: Minimum length (default: 3)
        max_length: Maximum length (default: 30)

    Returns:
        True if username format is valid, False otherwise

    Example:
        >>> validate_username("john_doe")
        True
        >>> validate_username("ab")
        False
    """
    if not username:
        return False

    if len(username) < min_length or len(username) > max_length:
        return False

    # Allow alphanumeric, underscore, and hyphen
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, username))
