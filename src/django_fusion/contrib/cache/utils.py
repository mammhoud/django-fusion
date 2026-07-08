"""
Cache utilities for django_fusion.

This module provides utility functions for cache management including
cache key generation, cache invalidation patterns, and Redis availability checking.

Functions:
    generate_cache_key: Generate a unique cache key for an object.
    cache_get_or_set: Get value from cache or compute and store it.
    invalidate_cache_pattern: Invalidate all cache entries matching a pattern.
    is_redis_available: Check if Redis is available and responding.

Usage::

    from django_fusion.contrib.cache.utils import cache_get_or_set, generate_cache_key
"""

