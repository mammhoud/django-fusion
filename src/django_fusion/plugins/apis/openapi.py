"""OpenAPI documentation for the django-fusion ``apis`` plugin.

Django-bolt auto-serves OpenAPI docs (``/docs``, ``/docs/openapi.json``,
Swagger / Redoc / Scalar / RapiDoc / Stoplight UIs) from a ``BoltAPI`` with an
``OpenAPIConfig``. This module provides the **Django-native equivalent** so a
plain Django/Wagtail site — which is served by gunicorn/uvicorn rather than a
Bolt Rust server — can expose the same contract without a second serving stack:

* :class:`OpenAPISpec` — a small, declarative OpenAPI 3.1 builder with
  summaries, tags, query parameters, and per-status-code response schemas.
* :func:`openapi_json` — a view that returns the raw ``application/json`` spec.
* :func:`openapi_docs` — a minimal HTML shell that loads Swagger UI for the
  configured spec (no build step; one CDN script tag).

The model maps 1:1 onto django-bolt's documented concepts so the same
thinking (``summary``/``description``/``tags``, ``response_model``,
``status_code``, typed query parameters) applies to both roads.

Usage (in a project ``urls.py`` or an ``openapi.py`` module)::

    from django_fusion.plugins.apis.openapi import OpenAPISpec, openapi_json, openapi_docs

    spec = OpenAPISpec(title="CTC Research API", version="1.0.0")
    spec.add_tag("research", "Publications and documents")
    spec.add_path(
        "/apis/research/publications/",
        "get",
        summary="List research publications",
        tags=["research"],
        params=[
            {"name": "lang", "in": "query", "schema": {"type": "string"}},
            {"name": "q", "in": "query", "schema": {"type": "string"}},
            {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 100}},
            {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
        ],
        responses={200: OpenAPISpec.json_response("Publications", {"type": "object"})},
    )

    urlpatterns = [
        path("openapi.json", openapi_json, {"spec": spec}, name="openapi-json"),
        path("docs/", openapi_docs, {"spec": spec}, name="openapi-docs"),
    ]
"""

from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache

__all__ = ["OpenAPISpec", "openapi_json", "openapi_docs"]


