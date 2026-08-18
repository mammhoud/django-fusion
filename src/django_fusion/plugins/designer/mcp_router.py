"""django-bolt router for the django-fusion interactive designer.

Safe to mount in any BoltAPI: handlers are read-only or pure-generation
and never write to the filesystem or execute raw template source.

Authentication mirrors ``designer/views.py``: when ``FUSION_MCP_DESIGNER_API_KEY``
(or the ``api_key`` constructor argument) is set, every designer endpoint requires
a matching ``X-API-Key`` header.  When no key is configured the router falls back
to localhost-only access (DEBUG-mode anonymous pattern).

Register on a ``BoltAPI``::

    from django_bolt import BoltAPI
    from django_fusion.plugins.designer.mcp_router import DesignerMCPRouter

    api = DesignerMCPRouter(api_key="secret").api

Or use the convenience singleton for no-auth local development::

    from django_fusion.plugins.designer.mcp_router import designer_router
    api = designer_router.api
"""

from __future__ import annotations

import json
import logging
import os
from importlib import import_module
from typing import Any

from django_bolt import BoltAPI
from django_bolt.exceptions import HTTPException
from django_bolt.params import Depends
from django_bolt.responses import Response

from django_fusion.mcp.fusion_router import _find_spec, _json_error

logger = logging.getLogger(__name__)

# All 8 designer tools.  5 have simplified GET endpoints;
# the remaining 3 (website_audit, webapp_enhancement_plan, validate)
# require complex JSON payloads and are available via POST /tools/call.
_ALL_TOOLS = frozenset({
    "designer.component_catalog",
    "designer.wagtail_field",
    "designer.form_scaffold",
    "designer.table_scaffold",
    "designer.preview",
    "designer.website_audit",
    "designer.webapp_enhancement_plan",
    "designer.validate",
})

_HANDLER_ATTRS = {
    "designer.component_catalog": "designer_component_catalog",
    "designer.website_audit": "designer_website_audit",
    "designer.webapp_enhancement_plan": "designer_webapp_enhancement_plan",
    "designer.wagtail_field": "designer_wagtail_field",
    "designer.form_scaffold": "designer_form_scaffold",
    "designer.table_scaffold": "designer_table_scaffold",
    "designer.validate": "designer_validate",
    "designer.preview": "designer_preview",
}

# Module-level caches
_TOOLS_CACHE: dict[str, Any] | None = None
_DESIGNER_MODULE: Any = None


def _get_designer():
    """Lazily import the designer module. Returns None on failure."""
    global _DESIGNER_MODULE
    if _DESIGNER_MODULE is not None:
        return _DESIGNER_MODULE
    if _find_spec("django_fusion.plugins.designer") is None:
        return None
    try:
        _DESIGNER_MODULE = import_module("django_fusion.plugins.designer")
        return _DESIGNER_MODULE
    except Exception:
        return None


def _get_tools() -> dict[str, Any]:
    """Lazily load MCP_DESIGNER_TOOLS from django-fusion."""
    global _TOOLS_CACHE
    if _TOOLS_CACHE is not None:
        return _TOOLS_CACHE
    if _find_spec("django_fusion.plugins.designer.tools") is None:
        _TOOLS_CACHE = {}
        return _TOOLS_CACHE
    try:
        tools_mod = import_module("django_fusion.plugins.designer.tools")
        _TOOLS_CACHE = getattr(tools_mod, "MCP_DESIGNER_TOOLS", {})
        return _TOOLS_CACHE
    except Exception:
        _TOOLS_CACHE = {}
        return _TOOLS_CACHE


def _get_handler(name: str):
    """Return a safe designer handler callable, or None."""
    attr = _HANDLER_ATTRS.get(name)
    if attr is None:
        return None
    mod = _get_designer()
    if mod is None:
        return None
    return getattr(mod, attr, None)


def _resolve_api_key(api_key: str | None = None) -> str | None:
    """Resolve the configured API key from argument, env, or Django setting."""
    if api_key:
        return api_key
    # Check env var (Kilo-compatible)
    env_key = os.environ.get("FUSION_MCP_DESIGNER_API_KEY", "").strip()
    if env_key:
        return env_key
    # Check Django settings (for in-project usage)
    try:
        from django.conf import settings
        from_django = getattr(settings, "FUSION_MCP_DESIGNER_API_KEY", None)
        if from_django:
            return str(from_django).strip()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------


