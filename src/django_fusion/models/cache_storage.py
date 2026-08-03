"""CachingStorage — generic caching storage for Django/Wagtail models."""
from __future__ import annotations
import hashlib
import json
import logging
import threading
from datetime import datetime
from typing import Any

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

logger = logging.getLogger(__name__)


class CachingStorage:
    """Generic caching storage class for Django and Wagtail models.

    Migrated from shared/contrib/core/cache.py.
    """

    DEFAULT_TIMEOUT = 60 * 60 * 24
    CACHE_PREFIX = "cached_data"
    MODEL_KEYS_SUFFIX = "model_keys"
    #: Soft cap for the per-model key registry. Beyond this, entries whose
    #: cached data has already expired are pruned to bound memory growth.
    MAX_REGISTRY_KEYS = 2000
    VERSION = "1"

    #: In-process lock guarding registry read-modify-write cycles so
    #: concurrent ``cache_set``/``cache_delete`` calls cannot lose updates.
    #: (Backends shared across processes still rely on the entry TTL as the
    #: ultimate bound; a missed registration is harmless because the data
    #: entry expires on its own.)
    _registry_lock = threading.RLock()

    @classmethod
    def _model_keys_key(cls, model_name):
        """Return the cache key for a model's registered object keys."""
        return f"{cls.CACHE_PREFIX}:{model_name}:{cls.MODEL_KEYS_SUFFIX}:v{cls.VERSION}"

    @classmethod
    def _registry_for(cls, model_name):
        """Return the registered keys list for a model, defaulting to ``[]``."""
        keys = cache.get(cls._model_keys_key(model_name))
        if not isinstance(keys, list):
            return []
        return [key for key in keys if isinstance(key, str)]

    @classmethod
    def _register_model_key(cls, model_name, cache_key, timeout):
        """Register a generated object key for model-wide invalidation."""
        with cls._registry_lock:
            registry_key = cls._model_keys_key(model_name)
            keys = cls._registry_for(model_name)
            if cache_key in keys:
                return
            keys.append(cache_key)
            if len(keys) > cls.MAX_REGISTRY_KEYS:
                # Bound growth: drop keys whose data entries already expired.
                keys = [key for key in keys if cache.get(key) is not None]
            cache.set(registry_key, keys, timeout)

    @classmethod
    def _unregister_model_key(cls, model_name, cache_key):
        """Remove a generated object key from the model registry."""
        with cls._registry_lock:
            registry_key = cls._model_keys_key(model_name)
            keys = cls._registry_for(model_name)
            if cache_key in keys:
                keys.remove(cache_key)
                if keys:
                    cache.set(registry_key, keys, cls.DEFAULT_TIMEOUT)
                else:
                    cache.delete(registry_key)

    @classmethod
    def _generate_cache_key(cls, model_name, identifier, suffix=""):
        identifier_str = str(identifier)
        if suffix:
            identifier_str = f"{identifier_str}_{suffix}"
        key_string = f"{cls.CACHE_PREFIX}:{model_name}:{identifier_str}:v{cls.VERSION}"
        return hashlib.md5(key_string.encode()).hexdigest()

    @classmethod
    def _serialize_data(cls, data):
        if isinstance(data, (dict, list, tuple, str, int, float, bool, type(None))):
            return json.dumps(data, cls=DjangoJSONEncoder)
        elif hasattr(data, "__dict__"):
            return json.dumps(data.__dict__, cls=DjangoJSONEncoder)
        elif isinstance(data, models.Model):
            from django.forms.models import model_to_dict
            return json.dumps(model_to_dict(data), cls=DjangoJSONEncoder)
        return str(data)

    @classmethod
    def _deserialize_data(cls, data_str, model_class=None):
        try:
            data = json.loads(data_str)
            if model_class and isinstance(data, dict):
                try:
                    return model_class(**data)
                except Exception:
                    return data
            return data
        except json.JSONDecodeError:
            return data_str

    @classmethod
    def cache_set(cls, model_name, identifier, data, suffix="", timeout=None, model_class=None):
        try:
            cache_key = cls._generate_cache_key(model_name, identifier, suffix)
            serialized_data = cls._serialize_data(data)
            timeout = timeout or cls.DEFAULT_TIMEOUT
            cache.set(cache_key, serialized_data, timeout)
            metadata_key = f"{cache_key}_meta"
            metadata = {"model_name": model_name, "identifier": str(identifier), "suffix": suffix, "cached_at": str(datetime.now())}
            cache.set(metadata_key, json.dumps(metadata), timeout)
            cls._register_model_key(model_name, cache_key, timeout)
            return True
        except Exception:
            return False

    @classmethod
    def cache_get(cls, model_name, identifier, suffix="", model_class=None):
        try:
            cache_key = cls._generate_cache_key(model_name, identifier, suffix)
            cached_data = cache.get(cache_key)
            if cached_data is None:
                return None
            return cls._deserialize_data(cached_data, model_class)
        except Exception:
            return None

    @classmethod
    def cache_delete(cls, model_name, identifier, suffix=""):
        try:
            cache_key = cls._generate_cache_key(model_name, identifier, suffix)
            cache.delete(cache_key)
            cache.delete(f"{cache_key}_meta")
            cls._unregister_model_key(model_name, cache_key)
            return True
        except Exception:
            return False

    @classmethod
    def clear_model_cache(cls, model_name):
        """Delete all registered cache entries for one model.

        The registry is scoped by model name, so invalidating one model never
        clears unrelated application or framework cache entries. Entries
        whose data already expired are skipped (not counted). Concurrent
        writers are serialized per process via ``_registry_lock``.

        Returns:
            The number of cache entries actually deleted.
        """
        with cls._registry_lock:
            registry_key = cls._model_keys_key(model_name)
            keys = cls._registry_for(model_name)
            deleted = 0
            for cache_key in keys:
                if cache.delete(cache_key):
                    deleted += 1
                cache.delete(f"{cache_key}_meta")
            cache.delete(registry_key)
            return deleted

    @classmethod
    def cache_get_or_set(cls, model_name, identifier, fetch_callback, suffix="", timeout=None, model_class=None):
        cached_data = cls.cache_get(model_name, identifier, suffix, model_class)
        if cached_data is not None:
            return cached_data
        data = fetch_callback()
        if data is not None:
            cls.cache_set(model_name=model_name, identifier=identifier, data=data, suffix=suffix, timeout=timeout, model_class=model_class)
        return data
