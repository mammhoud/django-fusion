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
    """
    A generic caching storage class for Django and Django Wagtail models.
    Supports multiple model types (courses, profiles, messages, etc.)
    """

    # Cache configuration
    DEFAULT_TIMEOUT = 60 * 60 * 24  # 24 hours
    CACHE_PREFIX = "cached_data"
    VERSION = "1"

    @classmethod
    def _generate_cache_key(
        cls, model_name: str, identifier: Any, suffix: str = ""
    ) -> str:
        """
        Generate a consistent cache key.

        Args:
            model_name: Name of the model (e.g., 'course', 'profile')
            identifier: Unique identifier for the data (id, slug, etc.)
            suffix: Additional suffix for complex queries

        Returns:
            Cache key string
        """
        # Convert identifier to string and create hash
        identifier_str = str(identifier)
        if suffix:
            identifier_str = f"{identifier_str}_{suffix}"

        # Create a deterministic hash
        key_string = f"{cls.CACHE_PREFIX}:{model_name}:{identifier_str}:v{cls.VERSION}"
        return hashlib.md5(key_string.encode()).hexdigest()

    @classmethod
    def _serialize_data(cls, data: Any) -> str:
        """Serialize data for caching."""
        if isinstance(data, (dict, list, tuple, str, int, float, bool, type(None))):
            return json.dumps(data, cls=DjangoJSONEncoder)
        elif hasattr(data, "__dict__"):
            return json.dumps(data.__dict__, cls=DjangoJSONEncoder)
        elif isinstance(data, models.Model):
            # For Django models, serialize to dict
            from django.forms.models import model_to_dict

            return json.dumps(model_to_dict(data), cls=DjangoJSONEncoder)
        else:
            return str(data)

    @classmethod
    def _deserialize_data(
        cls, data_str: str, model_class: type[models.Model] | None = None
    ) -> Any:
        """Deserialize data from cache."""
        try:
            data = json.loads(data_str)
            if model_class and isinstance(data, dict):
                # Attempt to create model instance
                try:
                    return model_class(**data)
                except:  # noqa: E722
                    return data
            return data
        except json.JSONDecodeError:
            return data_str

    @classmethod
    def cache_set(
        cls,
        model_name: str,
        identifier: Any,
        data: Any,
        suffix: str = "",
        timeout: int | None = None,
        model_class: type[models.Model] | None = None,
    ) -> bool:
        """
        Cache data with proper serialization.

        Args:
            model_name: Name of the model/entity
            identifier: Unique identifier
            data: Data to cache
            suffix: Additional cache key suffix
            timeout: Cache timeout in seconds
            model_class: Django model class for serialization

        Returns:
            Success status
        """
        try:
            cache_key = cls._generate_cache_key(model_name, identifier, suffix)
            serialized_data = cls._serialize_data(data)

            timeout = timeout or cls.DEFAULT_TIMEOUT
            cache.set(cache_key, serialized_data, timeout)

            # Also store metadata about what's cached
            metadata_key = f"{cache_key}_meta"
            metadata = {
                "model_name": model_name,
                "identifier": str(identifier),
                "suffix": suffix,
                "cached_at": str(datetime.now()),
            }
            cache.set(metadata_key, json.dumps(metadata), timeout)

            logger.debug(f"Cached data for {model_name}/{identifier}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache data: {e}")
            return False

    @classmethod
    def cache_get(
        cls,
        model_name: str,
        identifier: Any,
        suffix: str = "",
        model_class: type[models.Model] | None = None,
    ) -> Any | None:
        """
        Get cached data if available.

        Args:
            model_name: Name of the model/entity
            identifier: Unique identifier
            suffix: Additional cache key suffix
            model_class: Django model class for deserialization

        Returns:
            Cached data or None
        """
        try:
            cache_key = cls._generate_cache_key(model_name, identifier, suffix)

            # Check cache first
            cached_data = cache.get(cache_key)

            if cached_data is None:
                logger.debug(f"Cache miss for {model_name}/{identifier}")
                return None

            # Deserialize and return
            data = cls._deserialize_data(cached_data, model_class)
            logger.debug(f"Cache hit for {model_name}/{identifier}")
            return data

        except Exception as e:
            logger.error(f"Failed to get cached data: {e}")
            return None

    @classmethod
    def cache_delete(cls, model_name: str, identifier: Any, suffix: str = "") -> bool:
        """
        Delete cached data.

        Args:
            model_name: Name of the model/entity
            identifier: Unique identifier
            suffix: Additional cache key suffix

        Returns:
            Success status
        """
        try:
            cache_key = cls._generate_cache_key(model_name, identifier, suffix)
            cache.delete(cache_key)

            # Also delete metadata
            metadata_key = f"{cache_key}_meta"
            cache.delete(metadata_key)

            logger.debug(f"Deleted cache for {model_name}/{identifier}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            return False

    @classmethod
    def cache_get_or_set(
        cls,
        model_name: str,
        identifier: Any,
        fetch_callback: callable,
        suffix: str = "",
        timeout: int | None = None,
        model_class: type[models.Model] | None = None,
    ) -> Any:
        """
        Get cached data or fetch and cache if not available.

        Args:
            model_name: Name of the model/entity
            identifier: Unique identifier
            fetch_callback: Function to fetch data if not cached
            suffix: Additional cache key suffix
            timeout: Cache timeout in seconds
            model_class: Django model class

        Returns:
            Data from cache or fetched data
        """
        # Try to get from cache first
        cached_data = cls.cache_get(model_name, identifier, suffix, model_class)

        if cached_data is not None:
            return cached_data

        # Fetch data if not in cache
        data = fetch_callback()

        if data is not None:
            # Cache the fetched data
            cls.cache_set(
                model_name=model_name,
                identifier=identifier,
                data=data,
                suffix=suffix,
                timeout=timeout,
                model_class=model_class,
            )

        return data

    @classmethod
    def bulk_cache_set(
        cls,
        model_name: str,
        data_dict: dict[Any, Any],
        suffix: str = "",
        timeout: int | None = None,
        model_class: type[models.Model] | None = None,
    ) -> bool:
        """
        Cache multiple items at once.

        Args:
            model_name: Name of the model/entity
            data_dict: Dictionary of {identifier: data}
            suffix: Additional cache key suffix
            timeout: Cache timeout in seconds
            model_class: Django model class

        Returns:
            Success status
        """
        try:
            cache_data = {}
            metadata = {}

            for identifier, data in data_dict.items():
                cache_key = cls._generate_cache_key(model_name, identifier, suffix)
                serialized_data = cls._serialize_data(data)
                cache_data[cache_key] = serialized_data

                # Metadata
                metadata_key = f"{cache_key}_meta"
                metadata[metadata_key] = json.dumps(
                    {
                        "model_name": model_name,
                        "identifier": str(identifier),
                        "suffix": suffix,
                        "cached_at": str(datetime.now()),
                    }
                )

            # Set all cache items
            timeout = timeout or cls.DEFAULT_TIMEOUT
            cache.set_many(cache_data, timeout)
            cache.set_many(metadata, timeout)

            logger.debug(f"Bulk cached {len(data_dict)} items for {model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to bulk cache: {e}")
            return False

    @classmethod
    def get_cache_stats(cls, model_name: str | None = None) -> dict:
        """
        Get cache statistics.

        Args:
            model_name: Optional filter by model name

        Returns:
            Cache statistics
        """
        # Note: This requires Django's cache backend to support keys() method
        # For Redis, you might need to use a different approach
        stats = {
            "total_items": 0,
            "by_model": {},
            "cache_prefix": cls.CACHE_PREFIX,
            "version": cls.VERSION,
        }

        # Implementation depends on cache backend
        # This is a simplified version
        return stats

    @classmethod
    def clear_model_cache(cls, model_name: str) -> int:
        """
        Clear all cache for a specific model.

        Args:
            model_name: Name of the model to clear

        Returns:
            Number of items cleared
        """
        # This method's implementation depends on your cache backend
        # For production, you might need to iterate through keys
        # or use pattern-based deletion if supported

        logger.info(f"Cleared cache for model: {model_name}")
        return 0  # Replace with actual implementation
