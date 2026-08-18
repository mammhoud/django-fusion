# OpenAPI & API Filtering — DF-019

> Source of truth: `src/django_fusion/plugins/apis/openapi.py`,
> `src/django_fusion/plugins/apis/viewsets.py`, and
> `src/django_fusion/plugins/apis/bolt.py`. This doc maps the
> [django-bolt OpenAPI guide](https://bolt.farhana.li/topics/openapi/) onto
> the django-fusion `apis` plugin so the same documentation/filtering
> discipline applies whether the API is served by Django or by a Bolt Rust
> server.

## Status

Two complementary roads exist:

1. **Django-native OpenAPI** — `OpenAPISpec` + `openapi_json` / `openapi_docs`
   (`src/django_fusion/plugins/apis/openapi.py`). Zero extra dependencies,
   works on any gunicorn/uvicorn-served site. This is the road the
   CTC Research / Precis sites use.
2. **Bolt auto-OpenAPI** — `build_bolt_api()` + `OpenAPIConfig`
   (`src/django_fusion/plugins/apis/bolt.py`). Only active when `django_bolt`
   is installed; serves `/docs`, `/docs/openapi.json`, Swagger/Redoc/Scalar
   from the Bolt Rust server.

Both roads answer with the same dual-mode `APISViewMixin.respond` contract
(component HTML in render-first mode, codec JSON in data mode).

## The django-bolt → django-fusion mapping

| django-bolt (from the OpenAPI guide) | django-fusion equivalent |
|---------------------------------------|--------------------------|
| `OpenAPIConfig(title, version, description, enabled, ...)` | `OpenAPISpec(title=..., version=..., description=...)` |
| `@api.get("/users/{id}", summary=..., description=..., tags=[...])` | `spec.add_path(path, "get", summary=..., tags=[...])` |
| `response_model=User` (msgspec.Struct) | `OpenAPISpec.json_response(desc, schema)` + `add_component_schema()` |
| Per-status-code `response_model={200: Item, 404: Error}` | `responses={200: ..., 404: ...}` in `add_path()` |
| Typed query params `q: str, page: int = 1, limit: int = 20` | `params=[{"name": "q", "in": "query", ...}]` + viewset `filter_fields` / `_page()` |
| `include_in_schema=False` to hide an endpoint | Omit the path from the spec |

## Django-native OpenAPI

```python
# projects/.../backend/apps/core/openapi.py
from django_fusion.plugins.apis.openapi import OpenAPISpec

spec = OpenAPISpec(
    title="CTC Research API",
    version="1.0.0",
    description="Evidence, publications, and learning resources.",
)
spec.add_tag("research", "Publications and documents")

spec.add_component_schema("Publication", {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "slug": {"type": "string"},
        "language": {"type": "string"},
        "published_at": {"type": "string", "format": "date-time"},
    },
})

spec.add_path(
    "/apis/research/publications/",
    "get",
    summary="List research publications",
    description="Localized publications, filtered by language.",
    tags=["research"],
    params=[
        {"name": "lang", "in": "query", "schema": {"type": "string", "default": "en"}},
        {"name": "q", "in": "query", "schema": {"type": "string"}},
        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 100}},
        {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
    ],
    responses={
        200: OpenAPISpec.json_response("Publications", {
            "type": "object",
            "properties": {"documents": {"type": "array", "items": OpenAPISpec.ref("Publication")}},
        }),
        404: OpenAPISpec.json_response("Not found"),
    },
    operation_id="listPublications",
)
```

Mount it:

```python
# urls.py
from django.urls import path
from django_fusion.plugins.apis.openapi import openapi_docs, openapi_json
from apps.core.openapi import spec

urlpatterns = [
    path("apis/openapi.json", openapi_json, {"spec": spec}, name="openapi-json"),
    path("apis/docs/", openapi_docs, {"spec": spec}, name="openapi-docs"),
]
```

`/apis/docs/` renders Swagger UI; `/apis/openapi.json` returns the raw
OpenAPI 3.1 document. Pass `?spec_url=<path>` to `openapi_docs` when the JSON
route is not a sibling of the docs route.

## Viewset filtering, search, ordering, pagination

`FusionApiViewset` accepts declarative query surfaces so one subclass exposes
a filterable API without hand-written queryset branches:

```python
class PublicationApiViewset(FusionApiViewset):
    model = Publication
    read_fields = ("id", "title", "slug", "language", "published_at")
    tenant_field = None
    filter_fields = ("language",)          # ?language=en  (exact match)
    search_fields = ("title", "abstract")   # ?q=cohort  (icontains, OR-combined)
    ordering_fields = ("published_at", "title")  # ?ordering=-published_at
    page_size = 50                          # ?limit=50&page=2  (or ?offset=100)
```

| Parameter | Behaviour | Default |
|-----------|-----------|---------|
| `?<field>=<value>` | exact match, only for `filter_fields` | — |
| `?q=` / `?search=` | `icontains` across `search_fields` | — |
| `?ordering=` | comma list of `ordering_fields` (`-` descends) | model default |
| `?limit=` | page size (clamped to `max_page_size`) | `page_size` (100) |
| `?page=` | 1-based page | 1 |
| `?offset=` | 0-based offset (alternative to `page`) | 0 |

Undeclared query parameters are ignored (never raise `FieldError`), so the
surface stays explicit and safe. List responses include `results`, `count`,
`total`, `page`, and `page_size`.

Source: `FusionApiViewset.apply_filters`, `apply_ordering`, `_page`
(`src/django_fusion/plugins/apis/viewsets.py`).

## Bolt auto-OpenAPI (when django_bolt is installed)

```python
from django_fusion.plugins.apis.bolt import build_bolt_api, mount_model_crud

api = build_bolt_api(prefix="/bolt", title="CTC Research API")
if api is not None:
    mount_model_crud(api, Publication, prefix="/publications")
```

`build_bolt_api()` configures `OpenAPIConfig` with the title/version and
serves `/bolt/docs` + `/bolt/docs/openapi.json`. `is_bolt_installed()` gates
the optional import so the same code degrades gracefully when the Rust server
is absent — this mirrors the formint sidecar pattern.

## Choosing a road

- **Django-served site** (Precis, CTC, Loop CRM): use the Django-native
  `OpenAPISpec` + viewset filtering. No second process to run.
- **High-throughput Rust sidecar** (formint professional): use the bolt
  bridge; bolt generates the OpenAPI spec from `response_model`/msgspec types
  automatically.

Do not run both for the same resource — pick one serving road per endpoint and
keep the `/apis/*` vs `/bolt/*` prefixes distinct.
