---
title: Structa Cloud Full Project Structure
description: Complete specification for building structa.cloud project from scratch
version: "1.0.0"
inclusion: auto
---

# Structa Cloud Full Project Specification

## Project Overview
Build a complete Django project structure for structa.cloud with the following characteristics:
- Modular architecture with www/ directory for application code
- Plugin system for extensibility
- Docker-ready configuration
- CI/CD utilities
- Internationalization support

## Directory Structure

```
structa.cloud/
├── www/                          # Application code (main entry point)
│   ├── __init__.py
│   ├── manage.py                 # Django management script
│   ├── conftest.py               # Pytest configuration
│   ├── asgi.py                   # ASGI entry point
│   ├── urls.py                   # Main URL configuration
│   ├── websocket.py              # WebSocket handler
│   ├── wsgi.py                   # WSGI entry point
│   │
│   ├── alliance/                 # Main application module
│   │   ├── __init__.py
│   │   ├── _typing.py
│   │   ├── asgi.py               # Alliance ASGI entry
│   │   ├── conf.py               # Alliance configuration
│   │   ├── urls.py               # Alliance URL routing
│   │   ├── websocket.py          # Alliance WebSocket
│   │   ├── wsgi.py               # Alliance WSGI
│   │   ├── alliance/             # Alliance sub-module
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   ├── urls.py
│   │   │   └── wsgi.py
│   │   ├── CI/                   # CI/CD utilities
│   │   │   ├── __init__.py
│   │   │   ├── management/
│   │   │   │   └── commands/
│   │   │   │       ├── verify_deployment.py
│   │   │   │       ├── load_fixtures.py
│   │   │   │       ├── validate_templates.py
│   │   │   │       └── build_assets.py
│   │   │   ├── tests/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── conftest.py
│   │   │   │   ├── test_*.py
│   │   │   │   └── ...
│   │   │   └── ...
│   │   └── templates/            # Alliance templates
│   │       ├── base.html
│   │       ├── home.html
│   │       └── ...
│   │
│   ├── apps/                     # Django applications
│   │   ├── __init__.py
│   │   ├── accounts/
│   │   ├── blog/
│   │   ├── content/
│   │   ├── lms/
│   │   └── ...
│   │
│   ├── core/                     # Core settings (not entry points)
│   │   ├── __init__.py
│   │   └── settings/             # Django settings
│   │       ├── __init__.py
│   │       ├── conf.py
│   │       ├── base/
│   │       │   ├── __init__.py
│   │       │   ├── apps.py
│   │       │   ├── paths.py
│   │       │   ├── assets.py
│   │       │   ├── auth.py
│   │       │   ├── emails.py
│   │       │   ├── logging.py
│   │       │   └── storages.py
│   │       ├── ENV/
│   │       │   ├── _core.yml
│   │       │   ├── database.yml
│   │       │   ├── security.yml
│   │       │   └── ...
│   │       └── CD/
│   │           ├── __init__.py
│   │           ├── core.py
│   │           ├── services.py
│   │           └── ...
│   │
│   ├── components/               # Reusable components
│   │   ├── __init__.py
│   │   ├── blocks/
│   │   ├── common/
│   │   ├── contact/
│   │   ├── content/
│   │   └── ...
│   │
│   └── configs/                  # Configuration files
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── readme.md
│
├── plugins/                      # Plugin architecture
│   ├── __init__.py              # Plugin registry
│   ├── base.py                  # Base plugin class
│   ├── loader.py                # Plugin loader
│   ├── hooks.py                 # Hook system
│   ├── signals.py               # Signal system
│   ├── settings.py              # Plugin settings
│   ├── templates/
│   ├── static/
│   └── <plugin_name>/           # Individual plugins
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       ├── admin.py
│       ├── templates/
│       ├── static/
│       ├── tests/
│       └── migrations/
│
├── assets/                       # Static assets
│   ├── bundles/                  # Webpack output
│   │   ├── staticfiles/          # Django static files
│   │   ├── js/
│   │   ├── css/
│   │   ├── images/
│   │   └── fonts/
│   ├── fixtures/                 # JSON fixtures
│   ├── emails/                   # Email CSV files
│   ├── templates/                # HTML templates
│   └── locale/                   # Translation files
│
├── compose/                      # Docker compose
│   ├── nginx/
│   ├── postgres/
│   ├── traefik/
│   └── cache/
│
├── cache/                        # Cache directory
├── logs/                         # Log files
├── webpack/                      # Webpack configuration
│
├── asgi.py                       # Root ASGI (symlink to www/asgi.py)
├── urls.py                       # Root URLs (symlink to www/urls.py)
├── websocket.py                  # Root WebSocket (symlink to www/websocket.py)
├── wsgi.py                       # Root WSGI (symlink to www/wsgi.py)
├── manage.py                     # Root manage.py (symlink to www/manage.py)
├── conftest.py                   # Root conftest.py (symlink to www/conftest.py)
│
├── .dockerignore
├── .env
├── .env.example
├── .github/
├── .gitignore
├── .pylintrc
├── .python-version
├── .ruff.toml
├── CHANGELOG.md
├── COM
├── docker-compose.override.yml
├── docker-compose.test.yml
├── docker-compose.yml
├── LICENSE
├── makefile
├── package.json
├── PROMPTS.md
├── pyproject.toml
├── pytest_simple.ini
├── README.md
├── run_containers.sh
├── secret.key.txt
├── SPECIFICATION.md
└── uv.lock
```

