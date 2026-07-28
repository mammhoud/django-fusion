from functools import cache
from typing import Any

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from ninja.errors import AuthenticationError
from ninja.security import HttpBasicAuth
from www.core.auth_app.models.token import Token

from config import logger


class AuthenticationException(AuthenticationError):
    """Custom exception for authentication errors with detailed messages."""

    def __init__(self, message: str, error_code: str = None, status_code: int = 401):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code


class AuthUtils:
    """Centralized authentication utility class."""

    @staticmethod
    def validate_token_structure(token: str) -> bool:
        """Validate basic token structure."""
        try:
            parts = token.split(".")
            return len(parts) == 3
        except AttributeError:
            return False

    @staticmethod
    def decode_jwt_token(token: str) -> dict[str, Any]:
        """Decode and validate JWT token."""
        try:
            return jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_exp": True},
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("Token has expired", "TOKEN_EXPIRED")
        except jwt.InvalidTokenError as e:
            raise AuthenticationException(f"Invalid token: {e!s}", "INVALID_TOKEN")

    @staticmethod
    def get_stored_token(token: str) -> Token | None:
        """Retrieve token from the database."""
        return (
            Token.objects.filter(
                token=token, is_revoked=False, is_deleted=False, exp__gt=now()
            )
            .select_related("created_by")
            .first()
        )

    @staticmethod
    def validate_token_state(token: Token) -> None:
        """Validate token state and permissions."""
        if token.is_revoked:
            raise AuthenticationException("Token has been revoked", "TOKEN_REVOKED")
        if not token.is_valid():
            raise AuthenticationException("Token is not valid", "TOKEN_INVALID")

    @staticmethod
    def get_and_validate_user(decoded_token: dict[str, Any]) -> get_user_model():
        """Retrieve and validate user from decoded token."""
        try:
            user = get_user_model().objects.get(id=decoded_token.get("user_id"))
            if not user.is_active:
                raise AuthenticationException(
                    "User account is disabled", "USER_DISABLED"
                )
            return user
        except get_user_model().DoesNotExist:
            raise AuthenticationException("User not found", "USER_NOT_FOUND")

    @staticmethod
    def update_token_usage(token: Token) -> None:
        """Update token usage statistics."""
        token.last_used = now()
        token.save(update_fields=["last_used"])


class BasicAuthWithToken(HttpBasicAuth):
    """Enhanced Basic Authentication with token generation."""

    def authenticate(
        self, request, username: str, password: str
    ) -> tuple[get_user_model() | None, dict[str, Any]]:
        """Authenticate using username/password and generate tokens."""
        try:
            user, refresh_token, access_token = Token.authenticate_credentials(
                username, password
            )

            if not user:
                return None, {}

            token_info = {
                "access_token": access_token.token if access_token else None,
                "refresh_token": refresh_token.token if refresh_token else None,
                "token_type": "Bearer",
                "expires_in": (
                    int((access_token.exp - now()).total_seconds())
                    if access_token
                    else None
                ),
                "user_id": str(user.id),
            }

            cache_key = f"auth_basic_{username}"
            cache.set(cache_key, token_info, 300)

            return user, token_info

        except AuthenticationException:
            raise
        except Exception as e:
            logger.error("Basic auth error: %s", e, exc_info=True)
            return None, {}
