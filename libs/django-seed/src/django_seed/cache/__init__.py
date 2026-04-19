"""
Cache module for Django Seed package.

This module provides caching functionality with support for multiple backends.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Optional as Opt
import time
import json
import pickle
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """Get a value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass

    @abstractmethod
    def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern."""
        pass


class InMemoryCache(CacheBackend):
    """In-memory cache backend."""

    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def get(self, key: str) -> Any:
        """Get a value from cache."""
        if key not in self._cache:
            return None

        # Check if expired
        if key in self._expiry and self._expiry[key] < time.time():
            del self._cache[key]
            del self._expiry[key]
            return None

        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        self._cache[key] = value
        if ttl:
            self._expiry[key] = time.time() + ttl
        return True

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if key not in self._cache:
            return False

        # Check expiry
        if key in self._expiry and self._expiry[key] < time.time():
            del self._cache[key]
            del self._expiry[key]
            return False

        return True

    def clear(self) -> bool:
        """Clear all cache entries."""
        self._cache.clear()
        self._expiry.clear()
        return True

    def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern."""
        # Simple pattern matching for in-memory cache
        import fnmatch
        return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]


class CacheManager:
    """Cache manager for Django Seed."""

    def __init__(self, backend: CacheBackend = None):
        self.backend = backend or InMemoryCache()
        self.hit_count = 0
        self.miss_count = 0
        self.error_count = 0

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from cache."""
        try:
            value = self.backend.get(key)
            if value is not None:
                self.hit_count += 1
                return value
            else:
                self.miss_count += 1
                return default
        except Exception as e:
            self.error_count += 1
            logger.error(f"Cache get error: {e}")
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        try:
            return self.backend.set(key, value, ttl)
        except Exception as e:
            self.error_count += 1
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        try:
            return self.backend.delete(key)
        except Exception as e:
            self.error_count += 1
            logger.error(f"Cache delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            return self.backend.exists(key)
        except Exception as e:
            self.error_count += 1
            logger.error(f"Cache exists error: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            return self.backend.clear()
        except Exception as e:
            self.error_count += 1
            logger.error(f"Cache clear error: {e}")
            return False

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            'hits': self.hit_count,
            'misses': self.miss_count,
            'errors': self.error_count,
            'hit_ratio': self.hit_count / (self.hit_count + self.miss_count)
                if (self.hit_count + self.miss_count) > 0 else 0
        }

    def get_or_set(self, key: str, default_factory, ttl: Optional[int] = None) -> Any:
        """Get a value from cache, or set it if not present."""
        value = self.get(key)
        if value is not None:
            return value

        # Value not in cache, compute it
        value = default_factory()
        self.set(key, value, ttl)
        return value


# Default cache instance
cache = CacheManager()

# Convenience functions
def get_cache() -> CacheManager:
    """Get the default cache instance."""
    return cache

def cache_result(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cache = get_cache()
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

            # Not in cache, compute and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator
