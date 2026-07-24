"""
RobynRequest — wraps Robyn's ``Request`` for django-fusion compatibility.

Provides a Django ``HttpRequest``-compatible interface so django-fusion
viewsets, route handlers, and components can process Robyn requests
without a full Django WSGI/ASGI stack.

Usage::

    from robyn import Request as RobynRequest
    from django_fusion.comp.robyn.request import RobynRequest as FusionRequest

    @app.get("/products")
    async def list_products(request: RobynRequest):
        fusion_req = FusionRequest(request)
        # Now usable with django-fusion views:
        viewset = ProductViewSet()
        return await viewset.list(fusion_req)
"""

from __future__ import annotations

import json as _json
from typing import Any
from urllib.parse import parse_qs

from robyn import Request as _RobynRequest


class RobynRequest:
    """Thin wrapper that makes a Robyn ``Request`` quack like Django's ``HttpRequest``.

    Django views expect ``request.method``, ``request.GET``, ``request.POST``,
    ``request.body``, ``request.path``, ``request.META``, ``request.headers``,
    ``request.session``, ``request.user``, and ``request.build_absolute_uri()``.

    This class provides all of those with reasonable defaults so django-fusion
    components (``Viewset``, ``FragmentComponent``, ``SearchableViewMixin``)
    can operate on Robyn's request object.
    """

    __slots__ = ("_robyn_req", "_body", "_body_read", "_session", "_user")

    def __init__(self, robyn_request: _RobynRequest) -> None:
        self._robyn_req = robyn_request
        self._body: bytes | None = None
        self._body_read: bool = False
        self._session: dict[str, Any] = {}
        self._user: Any = None

    # ── Django HttpRequest interface ──────────────────────────────────

    @property
    def method(self) -> str:
        """HTTP method, uppercased (e.g. ``GET``, ``POST``)."""
        return self._robyn_req.method.upper()

    @property
    def path(self) -> str:
        """Request path without query string."""
        return self._robyn_req.url.path or "/"

    @property
    def path_info(self) -> str:
        """Alias for ``path`` (Django compatibility)."""
        return self.path

    @property
    def GET(self) -> dict[str, list[str]]:
        """Parsed query-string parameters (read-only, Django-compatible ``QueryDict``-like)."""
        return _RobynQueryDict(self._robyn_req.url.query or "")

    @property
    def POST(self) -> dict[str, list[str]]:
        """
        Parsed POST body parameters.

        Only populated when ``Content-Type`` is
        ``application/x-www-form-urlencoded``.  Returns an empty dict
        otherwise — JSON bodies should be parsed via ``self.json()``.
        """
        ct = self.content_type or ""
        if "application/x-www-form-urlencoded" in ct:
            # Body must have been read — callers should await read_body() first
            if self._body is not None:
                return _RobynQueryDict(self._body.decode("utf-8", errors="replace"))
        return _RobynQueryDict("")

    @property
    def body(self) -> bytes:
        """Raw request body bytes (synchronous — must call ``await read_body()`` first)."""
        if self._body is None:
            return b""
        return self._body

    async def read_body(self) -> bytes:
        """Read and cache the request body (async, idempotent)."""
        if not self._body_read:
            try:
                raw = await self._robyn_req.body()
                self._body = raw if isinstance(raw, bytes) else raw.encode("utf-8")
            except Exception:
                self._body = b""
            self._body_read = True
        return self._body

    async def json(self) -> Any:
        """Parse request body as JSON (async)."""
        body = await self.read_body()
        if not body:
            return {}
        return _json.loads(body.decode("utf-8"))

    @property
    def content_type(self) -> str | None:
        """``Content-Type`` header value."""
        return self._robyn_req.headers.get("content-type")

    @property
    def headers(self) -> dict[str, str]:
        """Request headers dict."""
        return {k.lower(): v for k, v in self._robyn_req.headers.items()}

    @property
    def META(self) -> dict[str, str]:
        """Django-compatible ``request.META`` dict."""
        meta: dict[str, str] = {
            "REQUEST_METHOD": self.method,
            "PATH_INFO": self.path,
            "QUERY_STRING": self._robyn_req.url.query or "",
            "SERVER_NAME": "robyn",
            "SERVER_PORT": "0",
            "CONTENT_TYPE": self.content_type or "",
            "CONTENT_LENGTH": str(len(self.body)),
        }
        for key, val in self._robyn_req.headers.items():
            meta_key = "HTTP_" + key.upper().replace("-", "_")
            meta[meta_key] = val
        return meta

    @property
    def session(self) -> dict[str, Any]:
        """Mutable session dict (no Django session backend — pure in-memory)."""
        return self._session

    @property
    def user(self) -> Any:
        """Authenticated user (set by auth middleware)."""
        return self._user

    @user.setter
    def user(self, value: Any) -> None:
        self._user = value

    def build_absolute_uri(self, location: str = "") -> str:
        """Build an absolute URI from a relative path."""
        host = self._robyn_req.headers.get("host", "localhost")
        scheme = "https" if self._robyn_req.headers.get("x-forwarded-proto") == "https" else "http"
        base = f"{scheme}://{host}"
        if location.startswith("/"):
            return f"{base}{location}"
        if location:
            return f"{base}/{location}"
        path = self.path
        query = self._robyn_req.url.query
        uri = f"{base}{path}"
        if query:
            uri += f"?{query}"
        return uri

    def get_host(self) -> str:
        """Return the HTTP host header."""
        return self._robyn_req.headers.get("host", "localhost")

    def get_full_path(self) -> str:
        """Return path + query string."""
        path = self.path
        query = self._robyn_req.url.query
        if query:
            return f"{path}?{query}"
        return path

    # ── Convenience ───────────────────────────────────────────────────

    @property
    def url(self) -> str:
        """The full request URL."""
        return self.build_absolute_uri(self.get_full_path())

    @property
    def scheme(self) -> str:
        """Request scheme (``http`` or ``https``)."""
        return "https" if self._robyn_req.headers.get("x-forwarded-proto") == "https" else "http"

    def __repr__(self) -> str:
        return f"<RobynRequest {self.method} {self.path}>"


# ---------------------------------------------------------------------------
# Internal: Django QueryDict-compatible wrapper
# ---------------------------------------------------------------------------


class _RobynQueryDict(dict):
    """Minimal ``QueryDict``-like dict for ``request.GET`` / ``request.POST``.

    Django views commonly call ``request.GET.get('key')`` and
    ``request.GET.getlist('key')``.  This subclass provides both.
    """

    def __init__(self, query_string: str) -> None:
        super().__init__()
        if query_string:
            parsed = parse_qs(query_string, keep_blank_values=True)
            for key, values in parsed.items():
                self[key] = values

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        """Return the *last* value for ``key`` (matching Django ``QueryDict.get()``)."""
        values = super().get(key)
        if values is None:
            return default
        return values[-1] if values else default

    def getlist(self, key: str, default: Any = None) -> list[str]:
        """Return all values for ``key`` as a list."""
        return list(super().get(key, default or []))

    def __repr__(self) -> str:
        return f"<RobynQueryDict: {dict.__repr__(self)}>"