def _make_designer_auth(api_key: str | None = None):
    """Return a django-bolt dependency gating designer endpoints.

    Policy (mirrors ``designer/views.py._is_allowed``):

    * If an API key is configured → requires a matching ``X-API-Key`` header.
    * If no API key is configured → allows localhost callers only, detected
      from the request ``Host`` header (127.0.0.1, ::1, localhost).
    """
    resolved = _resolve_api_key(api_key)

    def _require_auth(request: dict[str, Any]) -> None:
        headers = request.get("headers", {}) or {}

        # API-key mode (production / remote access)
        if resolved:
            provided = headers.get("x-api-key", "")
            if provided != resolved:
                raise HTTPException(status_code=403, detail="Invalid or missing X-API-Key header")
            return

        # Localhost-only mode (development / DEBUG)
        host = (headers.get("host") or "").split(":", 1)[0].strip().lower()
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Designer access requires API-key authentication in production. "
                    "Set FUSION_MCP_DESIGNER_API_KEY and provide it via X-API-Key header."
                ),
            )

    return _require_auth


class _DesignerAuth:
    """Callable dependency that gates designer endpoints (API-key or localhost)."""

    def __init__(self, api_key: str | None = None) -> None:
        self._check = _make_designer_auth(api_key)

    def __call__(self, request: dict[str, Any]) -> None:
        self._check(request)


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------


def register_designer_routes(api: BoltAPI, *, api_key: str | None = None) -> None:
    """Register the django-fusion designer MCP endpoints on *api*."""
    auth = _make_designer_auth(api_key)

    # -- tools/list ---------------------------------------------------------

    @api.get("/designer/tools", tags=["designer"])
    def tools_list(_auth: None = Depends(auth)) -> Any:
        tools = _get_tools()
        if not tools:
            return _json_error(
                "django-fusion designer tools are not available.",
                503,
                hint="Install django-fusion with the optional designer module.",
            )
        listed = {name: meta for name, meta in tools.items() if name in _ALL_TOOLS}
        return {
            "ok": True,
            "tools": [
                {"name": name, **meta} for name, meta in listed.items()
            ],
        }

    # -- tools/call (JSON-RPC POST) ----------------------------------------

    @api.post("/designer/tools/call", tags=["designer"])
    def tools_call(request: dict[str, Any], _auth: None = Depends(auth)) -> Any:
        """JSON-RPC POST endpoint for all 8 designer tools.

        Accepts::

            {
              "jsonrpc": "2.0",
              "id": 1,
              "method": "tools/call",
              "params": {
                "name": "designer.website_audit",
                "arguments": {"project": "my-project", "sections": [{"name": "hero", "kind": "hero"}]}
              }
            }

        Returns MCP-compliant ``{"jsonrpc": "2.0", "id": …, "result": {…}}``
        on success or ``{"jsonrpc": "2.0", "id": …, "error": {…}}`` on failure.
        """
        raw = request.get("body", b"")
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8", "replace")
        try:
            body = json.loads(raw) if raw else {}
        except (TypeError, ValueError):
            body = None

        request_id = (body or {}).get("id")
        if not isinstance(body, dict):
            return Response(
                {"jsonrpc": "2.0", "id": request_id, "error": {"message": "Invalid JSON-RPC body"}},
                status_code=400,
            )
        if body.get("jsonrpc") != "2.0":
            return Response(
                {"jsonrpc": "2.0", "id": request_id, "error": {"message": "jsonrpc must be '2.0'"}},
                status_code=400,
            )
        if body.get("method") != "tools/call":
            return Response(
                {"jsonrpc": "2.0", "id": request_id, "error": {"message": "method must be tools/call"}},
                status_code=400,
            )
        params = body.get("params", {})
        if not isinstance(params, dict):
            return Response(
                {"jsonrpc": "2.0", "id": request_id, "error": {"message": "params must be an object"}},
                status_code=400,
            )
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(arguments, dict):
            return Response(
                {"jsonrpc": "2.0", "id": request_id, "error": {"message": "arguments must be an object"}},
                status_code=400,
            )

        handler = _get_handler(name)
        if handler is None:
            return Response(
                {"jsonrpc": "2.0", "id": request_id, "error": {"message": f"Unknown designer tool: {name}"}},
                status_code=404,
            )
        try:
            result = handler(**arguments)
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except (TypeError, ValueError) as exc:
            return Response(
                {"jsonrpc": "2.0", "id": request_id, "error": {"message": str(exc)}},
                status_code=400,
            )
        except Exception:
            logger.exception("designer.tools/call failed for %s", name)
            return Response(
                {"jsonrpc": "2.0", "id": request_id, "error": {"message": "Designer tool failed"}},
                status_code=500,
            )

    # -- designer.component_catalog ----------------------------------------

    @api.get("/designer/component-catalog", tags=["designer"])
    def component_catalog(query: str = "", limit: int = 50, _auth: None = Depends(auth)) -> Any:
        handler = _get_handler("designer.component_catalog")
        if handler is None:
            return _json_error("designer.component_catalog is not available.", 503)
        try:
            result = handler(query=query, limit=limit)
            return {"ok": True, **result}
        except (TypeError, ValueError) as exc:
            return _json_error(str(exc), 400)
        except Exception:
            logger.exception("designer.component_catalog failed")
            return _json_error("Designer tool failed", 500)

    # -- designer.wagtail_field --------------------------------------------

    @api.get("/designer/wagtail-field", tags=["designer"])
    def wagtail_field(
        field_type: str,
        name: str,
        label: str = "",
        required: bool = False,
        help_text: str = "",
        _auth: None = Depends(auth),
    ) -> Any:
        handler = _get_handler("designer.wagtail_field")
        if handler is None:
            return _json_error("designer.wagtail_field is not available.", 503)
        try:
            result = handler(
                field_type=field_type,
                name=name,
                label=label,
                required=required,
                help_text=help_text,
            )
            return {"ok": True, **result}
        except (TypeError, ValueError) as exc:
            return _json_error(str(exc), 400)
        except Exception:
            logger.exception("designer.wagtail_field failed")
            return _json_error("Designer tool failed", 500)

    # -- designer.form_scaffold --------------------------------------------

    @api.get("/designer/form-scaffold", tags=["designer"])
    def form_scaffold(class_name: str, style_framework: str = "bootstrap", _auth: None = Depends(auth)) -> Any:
        handler = _get_handler("designer.form_scaffold")
        if handler is None:
            return _json_error("designer.form_scaffold is not available.", 503)
        try:
            result = handler(
                class_name=class_name,
                fields=[],
                base="BaseStyledForm",
                style_framework=style_framework,
            )
            return {"ok": True, **result}
        except (TypeError, ValueError) as exc:
            return _json_error(str(exc), 400)
        except Exception:
            logger.exception("designer.form_scaffold failed")
            return _json_error("Designer tool failed", 500)

    # -- designer.table_scaffold -------------------------------------------

    @api.get("/designer/table-scaffold", tags=["designer"])
    def table_scaffold(class_name: str, _auth: None = Depends(auth)) -> Any:
        handler = _get_handler("designer.table_scaffold")
        if handler is None:
            return _json_error("designer.table_scaffold is not available.", 503)
        try:
            result = handler(class_name=class_name, columns=[], base="BaseTable")
            return {"ok": True, **result}
        except (TypeError, ValueError) as exc:
            return _json_error(str(exc), 400)
        except Exception:
            logger.exception("designer.table_scaffold failed")
            return _json_error("Designer tool failed", 500)

    # -- designer.preview --------------------------------------------------

    @api.get("/designer/preview", tags=["designer"])
    def preview(name: str, max_chars: int = 20000, _auth: None = Depends(auth)) -> Any:
        handler = _get_handler("designer.preview")
        if handler is None:
            return _json_error("designer.preview is not available.", 503)
        try:
            result = handler(name=name, props={}, max_chars=max_chars)
            return {"ok": True, **result}
        except (TypeError, ValueError) as exc:
            return _json_error(str(exc), 400)
        except Exception:
            logger.exception("designer.preview failed")
            return _json_error("Designer tool failed", 500)


