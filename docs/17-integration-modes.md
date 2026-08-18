# Integration Modes, Health, and Project Boundaries — DF-017

This guide records the supported ways to use django-fusion in a Django/Wagtail
site and the boundaries between reusable library code and deployment-specific
project code.

## 1. Project organization

```text
structa.cloud/
├── libs/django-fusion/
│   ├── src/django_fusion/core/assets/       # canonical asset JSON API
│   ├── src/django_fusion/core/health/       # app, DB, media, asset probes
│   ├── src/django_fusion/comp/templatetags/ # fusion and component tags
│   └── docs/                                # library contracts and examples
├── projects/cms-fusion/backend/
│   ├── apps/                                # CMS models, routes, adapters
│   └── www/urls.py                          # CMS URL mounts
├── projects/precis/precis-main/backend/
│   ├── apps/                                # LMS models, routes, adapters
│   └── www/urls.py                          # LMS URL mounts
└── applications/proxy/
    ├── nginx/                               # shared-media static/media server
    └── traefik/                             # host and path routing
```

**Rule:** reusable request/response behavior belongs in `django-fusion`;
site-specific paths, CDN credentials, storage providers, and proxy mounts stay
in the site or infrastructure layer.

## 2. Mode A — Django templates with webpack loader

Use this mode when Django/Wagtail returns the document or a `TemplateResponse`.
The webpack stats file is read by `django-webpack-loader` and the template emits
the generated bundle tags.

```django
{% load render_bundle from webpack_loader %}
<head>
    {% render_bundle 'fusion' 'css' %}
</head>
<body>
    {{ page_content }}
    {% render_bundle 'fusion' 'js' %}
</body>
```

Typical settings are site-owned because each site has a different bundle
folder and stats file:

```python
WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/precis-lms/",
        "STATS_FILE": BASE_DIR / "assets" / "staticfiles" / "bundles" / "precis-lms" / "webpack-stats.json",
    }
}
```

Use this mode for:

- full-page server rendering;
- Wagtail previews and admin-adjacent pages;
- HTMX responses where the outer document already owns the asset tags.

For HTMX, use the existing fusion rendering pipeline and `TemplateResponse`;
do not return an asset JSON payload in place of the requested fragment.

## 3. Mode B — django-fusion asset JSON API

Use this mode when a decoupled frontend (for example Next.js) owns the page
shell and needs a backend-controlled manifest.

Mount the canonical URL module from the site URL configuration. The path is
site-owned; keep one mount per site and do not add compatibility aliases:

```python
from django.urls import include, path
from django_fusion.core.assets import urls as assets_urls

urlpatterns = [
    path("fusion/assets/", include(assets_urls)),
]
```

Current project mounts are:

| Site | Asset API mount |
|---|---|
| LMS Fusion | `/fusion/assets/` |
| CMS Fusion | `/apis/assets/` |

Endpoints append to the configured mount:

| Endpoint | Response |
|---|---|
| `<mount>/top/` | CSS, fonts, preconnect, inline CSS |
| `<mount>/bottom/` | deferred JS and inline JS |
| `<mount>/manifest/` | combined `top` and `bottom` manifest |

Configure the manifest in Django settings:

```python
FUSION_ASSETS = {
    "top": {"css": ["/static/bundles/site.css"], "fonts": [], "preconnect": []},
    "bottom": {"js": ["/static/bundles/site.js"], "inline_js": []},
}
```

The same manifest can be embedded in a server-rendered document:

```django
{% load fusion_assets %}
{% fusion_assets_manifest %}
```

This writes `window.__FUSION_ASSETS__` and lets a frontend hydrate without a
second request. The API and template tag share `_get_assets_config()`; there
is one source of truth.

## 4. Response selection by use case

| Use case | Return | Asset source |
|---|---|---|
| Full Django page | `TemplateResponse` / normal template | webpack loader tags or fusion tags |
| HTMX/Unpoly fragment | fragment `TemplateResponse` with fusion headers | parent document owns bundles |
| Next.js/SPA page | `JsonResponse` page data | `/api/fusion/assets/manifest/` |
| Health probe | `JsonResponse` with `status`, `checks`, warnings/errors | `django_fusion.core.health` |
| Webhook/API client | explicit JSON API response | asset API only when needed |

Do not mix these contracts: a fragment endpoint should not silently switch to
JSON just because a client also needs assets.

## 5. Health and shared-media boundary

Reusable checks now live in `django_fusion.core.health`:

```python
from django_fusion.core.health import (
    asset_health_check,
    media_health_check,
)
```

The checks preserve the historical response shape:

```json
{
  "status": "ok | degraded | unhealthy",
  "checks": {},
  "warnings": [],
  "errors": []
}
```

`media_health_check` checks `MEDIA_ROOT`, writability, file count, and common
subdirectories. `asset_health_check` checks `STATIC_ROOT`, `MEDIA_ROOT`, the
webpack `STATS_FILE`, and bundle files.

Site-specific CMS/LMS health adapters may remain thin project-layer integrations,
but the shared implementation is canonical in django-fusion. New code should
import directly from django-fusion. Keep these concerns in the project layer:

- S3/CDN credentials and remote availability;
- host-specific `shared-media` routing;
- site-specific required directories;
- deployment policy deciding whether degraded should fail readiness.

The shared Nginx service remains infrastructure, not a Django model or asset
registry. It serves read-only static/media mounts; Django health checks verify
the source roots and generated bundles.

## 6. Remarks and failure modes

- `django-webpack-loader` is optional. Install `django-fusion[webpack]` only
  for the loader mode.
- A missing webpack stats file is normally `degraded`, not an import failure;
  production readiness policy can promote it to a hard failure.
- Keep `/health/` unauthenticated for container probes unless the deployment
  adds a probe token or network restriction.
- The historical `django_fusion.plugins.webpack.assets` compatibility package was
  removed. Import asset views and URL patterns directly from
  `django_fusion.core.assets` and `django_fusion.core.assets.urls`.
- Use `fragment_name` for fragment identity. Do not invent parallel context
  keys such as `fragment`, `name`, or `fragment_slug`.

## 7. Webpack enhancement plan

| Phase | Enhancement | Outcome |
|---|---|---|
| P1 | Keep one canonical manifest reader | API, template tags, and Bolt use identical data |
| P2 | Add `render_bundle` examples to site base templates | predictable SSR output and easier onboarding |
| P2 | Validate stats schema and referenced files in CI | fail early on stale bundles |
| P3 | Component-to-entry analyzer | generate per-component JS/CSS entry points |
| P3 | Dev-server/HMR adapter | faster Django/Wagtail template development |
| P4 | Signed/versioned manifest cache headers | safe CDN caching and controlled rollouts |

Before a build enhancement, run both modes against the same site settings and
verify that top assets load before first paint and bottom scripts remain
non-blocking.

## Related

- [DF-009 Health checks](./09-health.md)
- [DF-016 Assets pipeline](./16-assets.md)
- [DF-005 Routing](./05-routing.md)
- [Structa Cloud django-fusion page](../../docs/projects/libs/django-fusion.md)
