# managers/base_managers.py
"""
Unified Base Managers with full functionality and optional caching.

Canonical imports::
    from django_fusion.management.managers.base import BaseManager
    from django_fusion.management.managers.base import CacheSupportMixin
    from django_fusion.management.managers.base import CachedManager
    from django_fusion.management.managers.base import UncachedManager
    from django_fusion.management.managers.base import cached_method
"""

import hashlib
import json
import logging
from functools import wraps
from typing import Any, Dict, List, Optional

from django.core.cache import cache
from django.db import models
from django.db.models import QuerySet

logger = logging.getLogger(__name__)


# ==================================================================
# =======================  BASE MANAGER  ===========================
# ==================================================================

class BaseManager(models.Manager):
    """
    Fully unified manager combining:
    - BaseManager
    - EnhancedManager

    Canonical import: from django_fusion.management.managers.base import BaseManager
    """

    # -----------------------------------------------------
    # BASIC GETTERS
    # -----------------------------------------------------
    def get_by_field(
        self,
        value: Any,
        field: str = None,
        raise_exception: bool = False,
        **kwargs,
    ) -> Optional[models.Model]:

        if field:
            try:
                return self.get(**{field: value}, **kwargs)
            except self.model.DoesNotExist:
                if raise_exception:
                    raise
                return None

        for fname in ["uuid", "id", "slug", "email", "code"]:
            if hasattr(self.model, fname):
                try:
                    return self.get(**{fname: value}, **kwargs)
                except (self.model.DoesNotExist, ValueError):
                    continue

        if raise_exception:
            raise self.model.DoesNotExist(f"No object found for: {value}")

        return None

    # -----------------------------------------------------
    # FILTER UTILITIES
    # -----------------------------------------------------
    def filter_by(
        self,
        filters: Dict[str, Any],
        exclude: Dict[str, Any] = None,
        ordering: List[str] = None,
        **kwargs,
    ) -> QuerySet:

        qs = self.filter(**filters)

        if exclude:
            qs = qs.exclude(**exclude)

        if ordering:
            qs = qs.order_by(*ordering)

        return qs

    # -----------------------------------------------------
    # BULK UPSERT
    # -----------------------------------------------------
    def bulk_create_or_update(
        self,
        objects_data: List[Dict[str, Any]],
        update_fields: List[str] = None,
        match_fields: List[str] = None,
        batch_size: int = 1000,
    ) -> List[models.Model]:

        pass

        match_fields = match_fields or ["id"]
        results = []

        for data in objects_data:
            try:
                match_filter = {
                    f: data[f] for f in match_fields
                    if f in data and data[f] is not None
                }

                if match_filter:
                    try:
                        obj = self.get(**match_filter)
                        if update_fields:
                            for f in update_fields:
                                if f in data:
                                    setattr(obj, f, data[f])
                        else:
                            for f, v in data.items():
                                setattr(obj, f, v)
                        obj.save()
                        results.append(obj)
                        continue
                    except self.model.DoesNotExist:
                        pass

                obj = self.create(**data)
                results.append(obj)

            except Exception as e:
                logger.error(f"Bulk upsert error {e} | Data: {data}")
                raise

        return results

    # -----------------------------------------------------
    # SAFE GET OR CREATE
    # -----------------------------------------------------
    def get_or_create_safe(self, defaults=None, **kwargs):
        try:
            return self.get_or_create(defaults=defaults, **kwargs)
        except (self.model.MultipleObjectsReturned, Exception):
            try:
                return self.get(**kwargs), False
            except self.model.DoesNotExist:
                raise

    # -----------------------------------------------------
    # SHORTCUTS
    # -----------------------------------------------------
    def exists_by(self, **kwargs) -> bool:
        return self.filter(**kwargs).exists()

    def count_by(self, **kwargs) -> int:
        return self.filter(**kwargs).count()

    def latest_by(self, field="created_at", **kwargs):
        try:
            return self.filter(**kwargs).latest(field)
        except self.model.DoesNotExist:
            return None

    # -----------------------------------------------------
    # RELATED OBJECT LOADING
    # -----------------------------------------------------
    def get_with_related(
        self,
        identifier: Any,
        field: str = None,
        select_related: List[str] = None,
        prefetch_related: List[str] = None,
        **kwargs,
    ):
        qs = self.all()
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)

        if field:
            return qs.filter(**{field: identifier}).first()

        for fname in ["uuid", "id", "slug", "email"]:
            if hasattr(self.model, fname):
                obj = qs.filter(**{fname: identifier}).first()
                if obj:
                    return obj

        return None

    # -----------------------------------------------------
    # ANNOTATE & AGGREGATE
    # -----------------------------------------------------
    def annotate_with(self, annotations, filters=None, ordering=None, **kwargs):
        qs = self.all()
        if annotations:
            qs = qs.annotate(**annotations)
        if filters:
            qs = qs.filter(**filters)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def aggregate_by(self, aggregates, filters=None, group_by=None, **kwargs):
        qs = self.all()
        if filters:
            qs = qs.filter(**filters)
        if group_by:
            return list(qs.values(*group_by).annotate(**aggregates))
        return qs.aggregate(**aggregates)

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------
    def search(self, query, search_fields, filters=None, ordering=None, limit=None):
        from django.db.models import Q

        qs = self.all()
        if query:
            q = Q()
            for f in search_fields:
                q |= Q(**{f"{f}__icontains": query})
            qs = qs.filter(q)
        if filters:
            qs = qs.filter(**filters)
        if ordering:
            qs = qs.order_by(*ordering)
        if limit:
            qs = qs[:limit]
        return qs


