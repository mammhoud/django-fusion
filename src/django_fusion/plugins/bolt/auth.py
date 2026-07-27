"""
Fusion bolt authentication — bridge Django session auth to bolt guards.

``FusionBoltAuthBackend`` reads the Django session (or JWT token) and
attaches ``request.user`` so bolt's ``IsAuthenticated`` guard works
transparently with fusion components.

Usage::

    from django_fusion.plugins.bolt import FusionBoltAuthBackend
    from django_bolt.auth import IsAuthenticated

    @bolt.get("/protected", guards=[IsAuthenticated()], auth=[FusionBoltAuthBackend()])
    def protected_view(request):
        return {"user": str(request.user)}
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("django_fusion.bolt")


class FusionBoltAuthBackend:
    """Bolt authentication backend that reads Django session or JWT.

    Priority:
    1. Django session cookie → ``request.user``
    2. JWT Bearer token (if django-bolt JWT installed)
    3. ``AnonymousUser`` on failure
    """

    def __init__(self):
        self._jwt_backend = None
        try:
            from django_bolt.auth import JWTAuthentication
            self._jwt_backend = JWTAuthentication()
        except Exception:
            pass
            try:
                from django_bolt.auth import JWTAuthentication

                self._jwt_backend = JWTAuthentication()
            except Exception:
                pass

    def authenticate(self, request: Any) -> Any:
        """Authenticate a request and return a user or ``AnonymousUser``.

        This method is called by bolt's middleware stack. It returns the
        authenticated user or ``AnonymousUser`` if authentication fails.
        """
        from django.contrib.auth.models import AnonymousUser

        # 1. Try Django session
        user = self._authenticate_session(request)
        if user is not None:
            return user

        # 2. Try JWT
        user = self._authenticate_jwt(request)
        if user is not None:
            return user

        return AnonymousUser()

    def _authenticate_session(self, request: Any) -> Any | None:
        """Try to get user from Django session."""
        session = getattr(request, "session", None)
        if session is None:
            return None

        try:
            from django.contrib.auth import get_user

            user = get_user(request)
            if user is not None and user.is_authenticated:
                return user
        except Exception as exc:
            logger.debug("Session auth failed: %s", exc)

        return None

    def _authenticate_jwt(self, request: Any) -> Any | None:
        """Try to get user from JWT Bearer token."""
        try:
            from django_bolt.auth import JWTAuthentication

            jwt_backend = JWTAuthentication()
            return jwt_backend.authenticate(request)
        except Exception:
            return None

    def __call__(self, request: Any) -> Any:
        return self.authenticate(request)
