# django-fusion Assets and Health Guide

This guide is the monorepo entry point for the shared asset and health
contracts. The detailed library reference is
[`DF-017`](../../libs/django-fusion/docs/17-integration-modes.md).

## Where code belongs

- `libs/django-fusion/src/django_fusion/core/assets/` — canonical asset JSON
  views and URL patterns.
- `libs/django-fusion/src/django_fusion/core/health/` — application, database,
  media, and webpack asset checks.
- `projects/cms-fusion/backend/` and `projects/precis/precis-main/backend/` — site
  settings, URL mounts, and compatibility adapters.
- `application/proxy/` — Traefik and the read-only `shared-proxy` Nginx
  service.

## Choose one response mode

### Server-rendered Django/Wagtail

Use `django-webpack-loader` in templates:

```django
{% load render_bundle from webpack_loader %}
{% render_bundle 'fusion' 'css' %}
{% render_bundle 'fusion' 'js' %}
```

This is the correct path for a full document or a `TemplateResponse` fragment.

### Decoupled frontend

Mount `django_fusion.core.assets.urls` and fetch:

```text
GET /api/fusion/assets/top/
GET /api/fusion/assets/bottom/
GET /api/fusion/assets/manifest/
```

This is the correct path for Next.js or another client that owns document
rendering. It returns JSON and does not replace page or HTMX fragment responses.

## Health checks

```python
from django_fusion.core.health import asset_health_check, media_health_check
```

Existing project modules import these functions so legacy routes and imports
continue working. Project-specific CDN, S3, and proxy checks should remain
adapters.

## Shared-proxy remarks

`shared-proxy` is a proxy/infrastructure service. It mounts static and media
volumes read-only and routes `/static/` and `/media/` through Nginx. It should
not be duplicated inside each Django project. Django checks source roots and
webpack output; the proxy health check remains a deployment concern.

## Validation

```bash
python3 -m pytest libs/django-fusion/tests/test_health_assets.py -q
python3 -m py_compile libs/django-fusion/src/django_fusion/core/assets/*.py \
  libs/django-fusion/src/django_fusion/core/health/*.py
python3 application/scripts/staging/check_markdown_links.py
```

See the library guide for the full response matrix, remarks, and the staged
webpack enhancement plan.