# ==================================================================
# =====================  CACHING MIXIN  ============================
# ==================================================================

class CacheSupportMixin:
    """
    Adds universal caching to BaseManager.

    Canonical import: from django_fusion.management.managers.base import CacheSupportMixin
    """

    CACHE_PREFIX = "cache_manager"
    DEFAULT_CACHE_TIMEOUT = 3600
    # Public compatibility settings used by token-aware and user managers.
    enable_cache = True
    cache_timeout = DEFAULT_CACHE_TIMEOUT

    @staticmethod
    def is_redis_available() -> bool:
        try:
            from django_redis import get_redis_connection
            conn = get_redis_connection("default")
            conn.ping()
            return True
        except:
            return False

    # ------------------------------ KEY GENERATION
    def _generate_cache_key(self, cache_type, identifier=None, params=None):
        model_name = self.model.__name__.lower()
        parts = [self.CACHE_PREFIX, model_name, cache_type]

        if identifier is not None:
            parts.append(str(identifier))

        if params:
            hashed = hashlib.md5(
                json.dumps(params, sort_keys=True).encode()
            ).hexdigest()[:12]
            parts.append(hashed)

        return ":".join(parts)

    # ------------------------------ GET CACHED OBJECT
    def get_cached(
        self,
        identifier: Any,
        field: str = None,
        include_related=False,
        force_refresh=False,
        **kwargs,
    ):
        if force_refresh:
            return super().get_by_field(identifier, field, **kwargs)

        params = {"field": field, "include_related": include_related, **kwargs}
        cache_key = self._generate_cache_key("get", identifier, params)

        cached = cache.get(cache_key)
        if cached:
            try:
                return self._deserialize_from_cache(cached)
            except:
                cache.delete(cache_key)

        obj = super().get_by_field(identifier, field, **kwargs)
        if obj:
            cache_data = self._serialize_for_cache(obj, include_related)
            cache.set(cache_key, cache_data, self.DEFAULT_CACHE_TIMEOUT)
        return obj

    # ------------------------------ GET CACHED FILTER
    def filter_cached(
        self,
        filters: Dict[str, Any],
        ordering: List[str] = None,
        limit: int = None,
        offset: int = 0,
        include_related: bool = False,
        force_refresh: bool = False,
        **kwargs,
    ):
        if force_refresh:
            qs = super().filter_by(filters, ordering=ordering)
            return qs[offset:offset + limit] if limit else qs

        params = {
            "filters": filters,
            "ordering": ordering,
            "limit": limit,
            "offset": offset,
            "include_related": include_related,
        }

        cache_key = self._generate_cache_key("filter", None, params)
        cached_ids = cache.get(cache_key)

        if cached_ids:
            return self.filter(pk__in=cached_ids)

        qs = super().filter_by(filters, ordering=ordering)
        sliced = qs[offset:offset + limit] if limit else qs

        ids = list(sliced.values_list("id", flat=True))
        cache.set(cache_key, ids, self.DEFAULT_CACHE_TIMEOUT)

        return self.filter(pk__in=ids)

    # ------------------------------ SERIALIZATION
    def _serialize_for_cache(self, obj, include_related=False):
        from django.forms.models import model_to_dict

        data = {
            "_id": obj.pk,
            "data": model_to_dict(obj),
        }

        if include_related:
            data["_related"] = self._get_related_data(obj)

        return data

    def _deserialize_from_cache(self, cache_data):
        try:
            return self.get(pk=cache_data["_id"])
        except self.model.DoesNotExist:
            obj = self.model(**cache_data["data"])
            obj.pk = cache_data["_id"]
            return obj

    def _get_related_data(self, obj):
        result = {}
        for field in ["user", "created_by", "updated_by", "owner"]:
            if hasattr(obj, field):
                try:
                    rel = getattr(obj, field)
                    if rel:
                        result[field] = {"id": rel.pk, "str": str(rel)}
                except:
                    pass
        return result


# ==================================================================
# =====================   cached_method   ===========================
# ==================================================================

def cached_method(timeout: int = 3600):
    """
    Decorator for caching any manager method result.

    Works only if the manager has `.get_cached()`.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):

            if not hasattr(self, "get_cached"):
                return func(self, *args, **kwargs)

            raw_key = {
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs,
            }

            cache_key = (
                f"method:"
                f"{self.__class__.__name__}:"
                f"{func.__name__}:"
                f"{hashlib.md5(json.dumps(raw_key, sort_keys=True, default=str).encode()).hexdigest()}"
            )

            def getter():
                return func(self, *args, **kwargs)

            # Use manager's caching engine
            return self.get_cached(
                identifier=None,
                field=None,
                force_refresh=False,
                cache_key_override=cache_key if hasattr(self, "get_cached") else None,
            ) if False else _method_cache(self, cache_key, getter, timeout)

        return wrapper

    return decorator


def _method_cache(manager, cache_key, getter, timeout):
    """Internal reuse to keep code clean."""
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = getter()
    cache.set(cache_key, result, timeout)
    return result


# ==================================================================
# ======================= FINAL MANAGERS ===========================
# ==================================================================

class CachedManager(CacheSupportMixin, BaseManager):
    """
    Full manager WITH caching.

    Canonical import: from django_fusion.management.managers.base import CachedManager
    """


class UncachedManager(BaseManager):
    """
    Full manager WITHOUT caching.

    Canonical import: from django_fusion.management.managers.base import UncachedManager
    """
