"""Skeleton manifest cache warming.

Provides a thin Redis-backed cache layer for :class:`SkeletonResolver`
so repeated page renders don't re-scan the filesystem.

Requires ``django-redis`` or a configured ``CACHES['default']`` backend.

Usage::

    from django_fusion.fragments.skeleton.cache import (
        get_cached_skeleton,
        warm_skeleton_cache,
    )

    # Per-request: fetch from cache or resolve + store
    entries = get_cached_skeleton("pages/home.html")

    # At startup / deploy: pre-warm all known pages
    warm_skeleton_cache(["pages/home.html", "blog/index.html"])
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "fusion:skeleton"
DEFAULT_TTL = 3600  # 1 hour


def _cache_key(page_path: str) -> str:
    """Produce a stable cache key for a page path."""
    normalised = page_path.lstrip("/")
    hashed = hashlib.sha256(normalised.encode()).hexdigest()[:16]
    return f"{CACHE_KEY_PREFIX}:{hashed}"


def _cache_enabled() -> bool:
    """Check that the cache backend is available and not the dummy backend."""
    try:
        cache.get("__fusion_skeleton_ping__")
        return True
    except Exception:
        return False


def get_cached_skeleton(page_path: str) -> list[dict[str, Any]] | None:
    """Return cached skeleton entries for *page_path*, or ``None``.

    The caller should fall back to :meth:`SkeletonResolver.resolve_page_skeleton`
    when this returns ``None``.
    """
    if not _cache_enabled():
        return None

    key = _cache_key(page_path)
    try:
        raw = cache.get(key)
        if raw is None:
            return None
        if isinstance(raw, str):
            return json.loads(raw)
        return raw
    except Exception:
        logger.debug("Cache miss for %s", page_path, exc_info=True)
        return None


def set_cached_skeleton(
    page_path: str,
    entries: list[dict[str, Any]],
    ttl: int = DEFAULT_TTL,
) -> None:
    """Store skeleton entries in the cache."""
    if not _cache_enabled():
        return

    key = _cache_key(page_path)
    try:
        cache.set(key, json.dumps(entries, default=str), timeout=ttl)
        logger.debug("Cached skeleton for %s (ttl=%ds)", page_path, ttl)
    except Exception:
        logger.warning("Failed to cache skeleton for %s", page_path, exc_info=True)


def warm_skeleton_cache(
    page_paths: list[str],
    ttl: int = DEFAULT_TTL,
) -> dict[str, int]:
    """Pre-compute and cache skeleton manifests for *page_paths*.

    Returns a dict of ``{page_path: entry_count}`` for successfully
    cached pages.
    """
    from django_fusion.fragments.skeleton.resolver import SkeletonResolver

    if not _cache_enabled():
        logger.warning("Cache backend not available — skipping warm-up.")
        return {}

    resolver = SkeletonResolver()
    results: dict[str, int] = {}

    for page_path in page_paths:
        entries = resolver.resolve_page_skeleton(page_path)
        if entries:
            serialized = [
                {
                    "variant": e.variant,
                    "component": e.component_path,
                    "order": e.order,
                    "props": e.props,
                    "skeleton_config": e.skeleton_config,
                }
                for e in entries
            ]
            set_cached_skeleton(page_path, serialized, ttl=ttl)
            results[page_path] = len(entries)
        else:
            logger.debug("No components found for %s — not cached.", page_path)

    return results


def invalidate_skeleton_cache(page_path: str | None = None) -> int:
    """Delete cached skeleton entries.

    If *page_path* is ``None``, deletes **all** skeleton cache entries
    (use after a template change or deployment).

    Returns the number of keys deleted.
    """
    if not _cache_enabled():
        return 0

    if page_path:
        key = _cache_key(page_path)
        deleted = 1 if cache.delete(key) else 0
        logger.debug("Invalidated skeleton cache for %s", page_path)
        return deleted

    # Delete all keys matching the prefix.  This is backend-dependent;
    # Redis supports ``delete_pattern`` (django-redis) while memcached
    # does not.  We try the pattern-delete first, then fall back to a
    # key iteration approach.
    try:
        # django-redis provides delete_pattern
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(f"{CACHE_KEY_PREFIX}:*")
            logger.info("Invalidated all skeleton cache entries (pattern delete).")
            return -1  # unknown count
    except Exception:
        pass

    # Fallback: if we have access to the raw client
    try:
        client = getattr(cache, "client", None)
        if client is not None:
            # Redis client
            raw_client = getattr(client, "get_client", lambda: client)()
            keys = raw_client.keys(f"{CACHE_KEY_PREFIX}:*")
            if keys:
                raw_client.delete(*keys)
                logger.info(
                    "Invalidated %d skeleton cache entries.", len(keys)
                )
                return len(keys)
    except Exception:
        logger.warning("Could not perform bulk cache invalidation.", exc_info=True)

    return 0
