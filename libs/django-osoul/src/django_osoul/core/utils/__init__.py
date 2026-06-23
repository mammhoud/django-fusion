"""
Django Forge utilities module.

Organized by category:
- data: Data utilities (cache, datetime, responses)
- security: Security utilities (token, validation, validators)
- formatting: Formatting utilities (text, decorators)

Provides text, datetime, response, decorator, cache, token, and validation utilities.
"""

# Data utilities
# Cache utilities (from data module)
from .data import (
    cache_get_or_set,
    created_response,
    error_response,
    forbidden_response,
    format_date_range,
    format_duration,
    format_relative_time,
    generate_cache_key,
    get_next_business_day,
    get_time_until,
    invalidate_cache_pattern,
    is_business_day,
    is_redis_available,
    not_found_response,
    server_error_response,
    success_response,
    unauthorized_response,
    validation_error_response,
)

# Formatting utilities
from .formatting import (
    cache_result,
    capitalize_words,
    generate_unique_slug,
    log_execution,
    retry_on_exception,
    slugify_unique,
    strip_html_tags,
    truncate_chars,
    truncate_words,
)

# Security utilities
from .security import (
    decode_token,
    generate_token,
    validate_email,
    validate_password,
    validate_phone,
    validate_token,
    validate_uuid,
)

__all__ = [
    # Text utilities
    "slugify_unique",
    "generate_unique_slug",
    "truncate_words",
    "truncate_chars",
    "strip_html_tags",
    "capitalize_words",
    # DateTime utilities
    "format_relative_time",
    "format_duration",
    "format_date_range",
    "get_time_until",
    "is_business_day",
    "get_next_business_day",
    # Response utilities
    "success_response",
    "error_response",
    "created_response",
    "not_found_response",
    "unauthorized_response",
    "forbidden_response",
    "server_error_response",
    "validation_error_response",
    # Decorators
    "cache_result",
    "retry_on_exception",
    "log_execution",
    # Cache utilities
    "generate_cache_key",
    "cache_get_or_set",
    "invalidate_cache_pattern",
    "is_redis_available",
    # Token utilities
    "generate_token",
    "validate_token",
    "decode_token",
    # Validation utilities
    "validate_email",
    "validate_phone",
    "validate_password",
    "validate_uuid",
]
