"""
Token-aware managers for secure operations.

Canonical imports::
    from django_fusion.core.managers import TokenAwareManagerMixin
    from django_fusion.core.managers import TokenCachedManager
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional

from django.core.cache import cache
from django.db import models
from django.db.models import QuerySet

from django_fusion.site.management.managers.cache import CachedManager

logger = logging.getLogger(__name__)


class TokenAwareManagerMixin:
    """
    Mixin for token-aware operations.

    Canonical import: from django_fusion.core.managers import TokenAwareManagerMixin
    """

    TOKEN_CACHE_PREFIX = "token_auth"
    TOKEN_CACHE_TIMEOUT = 300  # 5 minutes

    def validate_token(
        self,
        token: str,
        action: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate token for action.
        """
        try:
            from core.services.token_service import TokenService

            if action == "read":
                return TokenService.validate_read_token(token)
            elif action == "write":
                return TokenService.validate_write_token(token)
            elif action == "delete":
                return TokenService.validate_delete_token(token)
            elif action == "admin":
                return TokenService.validate_admin_token(token)
            else:
                return TokenService.validate_token(token)

        except ImportError:
            logger.warning("TokenService not available")
            return {"valid": True, "action": action, "user_id": user_id}

    def get_token_cache_key(
        self,
        token: str,
        action: str,
        user_id: Optional[str] = None,
    ) -> str:
        """Generate cache key for token validation."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        parts = [self.TOKEN_CACHE_PREFIX, action, token_hash]

        if user_id:
            parts.append(f"user:{user_id}")

        return ":".join(parts)

    def get_with_token(
        self,
        identifier: Any,
        token: str,
        action: str = "read",
        user_id: Optional[str] = None,
        require_ownership: bool = False,
        field: str = None,
        **kwargs,
    ) -> Optional[models.Model]:
        """
        Get object with token validation.
        """
        # Validate token
        validation = self.validate_token(token, action, user_id, str(identifier))

        if not validation.get("valid", True):
            logger.warning(f"Token validation failed: {validation}")
            return None

        # Get object
        obj = self.get_by_field(identifier, field, **kwargs)
        if not obj:
            return None

        # Check ownership if required
        if require_ownership and user_id:
            if not self._check_ownership(obj, user_id):
                return None

        # Check object-level permissions
        if hasattr(obj, "check_token_permission"):
            if not obj.check_token_permission(token, action):
                return None

        return obj

    def filter_with_token(
        self,
        token: str,
        action: str = "read",
        user_id: Optional[str] = None,
        filters: Dict[str, Any] = None,
        require_ownership: bool = False,
        **kwargs,
    ) -> QuerySet:
        """
        Filter objects with token validation.
        """
        # Validate token
        validation = self.validate_token(token, action, user_id)

        if not validation.get("valid", True):
            return self.model.objects.none()

        qs = self.all()
        filters = filters or {}

        # Add ownership filter if required
        if require_ownership and user_id:
            ownership_filters = self._get_ownership_filters(user_id)
            if ownership_filters:
                filters.update(ownership_filters)

        # Apply filters
        if filters:
            qs = qs.filter(**filters)

        return qs

    def _check_ownership(self, obj: models.Model, user_id: str) -> bool:
        """Check if user owns the object."""
        # Check common ownership fields
        ownership_fields = ['user_id', 'created_by_id', 'owner_id']

        for field in ownership_fields:
            if hasattr(obj, field):
                if str(getattr(obj, field)) == user_id:
                    return True

        # Check foreign key relationships
        if hasattr(obj, 'user'):
            try:
                return str(obj.user.id) == user_id
            except:
                pass

        return False

    def _get_ownership_filters(self, user_id: str) -> Dict[str, Any]:
        """Get filters for user ownership."""
        ownership_fields = ['user_id', 'created_by_id', 'owner_id']

        for field in ownership_fields:
            if hasattr(self.model, field):
                return {field: user_id}

        return {}


class TokenCachedManager(TokenAwareManagerMixin, CachedManager):
    """
    Token-aware cached manager.

    Canonical import: from django_fusion.core.managers import TokenCachedManager
    """

    def get_token_cached(
        self,
        identifier: Any,
        token: str,
        action: str = "read",
        user_id: Optional[str] = None,
        require_ownership: bool = False,
        field: str = None,
        cache_timeout: int = None,
        force_refresh: bool = False,
        **kwargs,
    ) -> Optional[models.Model]:
        """
        Get object with token validation and caching.
        """
        if not self.enable_cache or force_refresh:
            return self.get_with_token(
                identifier=identifier,
                token=token,
                action=action,
                user_id=user_id,
                require_ownership=require_ownership,
                field=field,
                **kwargs,
            )

        # Generate cache key including token info
        token_hash = hashlib.sha256(f"{token}:{action}".encode()).hexdigest()[:16]
        params = {
            "token_hash": token_hash,
            "user_id": user_id,
            "require_ownership": require_ownership,
            "field": field,
            **kwargs,
        }

        cache_key = self._generate_cache_key("token_get", identifier, params)

        # Try cache first
        cached_obj = cache.get(cache_key)
        if cached_obj is not None:
            try:
                obj = self._deserialize_from_cache(cached_obj)

                # Revalidate ownership if required
                if require_ownership and user_id:
                    if not self._check_ownership(obj, user_id):
                        cache.delete(cache_key)
                        return None

                return obj
            except Exception as e:
                logger.error(f"Cache deserialization failed: {e}")
                cache.delete(cache_key)

        # Get with token validation
        obj = self.get_with_token(
            identifier=identifier,
            token=token,
            action=action,
            user_id=user_id,
            require_ownership=require_ownership,
            field=field,
            **kwargs,
        )

        if obj:
            # Cache the object
            cache_data = self._serialize_for_cache(obj)
            timeout = cache_timeout or self.cache_timeout
            cache.set(cache_key, cache_data, timeout)

        return obj

    def filter_token_cached(
        self,
        token: str,
        action: str = "read",
        user_id: Optional[str] = None,
        filters: Dict[str, Any] = None,
        require_ownership: bool = False,
        ordering: List[str] = None,
        limit: int = None,
        offset: int = 0,
        cache_timeout: int = None,
        force_refresh: bool = False,
        **kwargs,
    ) -> QuerySet:
        """
        Filter with token validation and caching.
        """
        if not self.enable_cache or force_refresh:
            return self.filter_with_token(
                token=token,
                action=action,
                user_id=user_id,
                filters=filters,
                require_ownership=require_ownership,
                **kwargs,
            )

        # Generate cache key
        token_hash = hashlib.sha256(f"{token}:{action}".encode()).hexdigest()[:16]
        params = {
            "token_hash": token_hash,
            "user_id": user_id,
            "filters": filters,
            "require_ownership": require_ownership,
            "ordering": ordering,
            "limit": limit,
            "offset": offset,
            **kwargs,
        }

        cache_key = self._generate_cache_key("token_filter", None, params)

        # Try cache first
        cached_ids = cache.get(cache_key)
        if cached_ids is not None:
            return self.filter(pk__in=cached_ids)

        # Query with token validation
        qs = self.filter_with_token(
            token=token,
            action=action,
            user_id=user_id,
            filters=filters,
            require_ownership=require_ownership,
            **kwargs,
        )

        # Apply ordering and pagination
        if ordering:
            qs = qs.order_by(*ordering)

        if limit:
            qs = qs[offset:offset + limit]

        # Get IDs for caching
        ids = list(qs.values_list('pk', flat=True))

        # Cache IDs
        timeout = cache_timeout or self.cache_timeout
        cache.set(cache_key, ids, timeout)

        return self.filter(pk__in=ids)
