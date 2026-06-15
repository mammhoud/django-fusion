# Migration Guide: django-seed → Wagtail CMS + django-unfold

## Overview

This guide documents the migration from the original django-seed foundation to the current production stack: **Wagtail CMS** with **django-unfold** admin interface. The migration is complete — this document serves as a reference for understanding what changed, why it changed, and how to handle future migrations or onboarding.

**Migration Status**: ✅ Complete
**Current Stack**: Wagtail CMS + django-unfold + Django Ninja
**Previous Stack**: django-seed (legacy foundation)

---

## Table of Contents

1. [What Was Migrated](#what-was-migrated)
2. [Architecture: Before and After](#architecture-before-and-after)
3. [Configuration Changes](#configuration-changes)
4. [Breaking Changes](#breaking-changes)
5. [Custom Code Patterns and Rationale](#custom-code-patterns-and-rationale)
6. [Troubleshooting Common Issues](#troubleshooting-common-issues)
7. [Future Migration Considerations](#future-migration-considerations)
8. [Rollback Procedures](#rollback-procedures)

---

## What Was Migrated

### Summary of Changes

| Component | Before (django-seed) | After (Current) | Status |
|-----------|---------------------|-----------------|--------|
| CMS Platform | django-seed (basic) | Wagtail CMS | ✅ Complete |
| Admin Interface | django-seed admin | django-unfold (Bootstrap 5) | ✅ Complete |
| API Framework | None / basic views | Django Ninja | ✅ Complete |
| Authentication | Basic Django auth | django-allauth + JWT | ✅ Complete |
| Frontend CSS | Bootstrap 3 | Bootstrap 5 | ✅ Complete |
| Database | SQLite (dev) | PostgreSQL | ✅ Complete |
| Migrations | Legacy | 267 applied migrations | ✅ Complete |
| Templates | django-seed templates | Custom Bootstrap 5 templates | ✅ Complete |

### What Was Preserved

- All existing database models (no schema changes)
- All existing migrations (267 applied, unchanged)
- All custom business logic in views and utilities
- All API endpoint contracts
- All authentication mechanisms

---

## Architecture: Before and After

### Before (django-seed)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet / Users                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │   Django Application (django-seed)     │
        │   - Basic admin interface              │
        │   - Bootstrap 3 templates              │
        │   - Standard Django views              │
        └────────────────────────────────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │   Database   │
                    │  (SQLite /   │
                    │  PostgreSQL) │
                    └──────────────┘
```

**Characteristics:**
- Monolithic Django application
- django-seed for data generation and scaffolding
- Bootstrap 3 admin templates
- No CMS capabilities
- Basic authentication
- No containerization

### After (Current Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet / Users                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │   Reverse Proxy (Nginx / Traefik)      │
        │   - Host header routing                │
        │   - SSL/TLS termination                │
        └────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
   │  Docsify    │   │  Frontend   │   │  API Backend │
   │  Service    │   │  (Wagtail + │   │ (Django      │
   │ (nginx:     │   │  django-    │   │  Ninja)      │
   │  alpine)    │   │  unfold)    │   │              │
   └─────────────┘   └─────────────┘   └──────────────┘
                             │                    │
                             └────────────────────┘
                                        │
                               ┌──────────────┐
                               │ PostgreSQL + │
                               │    Redis     │
                               └──────────────┘
```

**Characteristics:**
- Wagtail CMS for content management
- django-unfold for modern Bootstrap 5 admin
- Django Ninja for REST API
- Multi-service Docker architecture
- Reverse proxy with domain routing
- Redis caching layer

---

## Configuration Changes

### INSTALLED_APPS

**Before (django-seed):**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_seed',
    # project apps
]
```

**After (current):**
```python
INSTALLED_APPS = [
    # django-unfold must come before django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'unfold.contrib.import_export',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Wagtail CMS
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    'modelcluster',
    'taggit',

    # API
    'ninja',

    # Authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # project apps
]
```

**Key change**: `django_seed` removed; `unfold` must appear before `django.contrib.admin`.

### URL Configuration

**Before:**
```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('your_app.urls')),
]
```

**After:**
```python
# urls.py
from django.contrib import admin
from django.urls import path, include
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('api/', include('your_app.api_urls')),
    path('', include(wagtail_urls)),  # Wagtail catches all remaining URLs
]
```

**Key change**: Wagtail admin at `/admin/`, Django admin moved to `/django-admin/`. Wagtail URL handler added as catch-all.

### Middleware

**Before:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**After:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # added
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',  # added
    'allauth.account.middleware.AccountMiddleware',  # added
    'django_structlog.middlewares.RequestMiddleware',  # added
]
```

### Database Configuration

**Before:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**After:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='project_db'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}
```

### Wagtail-Specific Settings

These settings are new — they did not exist in the django-seed configuration:

```python
# Wagtail settings
WAGTAIL_SITE_NAME = 'Your Project Name'
WAGTAILADMIN_BASE_URL = 'https://site.structa.cloud'
WAGTAILIMAGES_IMAGE_MODEL = 'your_app.CustomImage'  # if using custom image model
WAGTAILDOCS_DOCUMENT_MODEL = 'your_app.CustomDocument'  # if using custom document model

# Search backend
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
    }
}
```

### Caching (New)

Not present in django-seed configuration:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

## Breaking Changes

### 1. Admin URL Changed

- **Before**: `/admin/` → Django admin
- **After**: `/admin/` → Wagtail admin, `/django-admin/` → Django admin

**Impact**: Any bookmarks or hardcoded links to `/admin/` now go to Wagtail admin. Update any scripts or documentation referencing the admin URL.

### 2. django-seed Commands Removed

The following management commands are no longer available:

```bash
# These no longer work:
python manage.py seed          # django-seed command
python manage.py flush_seed    # django-seed command
```

**Replacement**: Use Django fixtures or factory_boy for test data:

```bash
# Load fixtures
python manage.py loaddata fixtures/initial_data.json

# Or use the Django shell with factory_boy
python manage.py shell
>>> from your_app.factories import UserFactory
>>> UserFactory.create_batch(10)
```

### 3. Template Tag Changes

**Before (django-seed):**
```html
{% load seed_tags %}
{% seed_data model="User" count=10 %}
```

**After**: No equivalent — data seeding is done via management commands or fixtures, not template tags.

### 4. Bootstrap 3 → Bootstrap 5

All templates were updated from Bootstrap 3 to Bootstrap 5. Key class changes:

| Bootstrap 3 | Bootstrap 5 | Notes |
|-------------|-------------|-------|
| `col-xs-*` | `col-*` | xs prefix removed |
| `hidden-xs` | `d-none d-sm-block` | Display utilities changed |
| `pull-left` | `float-start` | Float utilities renamed |
| `pull-right` | `float-end` | Float utilities renamed |
| `panel` | `card` | Panel component replaced |
| `well` | `card bg-light` | Well component replaced |
| `btn-default` | `btn-secondary` | Button variant renamed |
| `glyphicons` | Font Awesome / Heroicons | Icon library changed |

### 5. Authentication Flow

**Before**: Basic Django authentication at `/accounts/login/`

**After**: django-allauth handles authentication with additional features:
- Social authentication (Google, GitHub, etc.)
- Email verification
- Password reset via email
- FIDO2 hardware key support

Login URL remains `/accounts/login/` but is now handled by allauth.

---

## Custom Code Patterns and Rationale

### Pattern 1: Wagtail Page Models

**Rationale**: Wagtail uses a page tree model instead of standard Django views for content pages. This provides built-in versioning, preview, and publishing workflow.

```python
# Before (standard Django view + model)
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published = models.BooleanField(default=False)

# After (Wagtail page model)
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel

class BlogPostPage(Page):
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
    ]
