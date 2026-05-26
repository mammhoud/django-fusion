---
title: Django Core Entry Points
description: Core module structure, entry points, and configuration for structa.cloud and ctc-research.com
inclusion: auto
---

# Django Core Entry Points

## Overview

The `www/` directory contains the ASGI/WSGI entry points, URL routing, and WebSocket handler shared by both **structa.cloud** (Tech Bridges Platform) and **ctc-research.com** (LMS & Blog Platform). It is the thin wiring layer — all business logic lives in `plugins/`.

Both sites have an **identical** `www/` layout. Differences are in `plugins/` and `configs/`.

---

## Directory Structure

```
websites/
├── structa.cloud/
│   ├── www/
│   │   ├── asgi.py          # ASGI entry point (HTTP + WebSocket)
│   │   ├── conf.py          # Core configuration loader
│   │   ├── urls.py          # Root URL configuration
│   │   ├── websocket.py     # WebSocket handler
│   │   └── wsgi.py          # WSGI entry point
│   ├── configs/
│   │   ├── base/            # Base config helpers (assets.py, etc.)
│   │   └── settings/
│   │       ├── __init__.py  # Entry point — imports from CD/
│   │       ├── conf.py      # MainSettings (Pydantic + Dynaconf singleton)
│   │       ├── setup.py     # Prints env summary on startup
│   │       └── CD/
│   │           ├── __init__.py   # Environment dispatcher
│   │           ├── core.py       # Fallback / development settings
│   │           ├── demo.py       # Demo / development settings
│   │           └── production.py # Production settings
│   ├── plugins/             # Feature plugins
│   ├── templates/
│   ├── assets/
│   ├── manage.py
│   └── pyproject.toml
│
└── ctc-research.com/        # Identical layout
    └── ...
```

---

## Entry Points

### `www/asgi.py` — identical on both sites

```python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")

from django.core.asgi import get_asgi_application

django_application = get_asgi_application()

from www.websocket import websocket_application  # noqa: E402

async def application(scope, receive, send):
    if scope["type"] == "http":
        await django_application(scope, receive, send)
    elif scope["type"] == "websocket":
        await websocket_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")
```

Key points:
- `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")` — **no** `from configs.settings.conf import settings` before `get_asgi_application()`.
- WebSocket import is **after** `get_asgi_application()` to ensure apps are loaded first.

---

## URL Configuration

### `www/urls.py` — identical on both sites

```python
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django_grep.contrib.debug_tools.common_urls import configure_common_urls
from django_grep.contrib.debug_tools.error_views import handler400, handler403, handler404, handler500
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("health/", include("django_grep.health.urls")),
    path("django-admin/", admin.site.urls),          # ← "django-admin/", NOT "control/" or "admin/"
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]

urlpatterns = configure_common_urls(urlpatterns)     # adds i18n, sitemap, robots.txt

urlpatterns += i18n_patterns(
    path("", include("plugins.urls")),               # ← plugins.urls, NOT www.apps.urls
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)

if settings.DEBUG:
    from django_grep.contrib.debug_tools.dev_urls import configure_dev_urls
    urlpatterns = configure_dev_urls(urlpatterns, settings)
```

Critical facts:
- Admin URL is `"django-admin/"` — **not** `"control/"`.
- The i18n root includes `"plugins.urls"` — **not** `"www.apps.urls"` directly.
- `www.apps.urls` (allauth + pipelines) is included **inside** `plugins/urls.py`, not from the root.

### `plugins/urls.py` — what it actually contains

```python
# Both sites — plugins/urls.py
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("auth/", include("plugins.pipelines_urls", namespace="pipelines")),
]
```

`plugins/urls.py` wires allauth and the legacy `pipelines` namespace. Individual plugin URL files (`plugins/blog/urls.py`, `plugins/profile/urls.py`, etc.) are included from here or from `plugins/pipelines_urls.py`.

---

## Settings Architecture

### Loading chain

```
configs/settings/__init__.py
    └── from .CD import *
            └── configs/settings/CD/__init__.py
                    ├── from configs.base import *          # base config helpers
                    ├── from configs.settings.conf import settings  # MainSettings singleton
                    └── environment dispatch:
                            production/staging  → from .production import *
                            demo/development    → from .demo import *
                            else                → from .core import *

configs/settings/__init__.py (continued)
    ROOT_URLCONF = "www.urls"
    WSGI_APPLICATION = settings.get("DJANGO_WSGI_APPLICATION", "www.wsgi.application")
    ASGI_APPLICATION = settings.get("DJANGO_ASGI_APPLICATION", "www.asgi.application")
```

