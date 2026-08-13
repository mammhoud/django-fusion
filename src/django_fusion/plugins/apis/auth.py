"""Token helpers shared by django-fusion Bolt API integrations.

The module is deliberately dependency-light at import time: PyJWT and
``django_bolt`` are loaded only when a caller requests token operations. This
lets projects keep their Django render/API fallback working when the optional
Bolt runtime is not installed.
"""
from __future__ import annotations

import os
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from django.conf import settings as django_settings

__all__ = [
    "BoltTokenConfig",
    "FusionTokenError",
    "build_bolt_auth",
    "extract_bearer_token",
    "get_token_config",
    "refresh_payload",
    "token_payload",
    "user_token_payload",
    "verify_token_user",
    "verify_request_user",
    "TokenUserError",
]


class FusionTokenError(RuntimeError):
    """Raised when token configuration, issuance, or verification fails."""


class TokenUserError(FusionTokenError):
    """Raised when a valid token cannot be mapped to an active Django user."""


@dataclass(frozen=True)
class BoltTokenConfig:
    """Configuration for JWT bearer tokens and optional static API keys.

    Raw values are read from environment/settings at construction time and are
    never included in ``repr`` output. API keys are passed to django-bolt only
    when explicitly configured.
    """

    secret: str = field(repr=False, default="")
    algorithm: str = "HS256"
    ttl_seconds: int = 3600
    refresh_ttl_seconds: int = 2_592_000
    api_key: str = field(repr=False, default="")
    api_key_header: str = "X-API-Key"
    authorization_header: str = "Authorization"
    issuer: str = "django-fusion"
    audience: str = ""

    @classmethod
    def from_django_settings(cls) -> BoltTokenConfig:
        """Build config from ``FUSION_BOLT_*`` settings/environment values."""
        secret = os.environ.get("FUSION_BOLT_JWT_SECRET") or getattr(
            django_settings, "SECRET_KEY", ""
        )
        api_key = os.environ.get("FUSION_BOLT_API_KEY", "") or getattr(
            django_settings, "FUSION_BOLT_API_KEY", ""
        )
        return cls(
            secret=secret,
            algorithm=os.environ.get(
                "FUSION_BOLT_JWT_ALGORITHM",
                getattr(django_settings, "FUSION_BOLT_JWT_ALGORITHM", "HS256"),
            ),
            ttl_seconds=int(
                os.environ.get(
                    "FUSION_BOLT_TOKEN_TTL",
                    getattr(django_settings, "FUSION_BOLT_TOKEN_TTL", 3600),
                )
            ),
            refresh_ttl_seconds=int(
                os.environ.get(
                    "FUSION_BOLT_REFRESH_TTL",
                    getattr(django_settings, "FUSION_BOLT_REFRESH_TTL", 2_592_000),
                )
            ),
            api_key=api_key,
            api_key_header=os.environ.get(
                "FUSION_BOLT_API_KEY_HEADER",
                getattr(django_settings, "FUSION_BOLT_API_KEY_HEADER", "X-API-Key"),
            ),
            authorization_header=os.environ.get(
                "FUSION_BOLT_AUTH_HEADER",
                getattr(django_settings, "FUSION_BOLT_AUTH_HEADER", "Authorization"),
            ),
            issuer=os.environ.get(
                "FUSION_BOLT_JWT_ISSUER",
                getattr(django_settings, "FUSION_BOLT_JWT_ISSUER", "django-fusion"),
            ),
            audience=os.environ.get(
                "FUSION_BOLT_JWT_AUDIENCE",
                getattr(django_settings, "FUSION_BOLT_JWT_AUDIENCE", ""),
            ),
        )

    def issue(
        self,
        subject: str,
        *,
        role: str = "viewer",
        ttl_seconds: int | None = None,
        token_type: str = "access",
        **claims: Any,
    ) -> str:
        """Issue a signed JWT without returning secrets in logs or errors.

        ``ttl_seconds`` is an optional per-token override used by public token
        endpoints. It is clamped to at least one second; the configured value
        remains the default for callers that do not provide an override.
        """
        if not self.secret:
            raise FusionTokenError("FUSION_BOLT_JWT_SECRET or SECRET_KEY is required")
        try:
            import jwt
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise FusionTokenError("PyJWT is required to issue Bolt tokens") from exc

        now = int(time.time())
        payload = {
            "sub": subject,
            "role": role,
            "iat": now,
            "exp": now + max(1, ttl_seconds or self.ttl_seconds),
            "typ": token_type,
            "iss": self.issuer,
            **claims,
        }
        if self.audience:
            payload["aud"] = self.audience
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode(self, token: str) -> dict[str, Any]:
        """Verify and decode a JWT using the configured claims policy."""
        if not token or not self.secret:
            raise FusionTokenError("A token and signing secret are required")
        try:
            import jwt
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise FusionTokenError("PyJWT is required to verify Bolt tokens") from exc

        options: dict[str, Any] = {"require": ["sub", "iat", "exp"]}
        kwargs: dict[str, Any] = {
            "algorithms": [self.algorithm],
            "options": options,
        }
        if self.issuer:
            kwargs["issuer"] = self.issuer
        if self.audience:
            kwargs["audience"] = self.audience
        try:
            payload = jwt.decode(token, self.secret, **kwargs)
        except Exception as exc:  # noqa: BLE001 - normalize provider errors
            raise FusionTokenError("Invalid or expired Bolt token") from exc
        return dict(payload)

    def bearer_headers(self, token: str) -> dict[str, str]:
        """Return the standard header mapping for a frontend/client request."""
        return {self.authorization_header: f"Bearer {token}"}