```

**Why**: Wagtail page models get versioning, scheduling, preview, and the Wagtail admin editor for free. Standard Django models require custom implementation of these features.

### Pattern 2: django-unfold Admin Registration

**Rationale**: django-unfold requires models to be registered with `ModelAdmin` from `unfold.admin` instead of `django.contrib.admin`.

```python
# Before (standard Django admin)
from django.contrib import admin

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']

# After (django-unfold)
from django.contrib import admin
from unfold.admin import ModelAdmin

@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    list_display = ['name', 'created_at']
    # unfold-specific options
    compressed_fields = True
    warn_unsaved_form = True
```

**Why**: django-unfold's `ModelAdmin` extends Django's with Bootstrap 5 styling and additional UX features. The API is backward-compatible — only the import changes.

### Pattern 3: Django Ninja API Endpoints

**Rationale**: Replaced ad-hoc Django views for API endpoints with Django Ninja for type safety, automatic OpenAPI docs, and better performance.

```python
# Before (standard Django view)
from django.http import JsonResponse
from django.views import View

class UserListView(View):
    def get(self, request):
        users = User.objects.all().values('id', 'username', 'email')
        return JsonResponse({'users': list(users)})

# After (Django Ninja)
from ninja import Router
from typing import List
from .schemas import UserSchema