class OpenAPISpec:
    """A declarative OpenAPI 3.1 document builder.

    Accumulate ``paths``, ``tags`` and ``components`` and render the finished
    spec with :meth:`as_dict`. The builder intentionally avoids the pydantic /
    ninja-schema dependency so it works even when the heavier API schema
    extras are not installed.
    """

    def __init__(
        self,
        *,
        title: str,
        version: str = "1.0.0",
        description: str = "",
        openapi: str = "3.1.0",
    ) -> None:
        self.title = title
        self.version = version
        self.description = description
        self.openapi = openapi
        self._paths: dict[str, dict[str, Any]] = {}
        self._tags: list[dict[str, str]] = []
        self._components: dict[str, dict[str, Any]] = {"schemas": {}}

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------

    @staticmethod
    def json_response(description: str, schema: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return an ``application/json`` OpenAPI response object."""
        response: dict[str, Any] = {"description": description}
        if schema is not None:
            response["content"] = {"application/json": {"schema": schema}}
        return response

    @staticmethod
    def ref(name: str) -> dict[str, str]:
        """Return a ``$ref`` pointer to a component schema."""
        return {"$ref": f"#/components/schemas/{name}"}

    # ------------------------------------------------------------------
    # Builder
    # ------------------------------------------------------------------

    def add_tag(self, name: str, description: str = "") -> "OpenAPISpec":
        """Register a documentation tag (group) used by paths."""
        if not any(tag["name"] == name for tag in self._tags):
            entry: dict[str, str] = {"name": name}
            if description:
                entry["description"] = description
            self._tags.append(entry)
        return self

    def add_component_schema(self, name: str, schema: dict[str, Any]) -> "OpenAPISpec":
        """Register a reusable component schema (referenced via ``$ref``)."""
        self._components["schemas"][name] = schema
        return self

    def add_path(
        self,
        path: str,
        method: str,
        *,
        summary: str = "",
        description: str = "",
        tags: list[str] | None = None,
        params: list[dict[str, Any]] | None = None,
        request_body: dict[str, Any] | None = None,
        responses: dict[int | str, dict[str, Any]] | None = None,
        operation_id: str | None = None,
    ) -> "OpenAPISpec":
        """Register one operation under *path*/*method*.

        *responses* maps a status code (or ``"default"``) to a full response
        object — build one with :meth:`json_response` or pass the raw dict.
        """
        operation: dict[str, Any] = {
            "responses": {str(code): value for code, value in (responses or {}).items()},
        }
        if summary:
            operation["summary"] = summary
        if description:
            operation["description"] = description
        if tags:
            operation["tags"] = tags
        if params:
            operation["parameters"] = params
        if request_body is not None:
            operation["requestBody"] = request_body
        if operation_id:
            operation["operationId"] = operation_id

        self._paths.setdefault(path, {})[method.lower()] = operation
        return self

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def as_dict(self) -> dict[str, Any]:
        """Return the complete OpenAPI document as a plain dict."""
        document: dict[str, Any] = {
            "openapi": self.openapi,
            "info": {
                "title": self.title,
                "version": self.version,
            },
            "paths": self._paths,
        }
        if self.description:
            document["info"]["description"] = self.description
        if self._tags:
            document["tags"] = self._tags
        if self._components.get("schemas"):
            document["components"] = self._components
        return document

    def as_json(self) -> str:
        """Return the spec serialized as compact JSON."""
        return json.dumps(self.as_dict())


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


def _resolve_spec(spec: Any) -> OpenAPISpec:
    """Resolve the spec from a view kwarg (spec instance or callable)."""
    if callable(spec) and not isinstance(spec, OpenAPISpec):
        return spec()
    return spec


@never_cache
def openapi_json(request: HttpRequest, spec: Any = None) -> JsonResponse:
    """GET — return the OpenAPI document as ``application/json``.

    *spec* is the ``OpenAPISpec`` (or a zero-arg callable returning one)
    passed via ``path(..., {"spec": spec})``.

    Marked ``never_cache`` so the site cache middleware (production enables
    ``UpdateCacheMiddleware``/``FetchFromCacheMiddleware``) never serves a
    stale spec after the declarative spec is edited.
    """
    resolved = _resolve_spec(spec)
    if resolved is None:
        return JsonResponse({"detail": "No OpenAPI spec configured."}, status=404)
    return JsonResponse(resolved.as_dict(), json_dumps_params={"indent": 2})


@never_cache
def openapi_docs(
    request: HttpRequest,
    spec: Any = None,
    spec_url: str | None = None,
) -> HttpResponse:
    """GET — render a minimal Swagger UI shell for the configured spec.

    The spec is served by :func:`openapi_json`; this page only points Swagger
    UI at that URL. Resolve the spec URL in this order:

    1. ``?spec_url=`` query parameter,
    2. ``spec_url`` view kwarg (passed via ``path(..., {"spec_url": ...})``),
    3. ``"openapi.json"`` (relative to the docs page).

    Pass an absolute path (e.g. ``"/apis/openapi.json"``) when the JSON route
    is not a sibling of the docs route.

    Marked ``never_cache`` so the docs shell is never served stale by the site
    cache middleware.
    """
    spec_url = request.GET.get("spec_url") or spec_url or "openapi.json"
    title = "API documentation"
    resolved = _resolve_spec(spec)
    if isinstance(resolved, OpenAPISpec):
        title = f"{resolved.title} — API documentation"

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      SwaggerUIBundle({{
        url: "{spec_url}",
        dom_id: "#swagger-ui",
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout: "BaseLayout"
      }});
    </script>
  </body>
</html>"""
    return HttpResponse(html, content_type="text/html; charset=utf-8")