class DesignerMCPRouter:
    """Builds a :class:`django_bolt.BoltAPI` exposing the designer as MCP endpoints.

    Parameters
    ----------
    api_key : str | None
        Pre-shared key for remote access.  If ``None`` (default), the router
        resolves ``FUSION_MCP_DESIGNER_API_KEY`` from the environment or
        Django settings.  When no key is found, only localhost callers are
        permitted (development-safe default).

    Mount with::

        api = DesignerMCPRouter(api_key="my-secret").api
    """

    _AUTH = _DesignerAuth

    def __init__(self, *, api_key: str | None = None, prefix: str = "", **kwargs: Any) -> None:
        self.api = BoltAPI(prefix=prefix, **kwargs)
        self._auth = self._AUTH(api_key)
        register_designer_routes(self.api, api_key=api_key)

    @staticmethod
    def register(api: BoltAPI, *, api_key: str | None = None) -> None:
        """Register the designer routes onto an existing BoltAPI."""
        register_designer_routes(api, api_key=api_key)


# Convenience singleton for simple mounting (no auth — localhost-only fallback).
# Lazily constructed so importing this module does not require Django settings.
_designer_router: Any = None


def __getattr__(name: str) -> Any:
    global _designer_router
    if name == "designer_router":
        if _designer_router is None:
            _designer_router = DesignerMCPRouter()
        return _designer_router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
