"""
Search mixins for models.
"""

from typing import Any, Dict, List

from django.db.models import Q


class SearchMixin:
    """
    Mixin for search functionality.
    """
    
    SEARCH_FIELDS = []
    
    @classmethod
    def search(
        cls,
        query: str = "",
        filters: Dict[str, Any] = None,
        ordering: List[str] = None,
        limit: int = 50,
        offset: int = 0,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Search objects.
        """
        qs = cls.objects.all()
        
        # Apply text search
        if query:
            search_fields = cls.SEARCH_FIELDS
            if not search_fields:
                # Auto-detect search fields
                search_fields = [
                    field.name
                    for field in cls._meta.get_fields()
                    if field.get_internal_type() in ["CharField", "TextField"]
                ]
            
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
            "limit": limit,
            "offset": offset,
            "has_more": (offset + len(results)) < total_count,
            "query": query,
        }
    
    @classmethod
    def autocomplete(
        cls,
        query: str,
        field: str = None,
        limit: int = 10,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Autocomplete search.
        """
        if not query:
            return []
        
        qs = cls.objects.all()
        
        if field and hasattr(cls, field):
            qs = qs.filter(**{f"{field}__istartswith": query})
        else:
            # Search across all search fields
            search_fields = cls.SEARCH_FIELDS
            if not search_fields:
                return []
            
            search_q = Q()
            for search_field in search_fields:
                search_q |= Q(**{f"{search_field}__istartswith": query})
            
            qs = qs.filter(search_q)
        
        results = qs[:limit]
        
        return [
            {
                "id": obj.id,
                "text": str(obj),
                "type": cls.__name__,
            }
            for obj in results
        ]


class UniversalSearchMixin:
    """
    Mixin for universal search across models.
    """
    
    @classmethod
    def register_for_search(cls):
        """Register model for universal search."""
        try:
            from core.search_registry import universal_search_registry
            universal_search_registry.register(cls)
        except ImportError:
            pass
    
    @classmethod
    def search_all_models(
        cls,
        keyword: str,
        limit_per_model: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search across all registered models.
        """
        try:
            from core.search_registry import universal_search_registry
            
            results = []
            registry = universal_search_registry.get_registry()
            
            for identifier, info in registry.items():
                model = info["model"]
                
                # Build search query
                q_filter = Q()
                for field in model._meta.fields:
                    if field.get_internal_type() in ["CharField", "TextField"]:
                        q_filter |= Q(**{f"{field.name}__icontains": keyword})
                
                # Execute search
                qs = model.objects.filter(q_filter)[:limit_per_model]
                
                for obj in qs:
                    results.append({
                        "model_identifier": identifier,
                        "model": info["name"],
                        "object_id": obj.pk,
                        "repr": str(obj),
                    })
            
            return results
            
        except ImportError:
            return []
    
    @classmethod
    def search_model_by_identifier(
        cls,
        model_identifier: str,
        keyword: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search specific model by identifier.
        """
        try:
            from core.search_registry import universal_search_registry
            
            info = universal_search_registry.get_model_info(model_identifier)
            if not info:
                return []
            
            model = info["model"]
            
            # Build search query
            q_filter = Q()
            for field in model._meta.fields:
                if field.get_internal_type() in ["CharField", "TextField"]:
                    q_filter |= Q(**{f"{field.name}__icontains": keyword})
            
            # Execute search
            qs = model.objects.filter(q_filter)[:limit]
            
            return [
                {
                    "model_identifier": model_identifier,
                    "object_id": obj.pk,
                    "repr": str(obj),
                }
                for obj in qs
            ]
            
        except ImportError:
            return []