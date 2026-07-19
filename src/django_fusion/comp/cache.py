"""Component mapping cache with Redis support.

Provides Redis-backed caching for component registry mappings when enabled
via Django's CACHES configuration. Falls back to in-memory caching when
Redis is unavailable or disabled.

Features:
    - Automatic Redis detection from Django settings
    - Graceful fallback to in-memory cache
    - Component name → path mapping
    - Template path → components usage mapping
    - Render history snapshots
    - Cache invalidation and warming
    - Metrics and monitoring

Configuration:
    # Enable Redis caching in settings.py:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'cypercloud',
            'TIMEOUT': 3600,
        }
    }

    # Or use Dynaconf:
    CACHES:
      default:
        backend: django.core.cache.backends.redis.RedisCache
        location: "{{ env 'REDIS_URL' or 'redis://localhost:6379/1' }}"

Usage:
    from django_fusion.comp.cache import ComponentMapCache, get_component_map_cache

    # Get or create cache instance
    cache = get_component_map_cache()

    # Store component mapping
    cache.set_component("auth_buttons", "partials/auth_buttons.html")

    # Retrieve component mapping
    path = cache.get_component("auth_buttons")

    # Batch operations
    cache.set_components({
        "card": "components/card.html",
        "modal": "components/modal.html",
    })

    # Template usage tracking
    cache.add_template_usage("components/card.html", ["home", "dashboard"])
    usage = cache.get_template_usage("components/card.html")

    # Render history
    cache.record_render("auth_buttons")
    history = cache.get_render_history()

    # Cache management
    cache.clear_all()
    cache.warmup_from_registry(components_registry)
    cache.get_stats()
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional
from functools import wraps

from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

logger = logging.getLogger(__name__)


class ComponentMapCache:
    """Redis-backed cache for component registry mappings.
    
    Provides high-performance caching of component name → path mappings,
    template usage patterns, and render history when Redis is available.
    Falls back gracefully to transient in-memory storage when Redis is
    unavailable or disabled.
    """
    
    # Cache key prefixes
    COMPONENT_KEY_PREFIX = "comp:component:"
    TEMPLATE_USAGE_KEY_PREFIX = "comp:template_usage:"
    RENDER_HISTORY_KEY = "comp:render_history"
    STATS_KEY = "comp:stats"
    MAPPING_KEY = "comp:mapping"
    
    # Batch operations key
    BATCH_KEY = "comp:batch"
    
    # Default timeouts (in seconds)
    DEFAULT_COMPONENT_TIMEOUT = 3600 * 24  # 24 hours
    DEFAULT_HISTORY_TIMEOUT = 3600  # 1 hour
    DEFAULT_STATS_TIMEOUT = 300  # 5 minutes
    
    def __init__(self, timeout: int | None = None, enabled: bool | None = None):
        """Initialize component map cache.
        
        Parameters
        ----------
        timeout : int, optional
            Cache timeout in seconds. Defaults to DEFAULT_COMPONENT_TIMEOUT.
            Use None for no expiration.
        enabled : bool, optional
            Force enable/disable caching. Auto-detects from settings if None.
        """
        self.timeout = timeout or self.DEFAULT_COMPONENT_TIMEOUT
        self._enabled = enabled if enabled is not None else self._detect_redis()
        self._in_memory_cache: dict[str, Any] = {}
        
        if self._enabled:
            logger.info("✅ Component map cache: Redis enabled")
        else:
            logger.info("⚠️  Component map cache: Using in-memory fallback")
    
    @staticmethod
    def _detect_redis() -> bool:
        """Detect if Redis is available and configured.
        
        Returns
        -------
        bool
            True if Redis cache is configured and available, False otherwise.
        """
        try:
            cache_config = getattr(settings, 'CACHES', {}).get('default', {})
            backend = cache_config.get('BACKEND', '')
            
            # Check if Redis backend is configured
            is_redis = 'redis' in backend.lower()
            
            if not is_redis:
                return False
            
            # Try a quick ping to verify connection
            cache.set("__ping__", 1, 1)
            result = cache.get("__ping__")
            cache.delete("__ping__")
            
            return result == 1
        except Exception as e:
            logger.debug(f"Redis detection failed: {e}")
            return False
    
    @property
    def is_redis_enabled(self) -> bool:
        """Check if Redis caching is enabled and available."""
        return self._enabled
    
    def _get_cache_backend(self) -> Any:
        """Get appropriate cache backend (Redis or in-memory)."""
        if self._enabled:
            return cache
        return None  # Use in-memory dict
    
    def set_component(self, name: str, path: str, timeout: int | None = None) -> None:
        """Store a component name → path mapping.
        
        Parameters
        ----------
        name : str
            Component name (e.g., "auth_buttons")
        path : str
            Component template path (e.g., "partials/auth_buttons.html")
        timeout : int, optional
            Custom timeout in seconds. Uses default if None.
        """
        key = f"{self.COMPONENT_KEY_PREFIX}{name}"
        timeout = timeout or self.timeout
        
        if self._enabled:
            cache.set(key, path, timeout)
            logger.debug(f"Cached component mapping: {name} → {path}")
        else:
            self._in_memory_cache[key] = path
    
    def get_component(self, name: str) -> str | None:
        """Retrieve a component template path by name.
        
        Parameters
        ----------
        name : str
            Component name
        
        Returns
        -------
        str | None
            Template path if found, None otherwise.
        """
        key = f"{self.COMPONENT_KEY_PREFIX}{name}"
        
        if self._enabled:
            result = cache.get(key)
        else:
            result = self._in_memory_cache.get(key)
        
        if result:
            logger.debug(f"Cache hit for component: {name}")
        else:
            logger.debug(f"Cache miss for component: {name}")
        
        return result
    
    def set_components(self, mapping: dict[str, str], timeout: int | None = None) -> None:
        """Bulk store component mappings.
        
        Parameters
        ----------
        mapping : dict[str, str]
            Component name → path mappings
        timeout : int, optional
            Custom timeout in seconds
        """
        timeout = timeout or self.timeout
        
        for name, path in mapping.items():
            self.set_component(name, path, timeout)
        
        logger.info(f"Cached {len(mapping)} component mappings")
    
    def get_components(self, names: list[str]) -> dict[str, str]:
        """Retrieve multiple component mappings.
        
        Parameters
        ----------
        names : list[str]
            Component names
        
        Returns
        -------
        dict[str, str]
            Available mappings (missing components not included)
        """
        result = {}
        for name in names:
            path = self.get_component(name)
            if path:
                result[name] = path
        return result
    
    def add_template_usage(
        self,
        template_path: str,
        component_names: list[str] | set[str],
        timeout: int | None = None
    ) -> None:
        """Record which components are used in a template.
        
        Parameters
        ----------
        template_path : str
            Template file path
        component_names : list[str] | set[str]
            Component names used in template
        timeout : int, optional
            Custom timeout in seconds
        """
        key = f"{self.TEMPLATE_USAGE_KEY_PREFIX}{template_path}"
        timeout = timeout or self.timeout
        
        # Convert set to list for JSON serialization
        names_list = sorted(list(component_names))
        
        if self._enabled:
            cache.set(key, json.dumps(names_list), timeout)
        else:
            self._in_memory_cache[key] = names_list
        
        logger.debug(f"Recorded {len(names_list)} components for template: {template_path}")
    
    def get_template_usage(self, template_path: str) -> set[str]:
        """Get components used in a template.
        
        Parameters
        ----------
        template_path : str
            Template file path
        
        Returns
        -------
        set[str]
            Component names used in template
        """
        key = f"{self.TEMPLATE_USAGE_KEY_PREFIX}{template_path}"
        
        if self._enabled:
            result = cache.get(key)
            if result:
                return set(json.loads(result))
        else:
            result = self._in_memory_cache.get(key)
            if result:
                return set(result) if isinstance(result, list) else result
        
        return set()
    
    def record_render(self, component_name: str) -> None:
        """Record a component render event.
        
        Parameters
        ----------
        component_name : str
            Component that was rendered
        """
        if not self._enabled:
            return
        
        try:
            # Get current history
            history = cache.get(self.RENDER_HISTORY_KEY) or []
            if isinstance(history, str):
                history = json.loads(history)
            
            # Add new render (keep last 1000)
            history.append({
                "component": component_name,
                "timestamp": self._get_timestamp(),
            })
            history = history[-1000:]
            
            # Store back
            cache.set(
                self.RENDER_HISTORY_KEY,
                json.dumps(history),
                self.DEFAULT_HISTORY_TIMEOUT
            )
        except Exception as e:
            logger.debug(f"Failed to record render: {e}")
    
    def get_render_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent render history.
        
        Parameters
        ----------
        limit : int
            Maximum number of entries to return
        
        Returns
        -------
        list[dict]
            Recent render events
        """
        if not self._enabled:
            return []
        
        try:
            history = cache.get(self.RENDER_HISTORY_KEY) or []
            if isinstance(history, str):
                history = json.loads(history)
            return history[-limit:]
        except Exception as e:
            logger.debug(f"Failed to get render history: {e}")
            return []
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics and metrics.
        
        Returns
        -------
        dict
            Cache statistics (keys count, Redis enabled, etc.)
        """
        stats = {
            "redis_enabled": self._enabled,
            "timeout": self.timeout,
        }
        
        if self._enabled:
            try:
                # Get cache info from Redis
                info = cache.get(self.STATS_KEY) or {}
                if isinstance(info, str):
                    info = json.loads(info)
                stats.update(info)
            except Exception as e:
                logger.debug(f"Failed to get cache stats: {e}")
                stats["error"] = str(e)
        else:
            stats["in_memory_keys"] = len(self._in_memory_cache)
        
        return stats
    
    def clear_all(self) -> None:
        """Clear all component cache entries."""
        if self._enabled:
            try:
                # Get all keys and delete them
                cache.delete_many([
                    self.RENDER_HISTORY_KEY,
                    self.STATS_KEY,
                    self.MAPPING_KEY,
                    self.BATCH_KEY,
                ])
                logger.info("Cleared all component cache entries (Redis)")
            except Exception as e:
                logger.warning(f"Failed to clear Redis cache: {e}")
        else:
            self._in_memory_cache.clear()
            logger.info("Cleared all component cache entries (in-memory)")
    
    def warmup_from_registry(self, registry: Any) -> int:
        """Pre-populate cache from component registry.
        
        Parameters
        ----------
        registry : ComponentRegistry
            Registry instance to warm up from
        
        Returns
        -------
        int
            Number of components cached
        """
        count = 0
        try:
            # Cache all components from registry
            for name, component in registry._components.items():
                try:
                    path = component.path
                    self.set_component(name, path)
                    count += 1
                except Exception as e:
                    logger.debug(f"Failed to cache component {name}: {e}")
            
            logger.info(f"Warmed up cache with {count} components")
        except Exception as e:
            logger.error(f"Failed to warmup cache: {e}")
        
        return count
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def invalidate(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern.
        
        Parameters
        ----------
        pattern : str
            Cache key pattern (e.g., "comp:component:*")
        
        Returns
        -------
        int
            Number of keys invalidated
        """
        if not self._enabled:
            # For in-memory, just remove matching keys
            keys_to_delete = [k for k in self._in_memory_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._in_memory_cache[key]
            return len(keys_to_delete)
        
        try:
            # Redis pattern deletion
            client = cache._cache
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
            return len(keys) if keys else 0
        except Exception as e:
            logger.warning(f"Failed to invalidate pattern {pattern}: {e}")
            return 0


# Singleton instance
_component_map_cache: ComponentMapCache | None = None


def get_component_map_cache() -> ComponentMapCache:
    """Get or create the singleton component map cache instance.
    
    Returns
    -------
    ComponentMapCache
        Global component map cache instance
    """
    global _component_map_cache
    
    if _component_map_cache is None:
        _component_map_cache = ComponentMapCache()
    
    return _component_map_cache


def cache_component(timeout: int | None = None):
    """Decorator to cache component retrieval.
    
    Parameters
    ----------
    timeout : int, optional
        Cache timeout in seconds
    
    Example
    -------
    >>> @cache_component(timeout=3600)
    ... def get_component_details(name):
    ...     return expensive_operation(name)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(name: str, *args, **kwargs):
            cache = get_component_map_cache()
            
            # Try to get from cache
            result = cache.get_component(name)
            if result:
                return result
            
            # Not in cache, call function
            result = func(name, *args, **kwargs)
            
            # Cache result if valid
            if result:
                cache.set_component(name, result, timeout)
            
            return result
        
        return wrapper
    return decorator


__all__ = [
    "ComponentMapCache",
    "get_component_map_cache",
    "cache_component",
]
