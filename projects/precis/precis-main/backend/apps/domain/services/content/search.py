"""
Search services.

Canonical import: from apps.domain.services.content import SearchService
"""

import logging
from typing import Any, Dict, List

from django.db.models import Q
from django_fusion.services.base import BaseService

logger = logging.getLogger(__name__)


class SearchService(BaseService):
    """
    Search service with advanced capabilities.
    """

    service_name = "search_service"

    def execute(self, operation: str, **kwargs) -> Any:
        """Execute search operation."""
        if operation == "search":
            return self.search(**kwargs)
        elif operation == "autocomplete":
            return self.autocomplete(**kwargs)
        elif operation == "facet":
            return self.get_facets(**kwargs)
        elif operation == "suggest":
            return self.get_suggestions(**kwargs)
        else:
            return super().execute(operation, **kwargs)

    def search(
        self,
        query: str = "",
        filters: Dict[str, Any] = None,
        facets: List[str] = None,
        ordering: List[str] = None,
        limit: int = 50,
        offset: int = 0,
        min_score: float = 0.1,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Advanced search with facets.
        """
        # Check if manager supports search
        if hasattr(self.manager, 'search'):
            return self.manager.search(
                query=query,
                filters=filters,
                ordering=ordering,
                limit=limit,
                offset=offset,
                min_score=min_score,
                **kwargs,
            )

        # Fallback to basic search
        return self._basic_search(
            query=query,
            filters=filters,
            ordering=ordering,
            limit=limit,
            offset=offset,
            **kwargs,
        )

    def _basic_search(
        self,
        query: str = "",
        filters: Dict[str, Any] = None,
        ordering: List[str] = None,
        limit: int = 50,
        offset: int = 0,
        **kwargs,
    ) -> Dict[str, Any]:
        """Basic search implementation."""
        qs = self.manager.all()

        # Apply text search
        if query:
            search_fields = getattr(self.model_class, 'SEARCH_FIELDS', [])
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

    def autocomplete(
        self,
        query: str,
        field: str = None,
        limit: int = 10,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Autocomplete search.
        """
        if hasattr(self.manager, 'autocomplete'):
            return self.manager.autocomplete(query, field, limit, **kwargs)

        # Basic autocomplete
        if not query:
            return []

        qs = self.manager.all()

        if field and hasattr(self.model_class, field):
            qs = qs.filter(**{f"{field}__istartswith": query})
        else:
            # Search across common fields
            search_fields = ['name', 'title', 'email', 'username']
            available_fields = [
                f for f in search_fields if hasattr(self.model_class, f)
            ]

            if available_fields:
                search_q = Q()
                for search_field in available_fields:
                    search_q |= Q(**{f"{search_field}__istartswith": query})
                qs = qs.filter(search_q)

        results = qs[:limit]

        return [
            {
                "id": obj.id,
                "text": str(obj),
                "type": self.model_class.__name__,
            }
            for obj in results
        ]

    def get_facets(
        self,
        query: str = "",
        filters: Dict[str, Any] = None,
        facet_fields: List[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Get search facets (aggregations).
        """
        from django.db.models import Count

        qs = self.manager.all()

        # Apply search query
        if query:
            search_fields = getattr(self.model_class, 'SEARCH_FIELDS', [])
            if search_fields:
                search_q = Q()
                for field in search_fields:
                    search_q |= Q(**{f"{field}__icontains": query})
                qs = qs.filter(search_q)

        # Apply filters (excluding facet fields)
        if filters:
            filter_copy = filters.copy()
            if facet_fields:
                for field in facet_fields:
                    filter_copy.pop(field, None)
            qs = qs.filter(**filter_copy)

        # Get facets
        facets = {}
        facet_fields = facet_fields or []

        for field in facet_fields:
            if hasattr(self.model_class, field):
                facet_data = list(
                    qs.values(field).annotate(count=Count('id')).order_by('-count')
                )
                facets[field] = facet_data

        return {
            "facets": facets,
            "total_count": qs.count(),
            "query": query,
        }

    def get_suggestions(
        self,
        query: str,
        suggestion_fields: List[str] = None,
        limit: int = 5,
        **kwargs,
    ) -> Dict[str, List[str]]:
        """
        Get search suggestions.
        """
        if not query:
            return {}

        qs = self.manager.all()
        suggestion_fields = suggestion_fields or ['name', 'title']
        available_fields = [
            f for f in suggestion_fields if hasattr(self.model_class, f)
        ]

        suggestions = {}

        for field in available_fields:
            # Get distinct values containing query
            field_suggestions = qs.filter(
                **{f"{field}__icontains": query}
            ).values_list(field, flat=True).distinct()[:limit]

            suggestions[field] = list(field_suggestions)

        return suggestions
