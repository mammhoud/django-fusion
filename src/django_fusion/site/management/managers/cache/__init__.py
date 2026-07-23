"""Cache manager utilities for Django model querysets.

Provides pluggable ``Manager`` subclasses that cache ``get``, ``filter``,
and arbitrary queryset results in any Django-configured cache backend.

Usage::

    from django_fusion.core.cache import CachedManager, CachedModelManager

    class ArticleManager(CachedManager):
        cache_ttl = 600   # 10 minutes

    class Article(models.Model):
        objects = ArticleManager()
"""

from .managers import CachedManager, CachedModelManager

__all__ = ["CachedManager", "CachedModelManager"]
