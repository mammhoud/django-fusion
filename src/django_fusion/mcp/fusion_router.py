"""django-bolt router exposing django-fusion metadata and health checks.

Import-safe: does not configure Django at import time.  All Django-dependent
operations are deferred until routes are called.

Register on a ``BoltAPI``::

    from django_bolt import BoltAPI
    from django_fusion.mcp.fusion_router import register_fusion_routes

    api = BoltAPI()
    register_fusion_routes(api)

Or build a standalone API::

    from django_fusion.mcp.fusion_router import FusionMCPRouter
    api = FusionMCPRouter().api
"""

from __future__ import annotations

import logging
import os
from importlib import import_module, util
from pathlib import Path
from typing import Any

from django_bolt import BoltAPI
from django_bolt.responses import Response

logger = logging.getLogger(__name__)


def _find_spec(module_name: str) -> Any | None:
    """Return a module spec when an optional dependency is importable."""
    try:
        return util.find_spec(module_name)
    except ModuleNotFoundError:
        return None


def _optional_import(module_name: str) -> Any | None:
    """Import an optional dependency only when it is installed."""
    if _find_spec(module_name) is None:
        return None
    return import_module(module_name)


def _json_error(message: str, status_code: int, **details: Any) -> Response:
    payload = {"ok": False, "error": message, **details}
    return Response(payload, status_code=status_code)


# ---------------------------------------------------------------------------
# Django / django-fusion status helpers
# ---------------------------------------------------------------------------


def _django_status() -> dict[str, Any]:
    if _find_spec("django") is None:
        return {
            "available": False,
            "configured": False,
            "error": "Optional dependency 'django' is not installed.",
        }

    django_conf = import_module("django.conf")
    settings = django_conf.settings
    configured = bool(settings.configured)
    return {
        "available": True,
        "configured": configured,
        "settings_module": os.environ.get("DJANGO_SETTINGS_MODULE"),
        "error": None
        if configured
        else "Django is not configured. Set DJANGO_SETTINGS_MODULE before using Django routes.",
    }


def _django_fusion_info() -> dict[str, Any]:
    if _find_spec("django_fusion") is None:
        return {
            "available": False,
            "error": "Optional package 'django_fusion' is not importable.",
        }
    fusion = import_module("django_fusion")
    return {
        "available": True,
        "version": getattr(fusion, "__version__", "unknown"),
        "path": str(Path(fusion.__file__).parent),
        "modules": ["site", "wagtail", "views", "comp", "routes", "contrib", "web", "health"],
    }


def _django_fusion_viewsets() -> dict[str, Any]:
    if _find_spec("django_fusion") is None:
        return {"available": False, "error": "django-fusion not installed"}
    try:
        viewsets = import_module("django_fusion.site")
        return {
            "available": True,
            "ComponentViews": hasattr(viewsets, "ComponentViews"),
            "PageHandler": hasattr(viewsets, "PageHandler"),
            "HTMXPaginationMixin": hasattr(viewsets, "HTMXPaginationMixin"),
            "ModelViewset": hasattr(viewsets, "ModelViewset"),
            "ReadonlyModelViewset": hasattr(viewsets, "ReadonlyModelViewset"),
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}


def _auth_features() -> dict[str, Any]:
    features = {
        "allauth": _find_spec("allauth") is not None,
        "django_fusion_auth": _find_spec("django_fusion.site.auth") is not None,
        "social_auth": _find_spec("allauth.socialaccount") is not None,
        "mfa": _find_spec("allauth.mfa") is not None,
        "oauth2_provider": _find_spec("oauth2_provider") is not None,
    }
    return {"ok": True, "features": features}


def _optional_dependencies() -> dict[str, bool]:
    return {
        "ceptor_ai": _find_spec("ceptor_ai") is not None,
        "django_fusion": _find_spec("django_fusion") is not None,
        "openai": _find_spec("openai") is not None,
        "allauth": _find_spec("allauth") is not None,
        "django_bolt": _find_spec("django_bolt") is not None,
    }


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------


def register_fusion_routes(api: BoltAPI) -> None:
    """Register django-fusion status and health endpoints on *api*."""

    @api.get("/health", tags=["django-fusion"])
    def health() -> dict[str, Any]:
        return {
            "ok": True,
            "status": "ok",
            "django": _django_status(),
            "optional_dependencies": _optional_dependencies(),
            "auth": _auth_features(),
        }

    @api.get("/django-fusion/info", tags=["django-fusion"])
    def django_fusion_info() -> Any:
        result = _django_fusion_info()
        if not result["available"]:
            return _json_error(result["error"], 503)
        return {"ok": True, **result}

    @api.get("/django-fusion/viewsets", tags=["django-fusion"])
    def django_fusion_viewsets() -> Any:
        result = _django_fusion_viewsets()
        if not result["available"]:
            return _json_error(result["error"], 503)
        return {"ok": True, **result}

    @api.get("/auth/features", tags=["django-fusion"])
    def auth_features() -> Any:
        return _auth_features()


class FusionMCPRouter:
    """Builds a :class:`django_bolt.BoltAPI` with django-fusion status endpoints.

    Usage::

        api = FusionMCPRouter().api
        # …or mount onto an existing API:
        FusionMCPRouter.register(existing_api)
    """

    def __init__(self, *, prefix: str = "", **kwargs: Any) -> None:
        self.api = BoltAPI(prefix=prefix, **kwargs)
        register_fusion_routes(self.api)

    @staticmethod
    def register(api: BoltAPI) -> None:
        """Register the fusion routes onto an existing BoltAPI."""
        register_fusion_routes(api)
