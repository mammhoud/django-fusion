"""
Token-aware filters.
"""

from typing import Any, Dict, Optional

try:
    import django_filters
except ImportError:
    django_filters = None

from django.core.exceptions import PermissionDenied as PermissionError
from django.db.models import QuerySet

from .base import BaseFilterMethod


class TokenFilterMixin:
    """
    Mixin for token-based filtering.
    """

    def validate_token(
        self,
        token: str,
        action: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate token for action.
        """
        # This should integrate with your token validation system
        # For now, return a basic validation
        return {"valid": True, "action": action, "user_id": user_id}

    def check_token_permission(
        self,
        token: str,
        action: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """Check if token has permission for action."""
        validation = self.validate_token(token, action, user_id)
        return validation.get("valid", False)


class TokenAwareFilter(BaseFilterMethod, TokenFilterMixin):
    """
    Token-aware base filter.
    """

    def __init__(
        self,
        *args,
        require_token: bool = False,
        token: Optional[str] = None,
        token_action: str = "read",
        user_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.require_token = require_token
        self.token = token
        self.token_action = token_action
        self.user_id = user_id

        if self.require_token and (not self.token or not self.user_id):
            raise ValueError("Token and user_id required for token-protected filters")

    def run(self) -> QuerySet:
        """Execute filter with token validation."""
        if self.require_token:
            if not self.check_token_permission(self.token, self.token_action, self.user_id):
                raise PermissionError("Token authentication failed")

        return super().run()


class TokenFilterSet:
    """
    Token-aware FilterSet.
    """

    def __init__(self):
        if django_filters is None:
            raise ImportError("django-filters is required to use TokenFilterSet")

        # Create the actual FilterSet class dynamically
        class _TokenFilterSet(django_filters.FilterSet, TokenFilterMixin):
            token = django_filters.CharFilter(
                field_name="token",
                method="filter_by_token",
                help_text="Authentication token",
            )

            def filter_by_token(self, queryset, name, value):
                """
                Filter based on token permissions.
                """
                # Get user_id from token (this is simplified)
                # In reality, you'd decode the token to get user_id
                validation = self.validate_token(value, "read")

                if not validation.get("valid"):
                    return queryset.none()

                user_id = validation.get("user_id")

                # Filter by user ownership if model has user field
                if hasattr(queryset.model, 'user_id'):
                    return queryset.filter(user_id=user_id)

                return queryset

        self._filterset_class = _TokenFilterSet
