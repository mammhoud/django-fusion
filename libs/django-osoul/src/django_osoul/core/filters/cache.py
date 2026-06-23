"""
Cached filters.
"""

import hashlib
import json

from django.core.cache import cache
from django.db.models import QuerySet

from .base import BaseFilterMethod, DictFilterMethod


class CachedBaseFilterMethod(BaseFilterMethod):
    """
    Cached version of BaseFilterMethod.
    """
    
    def __init__(
        self,
        *args,
        cache_key_prefix: str = "filter_method",
        cache_timeout: int = 3600,
        force_refresh: bool = False,
        enable_logging: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cache_key_prefix = cache_key_prefix
        self.cache_timeout = cache_timeout
        self.force_refresh = force_refresh
        self.enable_logging = enable_logging
    
    def _generate_cache_key(self) -> str:
        """Generate cache key for filter."""
        raw_data = {
            "model": self.model_class.__name__,
            "field": self.filter_field,
            "value": str(self.filter_value),
            "filter_data": self.filter_data,
        }
        raw_str = json.dumps(raw_data, sort_keys=True)
        hashed = hashlib.md5(raw_str.encode()).hexdigest()
        return f"{self.cache_key_prefix}:{hashed}"
    
    def run(self) -> QuerySet:
        """Execute filter with caching."""
        cache_key = self._generate_cache_key()
        
        if not self.force_refresh:
            cached_ids = cache.get(cache_key)
            if cached_ids is not None:
                if self.enable_logging:
                    print(f"Cache hit: {cache_key}")
                return self.model_class.objects.filter(pk__in=cached_ids)
        
        if self.enable_logging:
            print(f"Cache miss: {cache_key}")
        
        # Execute original filter
        result = super().run()
        
        # Cache the IDs
        ids = list(result.values_list("pk", flat=True))
        cache.set(cache_key, ids, timeout=self.cache_timeout)
        
        return self.model_class.objects.filter(pk__in=ids)


class CachedDictFilterMethod(DictFilterMethod):
    """
    Cached version of DictFilterMethod.
    """
    
    def __init__(
        self,
        *args,
        cache_key_prefix: str = "dict_filter_method",
        cache_timeout: int = 3600,
        force_refresh: bool = False,
        enable_logging: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.cache_key_prefix = cache_key_prefix
        self.cache_timeout = cache_timeout
        self.force_refresh = force_refresh
        self.enable_logging = enable_logging
    
    def _generate_cache_key(self) -> str:
        """Generate cache key for filter."""
        raw_data = {
            "model": self.model_class.__name__,
            "filters": self.filters,
            "filter_data": self.filter_data,
        }
        raw_str = json.dumps(raw_data, sort_keys=True)
        hashed = hashlib.md5(raw_str.encode()).hexdigest()
        return f"{self.cache_key_prefix}:{hashed}"
    
    def run(self) -> QuerySet:
        """Execute filter with caching."""
        cache_key = self._generate_cache_key()
        
        if not self.force_refresh:
            cached_ids = cache.get(cache_key)
            if cached_ids is not None:
                if self.enable_logging:
                    print(f"Cache hit: {cache_key}")
                return self.model_class.objects.filter(pk__in=cached_ids)
        
        if self.enable_logging:
            print(f"Cache miss: {cache_key}")
        
        # Execute original filter
        result = super().run()
        
        # Cache the IDs
        ids = list(result.values_list("pk", flat=True))
        cache.set(cache_key, ids, timeout=self.cache_timeout)
        
        return self.model_class.objects.filter(pk__in=ids)