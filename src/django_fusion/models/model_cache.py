import logging
from typing import Any

from django_fusion.models.cache_storage import CachingStorage

logger = logging.getLogger(__name__)

class ModelCacheMixin:
    """Mixin to add caching capabilities to Django models."""

    @property
    def cache_key(self) -> str:
        """Generate cache key for this instance."""
        return CachingStorage._generate_cache_key(
            model_name=self.__class__.__name__.lower(),
            identifier=self.pk or getattr(self, "slug", None) or id(self),
        )

    def cache_set(self, timeout: int | None = None) -> bool:
        """Cache this instance."""
        return CachingStorage.cache_set(
            model_name=self.__class__.__name__.lower(),
            identifier=self.pk or getattr(self, "slug", None),
            data=self,
            timeout=timeout,
            model_class=self.__class__,
        )

    @classmethod
    def cache_get(cls, identifier: Any) -> Any | None:
        """Get cached instance by identifier."""
        return CachingStorage.cache_get(
            model_name=cls.__name__.lower(), identifier=identifier, model_class=cls
        )

    @classmethod
    def get_or_cache(cls, identifier: Any, **kwargs) -> Any | None:
        """
        Get from cache or fetch from database.

        Args:
            identifier: Primary key, slug, or other identifier
            **kwargs: Additional filter parameters

        Returns:
            Model instance or None
        """

        def fetch_data():
            try:
                # Try primary key first
                if isinstance(identifier, (int, str)) and identifier.isdigit():
                    return cls.objects.filter(pk=int(identifier)).first()

                # Try slug if exists
                if hasattr(cls, "slug"):
                    return cls.objects.filter(slug=identifier).first()

                # Try other lookups
                return cls.objects.filter(**kwargs).first()
            except Exception as e:
                logger.error(f"Failed to fetch {cls.__name__}: {e}")
                return None

        return CachingStorage.cache_get_or_set(
            model_name=cls.__name__.lower(),
            identifier=identifier,
            fetch_callback=fetch_data,
            model_class=cls,
        )

    def invalidate_all_cache(self) -> int:
        """Invalidate all cache for this model."""
        return CachingStorage.clear_model_cache(self.__class__.__name__.lower())

    def _generate_cache_key(self, suffix: str, identifier: Any) -> str:
        """Generate cache key helper."""
        return CachingStorage._generate_cache_key(
            model_name=self.__class__.__name__.lower(),
            identifier=identifier,
            suffix=suffix,
        )
