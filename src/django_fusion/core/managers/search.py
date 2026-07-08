"""
Search manager with advanced search capabilities.

Canonical import: from django_fusion.core.managers import SearchManagerMixin
"""

import logging
from typing import Any, Dict, List

from django.db import models
from django.db.models import Q, QuerySet

logger = logging.getLogger(__name__)


class SearchManagerMixin:
    """
    Mixin for advanced search functionality.

    Canonical import: from django_fusion.core.managers import SearchManagerMixin
    """

    SEARCH_FIELDS = []
    SEARCH_WEIGHTS = {}
    SEARCH_MIN_SCORE = 0.1

    def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        ordering: List[str] = None,
        limit: int = 50,
        offset: int = 0,
        min_score: float = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Advanced search with scoring and ranking.
        """
        if not query:
            return self._search_without_query(filters, ordering, limit, offset)

        # Get search fields
        search_fields = self._get_search_fields()
        if not search_fields:
            return {"results": [], "total_count": 0, "has_more": False}

        # Build search query
        search_q = self._build_search_query(query, search_fields)

        # Start with base queryset
        qs = self.all()

        # Apply search filter
        qs = qs.filter(search_q)

        # Apply additional filters
        if filters:
            qs = qs.filter(**filters)

        # Get total count
        total_count = qs.count()

        # Apply ordering
        if ordering:
            qs = qs.order_by(*ordering)
        else:
            # Default ordering by relevance
            qs = self._order_by_relevance(qs, query, search_fields)

        # Apply pagination
        qs = qs[offset:offset + limit]

        # Score results
        results = list(qs)
        scored_results = self._score_results(results, query, search_fields)

        # Apply minimum score filter
        min_score = min_score or self.SEARCH_MIN_SCORE
        filtered_results = [
            item for item in scored_results if item.get("score", 0) >= min_score
        ]

        return {
            "results": filtered_results,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + len(filtered_results)) < total_count,
            "query": query,
        }

    def _search_without_query(
        self,
        filters: Dict[str, Any] = None,
        ordering: List[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Search without query text."""
        qs = self.all()

        if filters:
            qs = qs.filter(**filters)

        total_count = qs.count()

        if ordering:
            qs = qs.order_by(*ordering)

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
        }

    def _get_search_fields(self) -> List[str]:
        """Get search fields for this model."""
        # Use model's SEARCH_FIELDS if defined
        if hasattr(self.model, 'SEARCH_FIELDS') and self.model.SEARCH_FIELDS:
            return self.model.SEARCH_FIELDS

        # Fallback to all CharField and TextField
        return [
            field.name
            for field in self.model._meta.get_fields()
            if field.get_internal_type() in ["CharField", "TextField"]
        ]

    def _build_search_query(self, query: str, search_fields: List[str]) -> Q:
        """Build search query with field weights."""
        search_q = Q()

        # Split query into words
        words = query.split()

        for field in search_fields:
            # Get field weight
            weight = self.SEARCH_WEIGHTS.get(field, 1.0)

            if weight > 0:
                for word in words:
                    if word:  # Skip empty words
                        # Exact match (higher weight)
                        exact_q = Q(**{f"{field}__iexact": word})
                        # Partial match
                        partial_q = Q(**{f"{field}__icontains": word})

                        # Add to search query with OR
                        search_q |= exact_q
                        search_q |= partial_q

        return search_q

    def _order_by_relevance(
        self,
        qs: QuerySet,
        query: str,
        search_fields: List[str],
    ) -> QuerySet:
        """
        Order results by relevance score.
        This is a simplified implementation.
        For production, consider using full-text search.
        """
        # Simple ordering: prioritize exact matches
        # In production, you might want to use Django's SearchVector
        return qs

    def _score_results(
        self,
        results: List[models.Model],
        query: str,
        search_fields: List[str],
    ) -> List[Dict[str, Any]]:
        """Score search results."""
        scored = []
        words = [w.lower() for w in query.split() if w]

        for obj in results:
            score = 0
            matches = []

            for field in search_fields:
                if hasattr(obj, field):
                    value = getattr(obj, field)
                    if value:
                        value_str = str(value).lower()

                        for word in words:
                            if word in value_str:
                                # Calculate score based on match type
                                if value_str == word:
                                    score += 10  # Exact match
                                elif value_str.startswith(word):
                                    score += 5   # Starts with
                                else:
                                    score += 1   # Contains

                                matches.append({
                                    "field": field,
                                    "value": value_str,
                                    "word": word,
                                })

            # Apply field weights
            for match in matches:
                weight = self.SEARCH_WEIGHTS.get(match["field"], 1.0)
                score *= weight

            scored.append({
                "object": obj,
                "score": score,
                "matches": matches,
            })

        # Sort by score (descending)
        scored.sort(key=lambda x: x["score"], reverse=True)

        return scored

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
        if not query:
            return []

        qs = self.all()

        if field and hasattr(self.model, field):
            qs = qs.filter(**{f"{field}__istartswith": query})
            results = qs[:limit]
        else:
            # Search across all search fields
            search_fields = self._get_search_fields()
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
                "type": self.model.__name__,
            }
            for obj in results
        ]