### Settings files

| File | Purpose |
|---|---|
| `configs/settings/conf.py` | `MainSettings` — Pydantic `BaseSettings` + Dynaconf singleton (`settings`) |
| `configs/settings/setup.py` | Imports `conf.settings`, prints env summary on startup |
| `configs/settings/CD/__init__.py` | Dispatches to `production`, `demo`, or `core` based on `SERVER_ENV` |
| `configs/settings/CD/core.py` | Fallback / bare-minimum settings (imports `configs.base.*`) |
| `configs/settings/CD/demo.py` | Development + demo settings (imports `configs.base.*`) |
| `configs/settings/CD/production.py` | Production overrides |
| `configs/base/` | Shared base config helpers (assets paths, installed apps lists, etc.) |

There is **no** `base.py` or `testing.py` at the `configs/settings/` level. Base config lives in `configs/base/`.

### `MainSettings` (conf.py)

`MainSettings` is a Pydantic `BaseSettings` class that:
- Reads from `.env` file and environment variables.
- Auto-detects Docker/Kubernetes via `/.dockerenv`, `RUNNING_ENV`, etc.
- Reads `secret.key.txt` for `DJANGO_SECRET_KEY`.
- Initialises a **Dynaconf** instance pointing at `configs/settings/ENV/*.yml` files.
- Exposes a `.get(key, default)` method used throughout settings files.

```python
from configs.settings.conf import settings

# Usage in settings files:
DEBUG = settings.DEBUG
SECRET_KEY = settings.DJANGO_SECRET_KEY
DATABASES = {"default": settings.get("DATABASE_URL")}
```

### Key environment variables

| Variable | Values | Purpose |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `configs.settings` | Django settings module (same on both sites) |
| `SERVER_ENV` | `development`, `demo`, `staging`, `production` | Selects settings layer |
| `RUNNING_ENV` | `local`, `docker`, `kubernetes`, `cloud` | Auto-detected; affects paths |
| `DB_HOST` | hostname | PostgreSQL host |
| `REDIS_URL` | `redis://...` | Redis connection |

---

## `apps.accounts` vs `plugins.accounts` — Known Divergence

The two sites have a naming inconsistency in `plugins/accounts/apps.py`:

| Site | `AppConfig.name` |
|---|---|
| `ctc-research.com` | `"plugins.accounts"` ✅ |
| `structa.cloud` | `"apps.accounts"` ⚠️ stale |

The `structa.cloud` value is a stale reference from before the `plugins/` rename. It does not cause a runtime crash (Django uses `label` for DB tables) but it means `apps.get_app_config("plugins.accounts")` fails on structa.cloud. Fix by updating `name = "apps.accounts"` → `name = "plugins.accounts"` in `websites/structa.cloud/plugins/accounts/apps.py`.

---

## Docker Integration

```yaml
# websites/ctc-research.docker-compose.yml
services:
  website:
    container_name: ctc-website
    environment:
      DJANGO_SETTINGS_MODULE: configs.settings
      SERVER_ENV: production
      RUNNING_ENV: docker

# websites/structa.docker-compose.yml
services:
  core:
    container_name: structa-website
    environment:
      DJANGO_SETTINGS_MODULE: configs.settings
      SERVER_ENV: production
      RUNNING_ENV: docker
```

---

## Best Practices

1. **`www/urls.py` stays thin** — no business logic; only health, admin, wagtail, and `plugins.urls`.
2. **Admin URL is `"django-admin/"`** — never change this; it is intentionally non-standard for security.
3. **All plugin URLs go through `plugins/urls.py`** — never include plugin URL files directly from `www/urls.py`.
4. **Settings via `settings.get()`** — never hardcode values that belong in `.env` or `ENV/*.yml`.
5. **`DJANGO_SETTINGS_MODULE` is always `"configs.settings"`** — the `CD/__init__.py` handles environment dispatch internally.

---

## Related Steering Files

- `structa.cloud-templates` — apps, templates, and CI/CD
- `plugins-internal-libs` — plugin architecture and internal libraries
- `cli-makefile` — CLI commands and Makefile targets