def get_token_config(config: BoltTokenConfig | None = None) -> BoltTokenConfig:
    """Return explicit config or the current Django settings-backed config."""
    return config or BoltTokenConfig.from_django_settings()


def extract_bearer_token(headers: Mapping[str, Any]) -> str | None:
    """Extract a bearer token from a case-insensitive header mapping."""
    authorization = next(
        (str(value) for key, value in headers.items() if key.lower() == "authorization"),
        "",
    )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip() or None


def token_payload(
    subject: str,
    *,
    role: str = "viewer",
    ttl_seconds: int | None = None,
    config: BoltTokenConfig | None = None,
    **claims: Any,
) -> dict[str, Any]:
    """Issue a standard token response without exposing signing material."""
    token_config = get_token_config(config)
    ttl = max(1, ttl_seconds or token_config.ttl_seconds)
    refresh_ttl = max(60, token_config.refresh_ttl_seconds)
    return {
        "token": token_config.issue(
            subject,
            role=role,
            ttl_seconds=ttl,
            token_type="access",
            **claims,
        ),
        "refresh_token": token_config.issue(
            subject,
            role=role,
            ttl_seconds=refresh_ttl,
            token_type="refresh",
            **claims,
        ),
        "token_type": "Bearer",
        "expires_in": ttl,
        "refresh_expires_in": refresh_ttl,
        "role": role,
    }


def user_token_payload(
    user: Any,
    *,
    role: str | None = None,
    workspace_id: int | str | None = None,
    config: BoltTokenConfig | None = None,
    ttl_seconds: int | None = None,
) -> dict[str, Any]:
    """Issue an access/refresh pair whose subject is a real Django user.

    The user primary key is the only canonical subject. Role and workspace are
    copied as claims for routing/UX, but protected endpoints must still resolve
    and check the current database user rather than trusting those claims alone.
    """
    if not getattr(user, "is_authenticated", False) or not getattr(user, "is_active", False):
        raise TokenUserError("An active authenticated user is required")
    try:
        profile = user.profile
    except Exception:  # noqa: BLE001 - profile is an optional product relation
        profile = None
    resolved_role = role or getattr(profile, "role", "viewer") or "viewer"
    resolved_workspace = workspace_id if workspace_id is not None else getattr(profile, "workspace_id", None)
    claims: dict[str, Any] = {"user_id": str(user.pk), "email": getattr(user, "email", "")}
    if resolved_workspace is not None:
        claims["workspace_id"] = str(resolved_workspace)
    return token_payload(
        str(user.pk),
        role=resolved_role,
        ttl_seconds=ttl_seconds,
        config=config,
        **claims,
    )


