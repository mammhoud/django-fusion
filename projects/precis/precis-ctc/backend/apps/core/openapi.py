"""OpenAPI 3.1 spec for the CTC Research public API surface.

Documents the Astro data contract (``/apis/*`` from
``apps.pages.pages.landing_api``) and the REST resources (``/api/*`` from
``apps.core.api.urls``). Served by django-fusion's ``openapi_json`` /
``openapi_docs`` views — no second serving stack is required.

See ``libs/django-fusion/docs/19-openapi-and-filtering.md`` (DF-019).
"""

from __future__ import annotations

from django_fusion.plugins.apis.openapi import OpenAPISpec

_PAGINATION = [
    {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 100}},
    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
    {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
]

_LANG = {"name": "lang", "in": "query", "schema": {"type": "string", "default": "en"}, "description": "en | sv | fr | de | es | ar | pt-br"}

_Q = {"name": "q", "in": "query", "schema": {"type": "string"}, "description": "Case-insensitive substring search."}

_OBJECT = {"type": "object"}
_LIST = {"type": "array", "items": _OBJECT}


def build_spec() -> OpenAPISpec:
    spec = OpenAPISpec(
        title="CTC Research API",
        version="1.0.0",
        description=(
            "Evidence, publications, and learning resources for the CTC Research "
            "academic medical-research site. The Astro frontend consumes `/apis/*` "
            "data endpoints; REST resources live under `/api/*`."
        ),
    )

    # ── Tags ────────────────────────────────────────────────────────────────
    spec.add_tag("pages", "Landing pages and fragments")
    spec.add_tag("research", "Publications and documents")
    spec.add_tag("courses", "Learning catalogue")
    spec.add_tag("events", "Events calendar")
    spec.add_tag("site", "Navigation, settings, languages, assets")

    # ── Site ────────────────────────────────────────────────────────────────
    spec.add_path("/apis/render-mode/", "get", summary="Report the active render mode", tags=["site"], responses={200: OpenAPISpec.json_response("Render mode", _OBJECT)})
    spec.add_path("/apis/site/settings/", "get", summary="Branding, social and footer settings", tags=["site"], responses={200: OpenAPISpec.json_response("Site settings", _OBJECT)})
    spec.add_path("/apis/navigation/", "get", summary="Header navigation items", tags=["site"], params=[_LANG], responses={200: OpenAPISpec.json_response("Navigation", _OBJECT)})
    spec.add_path("/apis/content/languages/", "get", summary="Seeded language catalogue", tags=["site"], responses={200: OpenAPISpec.json_response("Languages", _OBJECT)})
    spec.add_path("/apis/assets/", "get", summary="Merged asset manifest for the frontend bundler", tags=["site"], responses={200: OpenAPISpec.json_response("Assets", _OBJECT)})

    # ── Pages ────────────────────────────────────────────────────────────────
    spec.add_path("/apis/pages/", "get", summary="List live Wagtail pages", tags=["pages"], responses={200: OpenAPISpec.json_response("Pages", _OBJECT)})
    spec.add_path(
        "/apis/pages/{slug}/",
        "get",
        summary="Page data for a single slug",
        tags=["pages"],
        params=[_LANG, {"name": "slug", "in": "path", "required": True, "schema": {"type": "string"}}],
        responses={200: OpenAPISpec.json_response("Page data", _OBJECT), 404: OpenAPISpec.json_response("Not found")},
    )
    spec.add_path("/fragment/pages/{slug}/", "get", summary="HTMX content-only page fragment", tags=["pages"], params=[{"name": "slug", "in": "path", "required": True, "schema": {"type": "string"}}], responses={200: OpenAPISpec.json_response("HTML fragment", {"type": "string"})})
    spec.add_path("/fragment/ping/", "get", summary="HTMX server-time ping", tags=["pages"], responses={200: OpenAPISpec.json_response("HTML fragment", {"type": "string"})})

    # ── Research / publications ──────────────────────────────────────────────
    spec.add_path(
        "/apis/research/publications/",
        "get",
        summary="List research publications",
        description="Localized publications with search and pagination.",
        tags=["research"],
        params=[_LANG, _Q, *_PAGINATION],
        responses={200: OpenAPISpec.json_response("Publications", _OBJECT)},
        operation_id="listPublications",
    )

    # ── Contact ──────────────────────────────────────────────────────────────
    spec.add_path("/apis/contact/", "get", summary="Contact form fields and methods", tags=["pages"], params=[_LANG], responses={200: OpenAPISpec.json_response("Contact", _OBJECT)})
    spec.add_path("/fragment/contact/", "post", summary="Submit the contact form (HTMX)", tags=["pages"], responses={200: OpenAPISpec.json_response("HTML fragment", {"type": "string"}), 400: OpenAPISpec.json_response("Validation error", {"type": "string"})})

    # ── REST resources ───────────────────────────────────────────────────────
    spec.add_path("/api/courses/", "get", summary="List courses", tags=["courses"], params=[_LANG, _Q, *_PAGINATION], responses={200: OpenAPISpec.json_response("Courses", _OBJECT)})
    spec.add_path("/api/courses/filters/", "get", summary="Course filter facets", tags=["courses"], responses={200: OpenAPISpec.json_response("Filters", _OBJECT)})
    spec.add_path("/api/events/", "get", summary="List events", tags=["events"], params=[*_PAGINATION], responses={200: OpenAPISpec.json_response("Events", _OBJECT)})
    spec.add_path("/api/blog/", "get", summary="List blog posts", tags=["pages"], responses={200: OpenAPISpec.json_response("Blog posts", _OBJECT)})
    spec.add_path("/api/products/", "get", summary="List products", tags=["courses"], responses={200: OpenAPISpec.json_response("Products", _OBJECT)})

    return spec


spec = build_spec()

__all__ = ["spec", "build_spec"]