router = Router()

@router.get('/users', response=List[UserSchema])
def list_users(request):
    return User.objects.all()
```

**Why**: Django Ninja provides automatic request/response validation, OpenAPI documentation at `/api/docs`, and better type safety with minimal boilerplate.

### Pattern 4: Environment Configuration with dynaconf

**Rationale**: Replaced hardcoded settings with dynaconf for environment-aware configuration management.

```python
# Before (hardcoded or basic os.environ)
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
DEBUG = True  # hardcoded

# After (dynaconf)
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix='DJANGO',
    settings_files=['settings.toml', '.secrets.toml'],
    environments=True,
    load_dotenv=True,
)
```

**Why**: dynaconf supports multiple environments (development, staging, production), secret management via Vault, and layered configuration files.

### Pattern 5: Structured Logging

**Rationale**: Replaced print statements and basic logging with django-structlog for structured, queryable log output.

```python
# Before
import logging
logger = logging.getLogger(__name__)
logger.info(f"User {user.id} logged in")

# After
import structlog
logger = structlog.get_logger()
logger.info("user_logged_in", user_id=user.id, username=user.username)
```

**Why**: Structured logs are machine-readable, enabling log aggregation tools (Datadog, ELK, etc.) to query and alert on specific fields.

---

## Troubleshooting Common Issues

### Issue 1: "unfold" not found in INSTALLED_APPS

**Symptom:**
```
django.core.exceptions.ImproperlyConfigured: 'unfold' must be placed before 'django.contrib.admin' in INSTALLED_APPS
```

**Solution:**
```python
INSTALLED_APPS = [
    'unfold',  # Must be FIRST, before django.contrib.admin
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    # ...
    'django.contrib.admin',
    # ...
]
```

### Issue 2: Wagtail migrations not applied

**Symptom:**
```
django.db.utils.ProgrammingError: relation "wagtailcore_page" does not exist
```

**Solution:**
```bash
python manage.py migrate
# Wagtail creates its own tables on first migrate
```

### Issue 3: Admin URL conflict

**Symptom**: Navigating to `/admin/` shows Wagtail admin instead of Django admin.

**Solution**: This is expected behavior. Django admin is at `/django-admin/`. If you need to change this:

```python
# urls.py
urlpatterns = [
    path('admin/', admin.site.urls),           # Django admin
    path('cms/', include(wagtailadmin_urls)),   # Wagtail admin at /cms/
    # ...
]
```

### Issue 4: Static files not loading in production

**Symptom**: CSS/JS files return 404 in production.

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Ensure whitenoise is in MIDDLEWARE (before other middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ...
]

# Configure static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Issue 5: Wagtail images not displaying

**Symptom**: Images uploaded via Wagtail admin don't display on the frontend.

**Solution:**
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# urls.py (development only)
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

In production, configure your web server (Nginx) to serve `/media/` from `MEDIA_ROOT`.

### Issue 6: django-allauth email backend not configured

**Symptom:**
```
ConnectionRefusedError: [Errno 111] Connection refused
```
when trying to send verification emails.

**Solution:**
```python
# For development - print emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production - configure SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
```

### Issue 7: Redis connection refused

**Symptom:**
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

**Solution:**
```bash
# Start Redis (local development)
redis-server

