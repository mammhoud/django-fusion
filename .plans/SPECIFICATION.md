# websites/structa.cloud Specification

## Project Overview

websites/structa.cloud is a Django-based web application with a modular architecture supporting:
- Core Django configuration
- Content copying/duplication
- Plugin system
- Multiple applications (accounts, blog, lms)

## Directory Structure

```
websites/structa.cloud/
├── core/              # Django core configuration
│   ├── asgi.py        # ASGI entry point
│   ├── wsgi.py        # WSGI entry point
│   ├── urls.py        # Main URL configuration
│   └── conf.py        # Core configuration
│
├── copy/              # Copy/duplication utilities
│   ├── copier.py      # Content copying utilities
│   ├── templates/     # Copy templates
│   └── management/    # Copy management commands
│       └── commands/
│           └── copy_content.py
│
├── plugins/           # Plugin system
│   ├── base.py        # Base plugin class
│   ├── manager.py     # Plugin manager
│   ├── registry.py    # Plugin registry
│   ├── templates/     # Plugin templates
│   └── management/    # Plugin management commands
│       └── commands/
│           ├── list_plugins.py
│           ├── enable_plugin.py
│           └── disable_plugin.py
│
├── www/               # Main application directory
│   ├── apps/          # Django applications
│   │   ├── __init__.py
│   │   ├── accounts/  # User accounts
│   │   ├── blog/      # Blog application
│   │   └── lms/       # Learning management
│   │
│   ├── components/    # Reusable components
│   │   ├── blocks/    # Wagtail blocks
│   │   ├── common/    # Common components
│   │   └── content/   # Content components
│   │
│   ├── configs/       # Django configuration
│   │   ├── base/      # Base configuration
│   │   │   ├── apps.py
│   │   │   ├── assets.py
│   │   │   ├── auth.py
│   │   │   ├── emails.py
│   │   │   ├── logging.py
│   │   │   ├── storages.py
│   │   │   └── paths.py
│   │   │
│   │   └── settings/  # Settings configuration
│   │       ├── __init__.py
│   │       ├── conf.py
│   │       └── ENV/
│   │           ├── _core.yml
│   │           ├── database.yml
│   │           ├── security.yml
│   │           └── .secrets.yml
│   │
│   ├── CI/            # CI/CD and testing
│   │   ├── tests/     # Integration tests
│   │   ├── management/commands/
│   │   │   └── verify_deployment.py
│   │   └── utils.py   # CI utilities
│   │
│   ├── templates/     # Templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── blog/
│   │   └── lms/
│   │
│   ├── asgi.py        # ASGI entry point (wrapper)
│   ├── urls.py        # URL configuration (wrapper)
│   ├── manage.py      # Django management script
│   └── conftest.py    # Pytest configuration
│
├── assets/            # Static assets
│   ├── bundles/       # Webpack output
│   │   ├── staticfiles/
│   │   ├── js/
│   │   ├── css/
│   │   ├── images/
│   │   └── fonts/
│   ├── fixtures/      # JSON fixtures
│   ├── emails/        # Email CSV files
│   └── locale/        # Translation files
│
├── compose/           # Docker compose
│   ├── nginx/
│   ├── postgres/
│   └── traefik/
│
├── cache/             # Cache directory
├── logs/              # Log files
├── webpack/           # Webpack configuration
└── docs/              # Documentation
```

## Core Module

### Purpose
The `core/` module contains Django's entry points and core configuration, separate from the application code.

### Files

#### asgi.py
```python
import os

from django.core.asgi import get_asgi_application

from configs.settings.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings.get("DJANGO_SETTINGS_MODULE"))
django_application = get_asgi_application()

from www.websocket import websocket_application

async def application(scope, receive, send):
    if scope["type"] == "http":
        await django_application(scope, receive, send)
    elif scope["type"] == "websocket":
        await websocket_application(scope, receive, send)
    else:
        msg = f"Unknown scope type {scope['type']}"
        raise NotImplementedError(msg)
```

#### urls.py
```python
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django_rseal.contrib.debug_tools.common_urls import configure_common_urls
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("health/", include("django_grep.health.urls")),
    path("control/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]

urlpatterns = configure_common_urls(urlpatterns)

urlpatterns += i18n_patterns(
    path("", include("www.apps.urls")),
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)

if settings.DEBUG:
    from django_rseal.contrib.debug_tools.dev_urls import configure_dev_urls
    urlpatterns = configure_dev_urls(urlpatterns, settings)
```

## Copy Module

### Purpose
The `copy/` module provides utilities for copying and duplicating content.

### Structure
```
copy/
├── copier.py          # Main copying utilities
├── templates/         # Copy templates
└── management/
    └── commands/
        └── copy_content.py
```

## Plugins Module

### Purpose
The `plugins/` module provides an extensible plugin system.

### Structure
```
plugins/
├── base.py            # Base plugin class
├── manager.py         # Plugin manager
├── registry.py        # Plugin registry
├── templates/         # Plugin templates
└── management/
    └── commands/
        ├── list_plugins.py
        ├── enable_plugin.py
        └── disable_plugin.py
```

### Example Plugin
```python
from plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    name = "My Plugin"
    version = "1.0.0"

    def enable(self):
        # Enable logic
        pass

    def disable(self):
        # Disable logic
        pass
```

## WWW Module (Main Application)

### Purpose
The `www/` module contains the main application code, including apps, components, and configurations.

### Apps Structure
```
www/apps/
├── __init__.py
├── accounts/
│   ├── __init__.py
│   ├── models/
│   ├── views/
│   ├── urls.py
│   ├── apps.py
│   └── tests/
├── blog/
│   ├── __init__.py
│   ├── models/
│   ├── views/
│   ├── urls.py
│   ├── apps.py
│   └── tests/
└── lms/
    ├── __init__.py
    ├── models/
    ├── views/
    ├── urls.py
    ├── apps.py
    └── tests/
```

