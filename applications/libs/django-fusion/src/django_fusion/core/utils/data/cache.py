"""
Cache utilities.

Canonical import: from django_fusion.core.utils.cache import generate_cache_key, cache_get_or_set, invalidate_cache_pattern, is_redis_available
"""

import hashlib
import json
from typing import Any, Callable

from django.core.cache import cache


def generate_cache_key(
    prefix: str,
    *args,
    **kwargs,
) -> str:
    """
    Generate deterministic cache key.
    """
    key_parts = [prefix]

    # Add positional arguments
    for arg in args:
        key_parts.append(str(arg))

    # Add keyword arguments
    if kwargs:
        sorted_kwargs = json.dumps(kwargs, sort_keys=True)
        kwargs_hash = hashlib.md5(sorted_kwargs.encode()).hexdigest()[:8]
        key_parts.append(kwargs_hash)

    return ":".join(key_parts)


def cache_get_or_set(
    key: str,
    default: Callable[[], Any],
    timeout: int = 3600,
) -> Any:
    """
    Get from cache or set using default function.
    """
    value = cache.get(key)

    if value is None:
        value = default()
        cache.set(key, value, timeout)

    return value


def invalidate_cache_pattern(pattern: str) -> bool:
    """
    Invalidate cache keys matching pattern (Redis only).
    """
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        keys = conn.keys(pattern)
        if keys:
            conn.delete(*keys)
        return True
    except:
        return False


def is_redis_available() -> bool:
    """Check if Redis is available."""
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        conn.ping()
        return True
    except:
        return False
