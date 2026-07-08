"""Unified cache managers for Django models."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from django.conf import settings
from django.core.cache import caches
from django.db import models


def _cache(alias: str | None = None):
    return caches[alias or getattr(settings, "Django_OSOUL_CACHE_ALIAS", "default")]

class CachedManager(models.Manager):
    cache_alias = None
    cache_ttl = 300
    cache_prefix = "django_fusion"
    def cache_key(self, method: str, *args: Any, **kwargs: Any) -> str:
        payload = json.dumps([args, kwargs], sort_keys=True, default=str)
        digest = hashlib.sha256(payload.encode()).hexdigest()
        model = self.model._meta.label_lower
        return f"{self.cache_prefix}:{model}:{method}:{digest}"
    def cached(self, method: str, producer, *args: Any, ttl: int | None = None, **kwargs: Any):
        key = self.cache_key(method, *args, **kwargs)
        cache = _cache(self.cache_alias)
        value = cache.get(key)
        if value is None:
            value = producer()
            cache.set(key, value, ttl if ttl is not None else self.cache_ttl)
        return value
    def cached_get(self, *args: Any, **kwargs: Any):
        return self.cached("get", lambda: self.get(*args, **kwargs), *args, **kwargs)
    def cached_filter(self, *args: Any, **kwargs: Any):
        return self.cached("filter", lambda: list(self.filter(*args, **kwargs)), *args, **kwargs)

class CachedModelManager(CachedManager):
    """Base class for model managers using Redis/DB cache backends via Django caches."""