### Components Structure
```
www/components/
├── blocks/
│   ├── content/
│   ├── media/
│   └── contact/
├── common/
└── content/
```

### Configuration Structure
```
www/configs/
├── base/
│   ├── apps.py        # INSTALLED_APPS
│   ├── assets.py      # Static files
│   ├── auth.py        # Authentication
│   ├── emails.py      # Email settings
│   ├── logging.py     # Logging
│   ├── storages.py    # Storage
│   └── paths.py       # Path configuration
└── settings/
    ├── __init__.py    # Settings entry point
    ├── conf.py        # Settings configuration
    └── ENV/
        ├── _core.yml
        ├── database.yml
        ├── security.yml
        └── .secrets.yml
```

## Configuration

### Django Settings
```python
# www/configs/settings/__init__.py
from .CD import *

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = settings.get("DJANGO_WSGI_APPLICATION")
ASGI_APPLICATION = settings.get("DJANGO_ASGI_APPLICATION")
```

### Dynaconf Settings
```yaml
# www/configs/settings/ENV/_core.yml
DJANGO_ASGI_APPLICATION: "core.asgi:application"
```

### Docker Compose
```yaml
# docker-compose.yml
APP_MODULE: "core.asgi:application"
```

## Management Commands

### build_assets.py
Build webpack bundles and run collectstatic.

```bash
python manage.py build_assets
python manage.py build_assets --webpack-only
python manage.py build_assets --collectstatic-only
python manage.py build_assets --production
```

### verify_deployment.py
Verify deployment configuration.

```bash
python manage.py verify_deployment
```

### load_fixtures.py
Load fixture data.

```bash
python manage.py load_fixtures
python manage.py load_fixtures --fixtures=wagtail_pages_dump.json
```

### validate_templates.py
Validate Django templates.

```bash
python manage.py validate_templates
python manage.py validate_templates --all
```

### copy_content.py
Copy content between sources.

```bash
python manage.py copy_content --source=page1 --target=page2
```

### manage_plugins.py
Manage plugins.

```bash
python manage.py list_plugins
python manage.py enable_plugin my_plugin
python manage.py disable_plugin my_plugin
```

## Asset Structure

### Static Files
```
assets/
├── bundles/
│   ├── staticfiles/   # Django collectstatic output
│   ├── js/            # Webpack JS bundles
│   ├── css/           # Webpack CSS bundles
│   ├── images/        # Image assets
│   └── fonts/         # Font assets
├── fixtures/          # JSON fixtures
├── emails/            # Email CSV files
└── locale/            # Translation files
```

### Build Command
```bash
python manage.py build_assets
```

This will:
1. Run webpack to generate bundles
2. Run collectstatic to collect static files
3. Verify the output

## Testing

### Test Structure
```
tests/
├── ci/                # CI/CD tests
├── apps/              # App tests
├── unit/              # Unit tests
├── integration/       # Integration tests
├── selenium/          # Selenium tests
├── email/             # Email tests
├── docker/            # Docker tests
└── performance/       # Performance tests
```

### Running Tests
```bash
pytest tests/
pytest tests/ci/
pytest tests/apps/
```

## Deployment

### Docker Build
```bash
docker compose build
docker compose up -d
```

### Deployment Verification
```bash
python manage.py verify_deployment
```

## Benefits of This Structure

1. **Clear Separation**
   - Core configuration separate from application code
   - Copy utilities isolated
   - Plugin system extensible

2. **Modular Design**
   - Easy to add new apps
   - Simple to create plugins
   - Flexible content copying

3. **Production Ready**
   - Docker-optimized structure
   - Clear build process
   - Deployment verification

4. **Maintainable**
   - Organized configuration
   - Clear module boundaries
   - Comprehensive documentation

## Migration from Previous Structure

If migrating from a different structure:

1. Move Django entry points to `core/`
2. Move copy utilities to `copy/`
3. Move plugin system to `plugins/`
4. Move application code to `www/`
5. Update all imports to use `www.apps.*`, `www.core.*`, etc.
6. Update Django settings to point to `core.urls`
7. Update Docker configuration to use `core.asgi:application`

## Conclusion

This structure provides a clean, modular, and production-ready architecture for websites/structa.cloud with clear separation of concerns and extensibility through plugins.

## Current State & Recommended Minimal Architecture

Summary of current state (as of this edit):

- The repository contains two site directories (`ctc-research.com` and `structa.cloud`) under `websites/` along with a canonical `websites/configs` used as the single source of truth for settings.
- Some per-site `configs` directories existed and a plan has been added to merge them into `websites/configs` (see `DEPLOY_CHECKLIST.md`).
- Asset build orchestration is provided by `manage.py build_assets` which runs npm scripts and `collectstatic`.
- A `.plans` directory contains deployment checklists, specs, and scripts to validate and organize work.

Recommended minimal architecture and next artifacts:

- See `MINIMAL_ARCH.md` for a concise, production-ready architecture and operational checklist.
- Use `ENHANCED_PROMPTS.md` to automate audit, Dockerfile/compose generation, CI config, and Results reporting.
- Run `./check_all_plans.sh` inside `.plans` to generate `UNDONE_TASKS.md` and prioritize work items.

Additions in this repo related to these recommendations have been created under `.plans/`:

- `MINIMAL_ARCH.md` — minimal architecture and operational checks.
- `ENHANCED_PROMPTS.md` — LLM prompts for automation and guidance.
- `DEPLOY_PROMPTS_MERGED.md` — merged summary of checklist and prompts.