## Core Entry Points

### asgi.py (www/asgi.py)
```python
import os
from django.core.asgi import get_asgi_application
from configs.settings.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings.get("DJANGO_SETTINGS_MODULE"))

django_application = get_asgi_application()

async def application(scope, receive, send):
    if scope["type"] == "http":
        await django_application(scope, receive, send)
    elif scope["type"] == "websocket":
        from www.alliance.websocket import websocket_application
        await websocket_application(scope, receive, send)
    else:
        msg = f"Unknown scope type {scope['type']}"
        raise NotImplementedError(msg)
```

### urls.py (www/urls.py)
```python
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("health/", include("django_grep.health.urls")),
    path("control/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]

urlpatterns += i18n_patterns(
    path("", include("www.apps.urls")),
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)
```

### websocket.py (www/websocket.py)
```python
async def websocket_application(scope, receive, send):
    while True:
        event = await receive()

        if event["type"] == "websocket.connect":
            await send({"type": "websocket.accept"})

        if event["type"] == "websocket.disconnect":
            break

        if event["type"] == "websocket.receive":
            if event["text"] == "ping":
                await send({"type": "websocket.send", "text": "pong!"})
```

## Configuration

### Django Settings (www/configs/settings/__init__.py)
```python
from .CD import *

ROOT_URLCONF = "www.alliance.urls"
WSGI_APPLICATION = settings.get("DJANGO_WSGI_APPLICATION")
ASGI_APPLICATION = settings.get("DJANGO_ASGI_APPLICATION")
```

### Dynaconf Settings (www/configs/settings/ENV/_core.yml)
```yaml
default:
  DJANGO_SETTINGS_MODULE: "configs.settings"
  DJANGO_ASGI_APPLICATION: "www.alliance.asgi:application"
```

### Docker Compose
```yaml
services:
  website:
    environment:
      - APP_MODULE=www.alliance.asgi:application
```

## Management Commands

### verify_deployment.py
Verify deployment health:
- Docker container status
- Database connectivity
- Static file serving
- URL accessibility

### load_fixtures.py
Load JSON fixtures:
- Load from assets/fixtures/
- Handle wagtailcore FK ordering
- Report loading results

### validate_templates.py
Validate Django templates:
- Syntax validation
- Structure validation
- Missing variable detection

### build_assets.py
Build static assets:
- Run webpack bundling
- Run Django collectstatic
- Verify output

## Plugin System

### Base Plugin Class
```python
class BasePlugin:
    name = ""
    version = "1.0.0"

    def __init__(self, config=None):
        self.config = config or {}

    def ready(self):
        pass

    def install(self):
        pass

    def uninstall(self):
        pass

    def get_urls(self):
        return []
```

## Best Practices

1. **Import Structure**
   - Standard library first
   - Third-party imports
   - Django imports
   - Local imports (relative)

2. **Module Organization**
   - Keep www/ directory for application code
   - Use www. prefix for all imports
   - Delegate functionality to appropriate modules

3. **Configuration**
   - Use Dynaconf for hierarchical config
   - Environment variables for sensitive data
   - YAML files for environment-specific settings

4. **Testing**
   - Use pytest for testing
   - Place tests in www/alliance/CI/tests/
   - Use conftest.py for fixtures

5. **Docker**
   - Use APP_MODULE for ASGI entry
   - Volume mount assets directory
   - Use docker-compose for orchestration

## Implementation Steps

1. Create www/ directory structure
2. Create core entry points (asgi.py, urls.py, etc.)
3. Create alliance/ module
4. Create apps/ directory
5. Create configs/ directory
6. Create components/ directory
7. Create plugins/ directory
8. Create assets/ directory structure
9. Create Docker configuration
10. Create management commands
11. Set up testing infrastructure
12. Configure internationalization

## Related Steering Files

- `.kiro/steering/structa-cloud-core.md`
- `.kiro/steering/structa-cloud-alliance.md`
- `.kiro/steering/structa-cloud-plugins.md`
