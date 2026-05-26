---
title: Plugins & Internal Libraries
description: Plugin architecture for structa.cloud and ctc-research.com
inclusion: auto
---

# Plugins & Internal Libraries

## Overview

The `plugins/` directory provides self-contained Django apps that extend site functionality. Both **structa.cloud** and **ctc-research.com** share the same plugin set layout, but their `INSTALLED_APPS` and `AppConfig.name` values diverge in places — these divergences are documented below as known issues.

Plugins communicate via Django signals — never via direct cross-plugin imports.

---

## Active Plugins

| Plugin | ctc-research.com | structa.cloud | Notes |
|---|---|---|---|
| `accounts` | `plugins.accounts` ✅ | `apps.accounts` ⚠️ | structa.cloud has stale `name` in `apps.py` |
| `blog` | present | present | not in `PLUGIN_APPS` on either site |
| `lms` | present | present | not in `PLUGIN_APPS` on either site |
| `profile` | present | present | `AppConfig.name = "apps.profile"` on both (stale) |
| `components` | present | present | not in `PLUGIN_APPS` on either site |

### Known `AppConfig.name` bugs

Both sites have stale `name` values that predate the `plugins/` rename:

| File | Current `name` | Correct `name` |
|---|---|---|
| `structa.cloud/plugins/accounts/apps.py` | `"apps.accounts"` | `"plugins.accounts"` |
| `ctc-research.com/plugins/profile/apps.py` | `"apps.profile"` | `"plugins.profile"` |
| `structa.cloud/plugins/profile/apps.py` | `"apps.profile"` | `"plugins.profile"` |

These do not crash Django (the `label` field controls DB table names) but break `apps.get_app_config("plugins.X")` lookups. Fix when touching those apps.

---

## Plugin Directory Layout

```
plugins/<name>/
├── __init__.py
├── apps.py                 # AppConfig — register signals in ready()
├── models.py               # Django models
├── views/                  # Class-based views (Layer 2 — manual URLs)
│   ├── __init__.py
│   └── *.py
├── viewsets.py             # django-osoul ModelViewset (Layer 3 — /osoul/)
├── components.py           # django-osoul FragmentComponent / RoutableComponent
├── urls.py                 # Layer 2 URL patterns
├── admin.py                # Django admin registration
├── wagtail_hooks.py        # Wagtail snippet / chooser registration
├── signals.py              # Signal definitions and receivers
├── services.py             # Business logic (shared between layers)
├── templates/
│   └── <name>/
│       ├── *.html          # Full-page templates
│       └── fragments/      # HTMX partial templates
├── migrations/
└── tests/
    ├── test_models.py
    └── test_views.py
```

---

## Internal Libraries

Three internal libraries are sourced from GitHub and shared across both sites via the `websites/pyproject.toml` workspace:

```toml
[tool.uv.sources]
django-osoul = { git = "https://github.com/mammhoud/django-osoul", branch = "generic" }
django-rseal = { git = "https://github.com/mammhoud/django-rseal", branch = "generic" }
django-grep  = { git = "https://github.com/mammhoud/django-grep",  branch = "generic" }
```

### django-grep

Health checks, search utilities, debug tools, and management commands.

```python
# Health check endpoint (wired in www/urls.py)
path("health/", include("django_grep.health.urls"))

# Debug URL helpers (wired in www/urls.py)
from django_grep.contrib.debug_tools.common_urls import configure_common_urls
from django_grep.contrib.debug_tools.dev_urls import configure_dev_urls

# Error view handlers
from django_grep.contrib.debug_tools.error_views import handler400, handler403, handler404, handler500

# Superuser auto-creation
python manage.py superuser_auto
```

Health endpoints provided:

| Endpoint | Checks |
|---|---|
| `/health/` | Service running, homepage HTTP 200, content length |
| `/health/assets/` | Static files count, webpack bundles.json, JS/CSS counts |
| `/health/database/` | DB connection, query execution |
| `/health/media/` | Media directory exists and accessible |

### django-osoul

The routing and component framework. Provides the `Site → Application → Viewset` tree that generates all `/osoul/` URLs.

**Key classes:**

```python
from django_osoul.routes import (
    Site,
    Application,
    viewprop,
    RoutableComponent,    # full-page view in /osoul/ tree
    FragmentComponent,    # HTMX-only partial in /osoul/ tree
    ModelViewset,         # staff CRUD
    ReadonlyModelViewset, # read-only list
)
from django_osoul.site.page_handler import ComponentViews, PageHandler
```

**Component hierarchy:**

```
ComponentViews             ← base view (TemplateView + HTMX detection)
    └── PageHandler        ← adds breadcrumbs/sidebar flags (legacy — avoid for new code)
    └── RoutableComponent  ← adds route_path, permission check, menu integration
            └── FragmentComponent  ← adds htmx_only, oob_fragments, paginate_by
```

**Never** import from `django_osoul.comp.site` — that path is deprecated.

**HTMX detection** — always use the canonical helper:

```python
from django_osoul.site._context_mixins import is_htmx_request

if is_htmx_request(request):
    ...
```

**Component class selection:**

| Scenario | Base Class | Import |
|---|---|---|
| HTMX partial (list, form, etc.) | `FragmentComponent` | `django_osoul.routes` |
| Full-page in `/osoul/` tree | `RoutableComponent` | `django_osoul.routes` |
| Staff CRUD admin | `ModelViewset` | `django_osoul.routes` |
| Read-only list | `ReadonlyModelViewset` | `django_osoul.routes` |
| Legacy profile page (avoid) | `PageHandler` | `django_osoul.site.page_handler` |