# Or via Docker
docker run -d -p 6379:6379 redis:alpine

# Verify connection
redis-cli ping  # Should return PONG
```

### Issue 8: Migrations conflict after adding Wagtail

**Symptom:**
```
CommandError: Conflicting migrations detected
```

**Solution:**
```bash
# Check for conflicts
python manage.py showmigrations

# Merge conflicting migrations
python manage.py makemigrations --merge

# Apply merged migration
python manage.py migrate
```

---

## Future Migration Considerations

### Upgrading Wagtail

Wagtail follows a regular release cycle. When upgrading:

1. Check the [Wagtail upgrade guide](https://docs.wagtail.org/en/stable/releases/upgrading.html)
2. Review breaking changes in the release notes
3. Run `python manage.py migrate` after upgrading
4. Test the Wagtail admin interface thoroughly
5. Check custom page models for API changes

```bash
# Upgrade Wagtail
pip install --upgrade wagtail

# Check for migration changes
python manage.py showmigrations | grep wagtail

# Apply new migrations
python manage.py migrate
```

### Upgrading django-unfold

django-unfold is actively developed. When upgrading:

1. Review the [changelog](https://github.com/unfoldadmin/django-unfold/blob/main/CHANGELOG.md)
2. Check for changes to `ModelAdmin` API
3. Test all custom admin views and actions
4. Verify custom admin templates still render correctly

### Adding New Services

When adding a new service to the Docker infrastructure:

1. Add service definition to `docker-compose.yaml`
2. Connect service to `app-network`
3. Add routing rule to Nginx configuration
4. Add domain to DNS
5. Update `ALLOWED_HOSTS` in Django settings
6. Document the new service in `docs/deployment/architecture.md`

### Database Migrations Strategy

For future schema changes:

```bash
# Always create migrations for model changes
python manage.py makemigrations your_app

# Review migration before applying
python manage.py sqlmigrate your_app 0002

# Apply in development first
python manage.py migrate

# Test thoroughly before production deployment
```

**Never** edit existing migration files. Create new migrations instead.

### Python Version Upgrades

The project requires Python 3.11+. When upgrading Python:

1. Update `.python-version` file
2. Update Docker base image in Dockerfiles
3. Run full test suite
4. Check for deprecated Python features in codebase
5. Update CI/CD pipeline Python version

---

## Rollback Procedures

### Rolling Back a Failed Deployment

If a deployment fails and you need to roll back:

```bash
# 1. Identify the last working migration
python manage.py showmigrations

# 2. Roll back to previous migration state
python manage.py migrate your_app 0001_previous_migration

# 3. Revert code to previous version
git checkout <previous-commit>

# 4. Restart services
docker-compose down
docker-compose up -d
```

### Rolling Back Wagtail Upgrade

```bash
# 1. Revert Wagtail version
pip install wagtail==<previous-version>

# 2. Roll back Wagtail migrations if needed
python manage.py migrate wagtailcore <previous-migration>

# 3. Restart application
```

### Emergency Rollback Checklist

- [ ] Identify the failing component
- [ ] Check application logs: `docker-compose logs`
- [ ] Roll back database migrations if schema changed
- [ ] Revert code to last known good commit
- [ ] Restart all services
- [ ] Verify health checks pass
- [ ] Notify team of rollback

---

## Related Documentation

- [System Architecture](architecture.md) — Full architecture overview
- [Environment Configuration](environment.md) — Environment variables reference
- [Docker Setup](01-docker-compose-setup.md) — Docker Compose configuration
- [Deployment Procedures](03-deployment-procedures.md) — Step-by-step deployment
- [Troubleshooting](06-troubleshooting.md) — General troubleshooting guide
- [Dependencies Audit](../libraries/dependencies.md) — Full dependency list
