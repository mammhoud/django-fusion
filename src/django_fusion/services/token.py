"""
Token-based security services.

Canonical imports::
    from django_fusion.services import TokenService
    from django_fusion.services import TokenProtectedService
"""

import logging
from typing import Any

from django.conf import settings
from django.db import models

from django_fusion.plugins.apis.auth import BoltTokenConfig, FusionTokenError

from .base import BaseService

logger = logging.getLogger(__name__)


class TokenService(BaseService):
    """
    Service for token-based operations.
    """

    service_name = "token_service"

    def execute(self, operation: str, **kwargs) -> Any:
        """Execute token operation."""
        if operation == "validate":
            return self.validate_token(**kwargs)
        elif operation == "generate":
            return self.generate_token(**kwargs)
        elif operation == "revoke":
            return self.revoke_token(**kwargs)
        else:
            raise ValueError(f"Unknown token operation: {operation}")

    @classmethod
    def validate_action_token(
        cls,
        token: str,
        expected_action: str = "read",
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Validate a token for a named action without requiring a model.

        Older site services call this class-level API. Keep the implementation
        in :meth:`validate_token` so instance and class callers share exactly
        the same validation behavior.
        """
        return cls().validate_token(token, action=expected_action, user_id=user_id)

    def validate_token(
        self,
        token: str,
        action: str = "read",
        user_id: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Validate a signed token without insecure permissive fallbacks."""
        config = BoltTokenConfig(
            secret=getattr(settings, "FUSION_BOLT_JWT_SECRET", "") or getattr(settings, "SECRET_KEY", ""),
            algorithm=getattr(settings, "FUSION_BOLT_JWT_ALGORITHM", "HS256"),
            issuer=getattr(settings, "FUSION_BOLT_JWT_ISSUER", "django-fusion"),
            audience=getattr(settings, "FUSION_BOLT_JWT_AUDIENCE", ""),
        )
        try:
            payload = config.decode(token)
        except FusionTokenError as exc:
            return {"valid": False, "error": str(exc)}

        token_action = payload.get("action", "read")
        token_user_id = str(payload.get("user_id") or payload.get("sub") or "")
        if action != "read" and token_action != action:
            return {"valid": False, "error": "Insufficient permissions"}
        if user_id is not None and token_user_id != str(user_id):
            return {"valid": False, "error": "User mismatch"}
        return {
            "valid": True,
            "user_id": token_user_id,
            "action": token_action,
            "payload": payload,
        }

    def generate_token(
        self,
        user_id: str,
        action: str = "read",
        expires_in: int = 3600,
        metadata: dict[str, Any] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate token for user and action.
        """
        try:
            config = BoltTokenConfig(
                secret=getattr(settings, "FUSION_BOLT_JWT_SECRET", "") or getattr(settings, "SECRET_KEY", ""),
                algorithm=getattr(settings, "FUSION_BOLT_JWT_ALGORITHM", "HS256"),
                issuer=getattr(settings, "FUSION_BOLT_JWT_ISSUER", "django-fusion"),
                audience=getattr(settings, "FUSION_BOLT_JWT_AUDIENCE", ""),
            )
            token = config.issue(
                str(user_id),
                ttl_seconds=expires_in,
                token_type="access",
                user_id=str(user_id),
                action=action,
                metadata=metadata or {},
            )
            return {"success": True, "token": token, "expires_in": expires_in}
        except Exception as e:  # noqa: BLE001 - service returns a stable result contract
            return {"success": False, "error": str(e)}

    def revoke_token(self, token: str, **kwargs) -> dict[str, Any]:
        """Revoke token."""
        # Implement token revocation logic
        # This might involve blacklisting the token

        return {"success": True, "message": "Token revoked"}


class TokenProtectedService(TokenService):
    """
    Service that requires token protection.
    """

    def execute(self, operation: str, **kwargs) -> Any:
        """Execute operation with token validation."""
        token = kwargs.pop("token", None)
        user_id = kwargs.pop("user_id", None)
        action = kwargs.pop("action", operation)

        # Validate token
        if token:
            validation = self.validate_token(token, action, user_id)
            if not validation.get("valid"):
                raise PermissionError(validation.get("error", "Token validation failed"))

        return super().execute(operation, **kwargs)

    def get_with_token(
        self,
        identifier: Any,
        token: str,
        action: str = "read",
        user_id: str | None = None,
        **kwargs,
    ) -> models.Model | None:
        """
        Get object with token validation.
        """
        # Validate token
        validation = self.validate_token(token, action, user_id)
        if not validation.get("valid"):
            return None

        return self.get(identifier, **kwargs)

    def create_with_token(
        self,
        data: dict[str, Any],
        token: str,
        user_id: str | None = None,
        **kwargs,
    ) -> tuple[bool, models.Model | None, str]:
        """
        Create with token validation.
        """
        # Validate token
        validation = self.validate_token(token, "create", user_id)
        if not validation.get("valid"):
            return False, None, validation.get("error", "Token validation failed")

        try:
            obj = self.create(data, **kwargs)
            return True, obj, "Created successfully"
        except Exception as e:
            return False, None, str(e)

    def update_with_token(
        self,
        identifier: Any,
        data: dict[str, Any],
        token: str,
        user_id: str | None = None,
        **kwargs,
    ) -> tuple[bool, models.Model | None, str]:
        """
        Update with token validation.
        """
        # Validate token
        validation = self.validate_token(token, "update", user_id)
        if not validation.get("valid"):
            return False, None, validation.get("error", "Token validation failed")

        result = self.update(identifier, data, **kwargs)
        if result:
            return True, result, "Updated successfully"
        return False, None, "Update failed"

    def delete_with_token(
        self,
        identifier: Any,
        token: str,
        user_id: str | None = None,
        **kwargs,
    ) -> tuple[bool, str]:
        """
        Delete with token validation.
        """
        # Validate token
        validation = self.validate_token(token, "delete", user_id)
        if not validation.get("valid"):
            return False, validation.get("error", "Token validation failed")

        success = self.delete(identifier, **kwargs)
        if success:
            return True, "Deleted successfully"
        return False, "Delete failed"
