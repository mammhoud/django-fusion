"""CachingStorage — generic caching storage for Django/Wagtail models."""
from __future__ import annotations
import hashlib
import json
import logging
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
    VERSION = "1"

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
            return True
        except Exception:
            return False

    @classmethod
    def cache_get_or_set(cls, model_name, identifier, fetch_callback, suffix="", timeout=None, model_class=None):
        cached_data = cls.cache_get(model_name, identifier, suffix, model_class)
        if cached_data is not None:
            return cached_data
        data = fetch_callback()
        if data is not None:
            cls.cache_set(model_name=model_name, identifier=identifier, data=data, suffix=suffix, timeout=timeout, model_class=model_class)
        return data