def verify_token_user(
    token: str,
    *,
    config: BoltTokenConfig | None = None,
    required_role: str | set[str] | None = None,
    workspace_id: int | str | None = None,
) -> Any:
    """Verify an access JWT and resolve its subject to an active Django user.

    This is intentionally stricter than signature verification: refresh tokens
    cannot authenticate API calls, inactive/deleted users are rejected, and
    optional role/workspace constraints are checked against the live profile.
    """
    token_config = get_token_config(config)
    claims = token_config.decode(token)
    if claims.get("typ", "access") != "access":
        raise TokenUserError("An access token is required")
    subject = str(claims.get("sub", "")).strip()
    if not subject:
        raise TokenUserError("Token subject is missing")
    try:
        from django.contrib.auth import get_user_model

        user_model = get_user_model()
    except (LookupError, TypeError, ValueError) as exc:
        raise TokenUserError("Token user does not exist") from exc
    try:
        user = user_model.objects.get(pk=subject)
    except user_model.DoesNotExist as exc:
        raise TokenUserError("Token user does not exist") from exc
    if not user.is_active:
        raise TokenUserError("Token user is inactive")

    try:
        profile = user.profile
    except Exception:  # noqa: BLE001 - profile is an optional product relation
        profile = None
    live_role = getattr(profile, "role", "viewer") if profile else "viewer"
    if required_role:
        allowed = {required_role} if isinstance(required_role, str) else set(required_role)
        if live_role not in allowed:
            raise TokenUserError("Token user lacks the required role")
    if workspace_id is not None and str(getattr(profile, "workspace_id", "")) != str(workspace_id):
        raise TokenUserError("Token user is outside the requested workspace")
    claim_workspace = claims.get("workspace_id")
    if (
        claim_workspace is not None
        and getattr(profile, "workspace_id", None) is not None
        and str(claim_workspace) != str(profile.workspace_id)
    ):
        raise TokenUserError("Token workspace claim is stale")
    return user


def verify_request_user(
    request: Any,
    *,
    config: BoltTokenConfig | None = None,
    required_role: str | set[str] | None = None,
    workspace_id: int | str | None = None,
) -> Any:
    """Resolve the authenticated Django user from a bearer request header."""
    token = extract_bearer_token(getattr(request, "headers", {}) or {})
    if not token:
        raise TokenUserError("Bearer access token is required")
    return verify_token_user(
        token,
        config=config,
        required_role=required_role,
        workspace_id=workspace_id,
    )


def refresh_payload(
    refresh_token: str,
    *,
    config: BoltTokenConfig | None = None,
) -> dict[str, Any]:
    """Rotate a valid refresh token into a new access/refresh pair."""
    token_config = get_token_config(config)
    claims = token_config.decode(refresh_token)
    if claims.get("typ") != "refresh":
        raise FusionTokenError("A refresh token is required")
    subject = str(claims.get("sub", "")).strip()
    if not subject:
        raise FusionTokenError("Refresh token subject is missing")
    try:
        from django.contrib.auth import get_user_model

        user_model = get_user_model()
    except (LookupError, TypeError, ValueError) as exc:
        raise TokenUserError("Refresh token user does not exist") from exc
    try:
        user = user_model.objects.get(pk=subject)
    except user_model.DoesNotExist as exc:
        raise TokenUserError("Refresh token user does not exist") from exc
    return user_token_payload(user, config=token_config)


def build_bolt_auth(config: BoltTokenConfig | None = None) -> list[Any]:
    """Construct django-bolt JWT/API-key authentication backends.

    Returns an empty list when django-bolt is unavailable or no backend can be
    configured. The caller can pass the result directly as ``auth=`` on Bolt
    decorators. No token value is logged or serialized.
    """
    try:
        from django_bolt.auth import APIKeyAuthentication, JWTAuthentication
    except (ImportError, ModuleNotFoundError):
        return []

    token_config = get_token_config(config)
    backends: list[Any] = []
    if token_config.secret:
        # The released Bolt API accepts ``secret``; the positional fallback
        # keeps this helper compatible with the older constructor used by the
        # POS sidecar.
        try:
            backends.append(JWTAuthentication(secret=token_config.secret))
        except TypeError:
            backends.append(JWTAuthentication(token_config.secret))
    if token_config.api_key:
        try:
            backends.append(
                APIKeyAuthentication(
                    api_keys={token_config.api_key},
                    header=token_config.api_key_header,
                )
            )
        except TypeError:
            backends.append(APIKeyAuthentication({token_config.api_key}))
    return backends
