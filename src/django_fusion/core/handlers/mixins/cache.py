"""
Cache mixins for models.
"""

import hashlib
import json
from typing import Any, Dict, Optional

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder


class CacheMixin:
    """
    Basic cache functionality mixin.
    """
    
    CACHE_PREFIX = "model_cache"
    DEFAULT_CACHE_TIMEOUT = 3600
    
    @classmethod
    def _generate_cache_key(
        cls,
        cache_type: str,
        identifier: Any = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate cache key."""
        model_name = cls.__name__.lower()
        key_parts = [cls.CACHE_PREFIX, model_name, cache_type]
        
        if identifier is not None:
            key_parts.append(str(identifier))
        
        if params:
            sorted_params = json.dumps(params, sort_keys=True, cls=DjangoJSONEncoder)
            param_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:8]
            key_parts.append(param_hash)
        
        return ":".join(key_parts)
    
    @classmethod
    def get_cached(
        cls,
        identifier: Any,
        cache_type: str = "detail",
        params: Optional[Dict[str, Any]] = None,
        default: Any = None,
    ) -> Any:
        """Get from cache."""
        cache_key = cls._generate_cache_key(cache_type, identifier, params)
        return cache.get(cache_key, default)
    
    @classmethod
    def set_cached(
        cls,
        identifier: Any,
        data: Any,
        cache_type: str = "detail",
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """Set in cache."""
        try:
            cache_key = cls._generate_cache_key(cache_type, identifier, params)
            timeout = timeout or cls.DEFAULT_CACHE_TIMEOUT
            cache.set(cache_key, data, timeout)
            return True
        except Exception:
            return False
    
    @classmethod
    def delete_cached(
        cls,
        identifier: Any,
        cache_type: str = "detail",
        params: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Delete from cache."""
        try:
            cache_key = cls._generate_cache_key(cache_type, identifier, params)
            cache.delete(cache_key)
            return True
        except Exception:
            return False
    
    def get_self_cache_key(self, cache_type: str = "detail") -> str:
        """Get cache key for this instance."""
        identifier = getattr(self, 'pk', None)
        if not identifier:
            identifier = getattr(self, 'uuid', None) or getattr(self, 'slug', None)
        
        if not identifier:
            raise ValueError("Instance has no identifier for cache key")
        
        return self._generate_cache_key(cache_type, identifier)
    
    def cache_self(self, cache_type: str = "detail", timeout: Optional[int] = None) -> bool:
        """Cache this instance."""
        cache_key = self.get_self_cache_key(cache_type)
        timeout = timeout or self.DEFAULT_CACHE_TIMEOUT
        
        # Serialize for caching
        data = self._serialize_for_cache()
        cache.set(cache_key, data, timeout)
        return True
    
    def get_cached_self(self, cache_type: str = "detail", default: Any = None) -> Any:
        """Get cached version of this instance."""
        cache_key = self.get_self_cache_key(cache_type)
        return cache.get(cache_key, default)
    
    def invalidate_self_cache(self, cache_type: str = "detail") -> bool:
        """Invalidate cache for this instance."""
        cache_key = self.get_self_cache_key(cache_type)
        cache.delete(cache_key)
        return True
    
    def _serialize_for_cache(self) -> Dict[str, Any]:
        """Serialize instance for caching."""
        from django.forms.models import model_to_dict
        
        data = model_to_dict(self)
        data['_model'] = self.__class__.__name__
        data['_id'] = self.pk
        
        # Add string representation
        data['_str'] = str(self)
        
        return data


class CacheSearchMixin(CacheMixin):
    """
    Cache mixin with search capabilities.
    """
    
    SEARCH_CACHE_TIMEOUT = 900  # 15 minutes
    
    @classmethod
    def search_cached(
        cls,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None,
        ordering: Optional[list] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        use_cache: bool = True,
        cache_timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search with caching.
        """
        if not use_cache:
            return cls._search_uncached(query, filters, ordering, limit, offset)
        
        # Generate cache key
        params = {
            "query": query,
            "filters": filters,
            "ordering": ordering,
            "limit": limit,
            "offset": offset,
        }
        
        cache_key = cls._generate_cache_key("search", None, params)
        
        # Try cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return {**cached_result, "from_cache": True}
        
        # Perform search
        result = cls._search_uncached(query, filters, ordering, limit, offset)
        
        # Cache result
        timeout = cache_timeout or cls.SEARCH_CACHE_TIMEOUT
        cache.set(cache_key, result, timeout)
        
        return {**result, "from_cache": False}
    
    @classmethod
    def _search_uncached(
        cls,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None,
        ordering: Optional[list] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Perform search without caching.
        """
        from django.db.models import Q
        
        qs = cls.objects.all()
        
        # Apply text search
        if query:
            search_fields = getattr(cls, 'SEARCH_FIELDS', [])
            if search_fields:
                search_q = Q()
                for field in search_fields:
                    search_q |= Q(**{f"{field}__icontains": query})
                qs = qs.filter(search_q)
        
        # Apply filters
        if filters:
            qs = qs.filter(**filters)
        
        # Get total count
        total_count = qs.count()
        
        # Apply ordering
        if ordering:
            qs = qs.order_by(*ordering)
        
        # Apply pagination
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        
        results = list(qs)
        
        return {
            "results": results,
            "total_count": total_count,
            "has_more": (offset + len(results)) < total_count,
            "query": query,
        }