**Fragment naming convention** — dotted `fragment_name` maps to a template path:

```python
# "blog.fragments.post_list"  →  blog/fragments/post_list.html
class BlogPostListFragment(FragmentComponent):
    fragment_name = "blog.fragments.post_list"
    htmx_only = True
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.published().order_by("-published_at")
```

Do **not** use `fragment_template` — it has been removed.

### django-rseal

Email sending, template rendering, transactional email utilities, and shared enums.

```python
from django_rseal.email import send_template_email
from django_rseal.contrib.enums import Environment, Runtime, Direction, Workflow

send_template_email(
    to="user@example.com",
    subject="Welcome",
    template="emails/welcome.html",
    context={"user": user},
)
```

The `Environment` and `Runtime` enums from `django_rseal.contrib.enums` are used throughout `configs/settings/conf.py` for environment detection.

### Updating Internal Libraries

```bash
# Push changes to all libs
python websites/cli.py push

# Push a single lib
python websites/cli.py push --lib django-osoul --message "fix: add WagtailPageMixin"
```

After pushing, the CLI updates `uv.lock` files with new commit SHAs. Then run `docker compose build --no-cache` to pick up the changes.

---

## Blog Plugin

### Models

- `BlogPost` — title, slug, content, author, tags, categories, published_at, is_published
- `BlogCategory` — name, slug, description
- `BlogTag` — name, slug

### Routing

| Layer | Class | URL | Audience |
|---|---|---|---|
| 1 (Wagtail) | `BlogIndexPage` (RoutablePageMixin) | `/blog/` | Public CMS page |
| 2 (Django) | `BlogPostListView` | `/blog/` | Public fallback |
| 2 (Django) | `BlogPostDetailView` | `/blog/<slug>/` | Public |
| 3 (osoul) | `BlogPostViewset` | `/osoul/blog/posts/` | Staff CRUD |
| 3 (osoul) | `BlogPostListFragment` | `/osoul/blog/posts/list-fragment/` | HTMX partial |
| 3 (osoul) | `BlogPostCreateFragment` | `/osoul/blog/posts/create-fragment/` | HTMX partial |

### Known bug — structa.cloud

```python
# structa.cloud/plugins/blog/viewsets.py
list_search_fields = ("title", "body")   # ← BUG: field is "content", not "body"
```

### Wagtail Snippets

```python
# wagtail_hooks.py
from wagtail.snippets.models import register_snippet

register_snippet(BlogCategoryViewSet)
register_snippet(BlogTagViewSet)
register_snippet(BlogPostViewSet)
```

---

## LMS Plugin

### Models

- `Course` — title, slug, description, instructor, is_published
- `Enrollment` — user, course, enrolled_at, completed_at

### Routing (ctc-research.com only)

| Layer | Class | URL |
|---|---|---|
| 3 (osoul) | `DashboardComponent` | `/osoul/lms/dashboard/` |
| 3 (osoul) | `CourseViewset` | `/osoul/lms/courses/` |
| 3 (osoul) | `EnrollmentViewset` | `/osoul/lms/enrollments/` |
| 3 (osoul) | `CourseListFragment` | `/osoul/lms/courses/list-fragment/` |

structa.cloud has the LMS plugin installed but **no routable component registration** in `www/core/routes.py` yet.

---

## Profile Plugin

### Current State

Profile views are wired in `plugins/profile/urls.py` as plain Django class-based views. They currently import directly from `plugins.profile.views` — no `PageHandler` in the URL wiring itself.

The `AppConfig.name` is `"apps.profile"` on both sites (stale — should be `"plugins.profile"`).

### Known URL duplication

Both `plugins/urls.py` and `plugins/profile/urls.py` contain overlapping profile route definitions (dashboard, profile, settings, etc.). This is the separation violation the allauth-htmx spec is meant to fix.

### Target State (not yet implemented)

```python
# www/core/routes.py — target
class ProfileApp(Application):
    title = "Profile"
    app_name = "profile"

    @viewprop
    def viewsets(self):
        from plugins.profile.components import (
            DashboardComponent,
            ProfileComponent,
            BlogPostCreateFragment,
        )
        return [
            DashboardComponent(),
            ProfileComponent(),
            BlogPostCreateFragment(),
        ]

    def has_view_permission(self, user, obj=None):
        return user.is_authenticated
```

---

## Plugin Configuration

Plugins are registered in `configs/base/` (not directly in `configs/settings/CD/*.py`). The actual `INSTALLED_APPS` list is assembled in `configs/base/__init__.py` or equivalent base config files, not in the per-environment settings.

```python
# configs/base/ — base config (actual structure)
PLUGIN_APPS = [
    "plugins.accounts",   # ctc-research.com only (structa.cloud has stale "apps.accounts")
    # blog, lms, profile, components are loaded via Dynaconf ENV/*.yml, not hardcoded here
]
```

---

## Best Practices

1. **No cross-plugin imports** — use Django signals for inter-plugin communication.
2. **Services layer** — shared queryset logic goes in `services.py`, called by both Layer 2 and Layer 3 views.
3. **Fragment naming** — always use dotted `fragment_name`, never `fragment_template`.
4. **Correct base class** — `FragmentComponent` for HTMX partials, `RoutableComponent` for full pages, `ModelViewset` for staff CRUD.
5. **Wagtail snippets** — register models as snippets in `wagtail_hooks.py`, not in `admin.py`.
6. **Fix stale `AppConfig.name`** — update `"apps.X"` → `"plugins.X"` when touching any plugin's `apps.py`.
7. **Migrations** — include migrations in the plugin directory; use plugin-specific table prefixes.
