# `django_fusion.analyzer`

> Part of **django-fusion** — Django foundation layer

JSON-based static analyzer for the `{% comp %}` component system. Scans the
project's `TEMPLATES_DIRS`, extracts component + template metadata, and
returns it in a structured JSON shape suitable for visualizers (e.g. the
Structa Customizer).

## Contents

- `apps.py` — Django AppConfig
- `schemas.py` — dataclasses for Component / Template / Page / Prop / Slot / Block
- `scanner.py` — depth-limited filesystem walk honoring `include_extensions` + `exclude_patterns`
- `parser.py` — static regex parser for `{% comp %}`, `{% extends %}`, `{% block %}`
- `views.py` — POST JSON view returning the spec response shape
- `urls.py` — mountable URL configuration

## Request

```http
POST /api/analyzer/
Content-Type: application/json
```

```json
{
  "url": "https://example.com",
  "website_slug": "my-site",
  "include_components": true,
  "include_templates": true,
  "depth": 3,
  "filters": {
    "exclude_patterns": ["admin", "static", "media"],
    "include_extensions": [".html", ".django", ".jinja"]
  }
}
```

## Response

```json
{
  "status": "success",
  "website": {
    "name": "My Site",
    "slug": "my-site",
    "base_url": "https://example.com",
    "analyzed_at": "2026-06-29T12:00:00Z"
  },
  "components": [...],
  "templates": [...],
  "pages": [...],
  "summary": {
    "total_components": 12,
    "total_templates": 24,
    "total_pages": 8
  }
}
```

## Mounting

In the consuming project's `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    path("api/analyzer/", include("django_fusion.analyzer.urls")),
]
```

## Caveats

- **Static analysis only** — `{% comp dynamic_variable_name %}` and template
  expressions cannot be resolved; the parser treats unquoted targets as
  `Dynamic/Unknown` markers (returned as `"path": "<dynamic>"`).
- **Regex-coupled to `{% comp %}` syntax** — if `django_fusion.comp` adds new
  tag syntax (e.g. bracketed kwargs), update `parser.py` accordingly.
- **Performance** — `depth` defaults to 3; raise mindfully on large trees and
  consider wrapping in a Celery task for production.
