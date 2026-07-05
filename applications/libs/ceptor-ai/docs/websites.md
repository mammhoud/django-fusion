# Websites — Configuration & Settings

Each website in the Structa Cloud workspace is a self-contained Django application with its own settings, apps, templates, and plugins.

## Website Overview

| Attribute | ctc-research | lms-demo | VResume |
|---|---|---|---|
| **Directory** | `applications/ctc-research/` | `applications/lms-demo/` | `applications/VResume/` |
| **Module** | LMS | LMS | CMS |
| **Default Port** | 5070 | 5071 | 5072 |
| **Site ID** | 1 | 2 | 3 |
| **Domain** | ctc-research.com | structa.cloud | vresume.structa.cloud |
| **Settings File** | `ctc-research/settings.py` | `lms-demo/settings.py` | `VResume/settings.py` |

## Settings Architecture

Each website's `settings.py` follows the same pattern:

```python
# 1. Path configuration — ensure site dirs are on PYTHONPATH
# 2. Site environment — call configure_site_environment()
# 3. Shared settings — from configs.settings import *
# 4. URL/ASGI/WSGI configuration
# 5. Website-specific overrides (WEBSITE_NAME, SITE_ID, LOCAL_APPS, etc.)
```

### Shared Settings Chain

```
configs/settings/__init__.py
  → configs/settings/conf.py      (dynaconf initialization)
  → configs/settings/setup.py      (environment detection)
  → configs/base/__init__.py       (imports all base modules)
      → configs/base/apps.py       (INSTALLED_APPS)
      → configs/base/auth.py       (authentication)
      → configs/base/databases.py  (database config)
      → configs/base/security.py   (security settings)
      → configs/base/middlewares.py (middleware)
      → configs/base/templates.py  (template dirs)
      → configs/base/assets.py     (static/media files)
      → configs/base/i18n.py       (internationalization)
      → configs/base/emails.py     (email backends)
      → configs/base/cache.py      (cache/redis/celery)
      → configs/base/urls.py       (URL config)
      → configs/base/paths.py      (dynamic path resolution)
      → configs/base/admin_site.py (Django admin/Unfold)
      → configs/base/logging.py    (logging config)
      → configs/base/classes.py    (AppRegistry helper)
```

### Site-Specific Settings

Each website overrides:

| Setting | ctc-research | lms-demo | VResume |
|---|---|---|---|
| `WEBSITE_NAME` | ctc-research | lms-demo | vresume |
| `WEBSITE_IDENTIFIER` | ctc-research | lms-demo | vresume |
| `SITE_ID` | 1 | 2 | 3 |
| `ROOT_URLCONF` | www.urls | www.urls | www.urls |
| `ASGI_APPLICATION` | server.application | server.application | server.application |
| `WSGI_APPLICATION` | server.application | server.application | server.application |
| `PROFILE_MODEL` | auth.User | auth.User | auth.User |

## LOCAL_APPS — Per-Site App Lists

Each site defines its own `LOCAL_APPS` inline in its `settings.py`:

### ctc-research
```python
LOCAL_APPS = [
    "www.core",
    "www.core.content.apps.ContentConfig",
    "www.core.handlers.apps.AccountsConfig",
    "plugins.accounts.apps.AccountsConfig",
    "plugins.lms.apps.LmsConfig",
    "plugins.blog.apps.BlogConfig",
    "plugins.products.apps.ProductsConfig",
    "plugins.profile.apps.ProfileConfig",
    "ceptor_ai",
    "django_fusion.analyzer.apps.AnalyzerAppConfig",
]
```

### lms-demo
```python
LOCAL_APPS = [
    "www.core",
    "www.core.content.apps.ContentConfig",
    "www.core.handlers.apps.AccountsConfig",
    "plugins.accounts.apps.AccountsConfig",
    "plugins.lms.apps.LmsConfig",
    "plugins.blog.apps.BlogConfig",
    "plugins.products.apps.ProductsConfig",
    "plugins.profile.apps.ProfileConfig",
    "ceptor_ai",
    "django_fusion.analyzer.apps.AnalyzerAppConfig",
]
```

### VResume
```python
LOCAL_APPS = [
    "www.core",
    "plugins.accounts.apps.AccountsConfig",
    "ceptor_ai",
    "django_fusion.analyzer.apps.AnalyzerAppConfig",
    "pages.home",
    "pages.about",
    "pages.cv",
    "pages.connect",
    "pages.portfolio",
    "pages.blog",
    "pages.events",
]
```

## Silenced System Checks

| Site | Silenced Checks |
|---|---|
| ctc-research | E028, E030, E032, E304, E305, E340 (legacy migration duplicates) |
| lms-demo | E028, E030, E032, E304, E305, E340 (legacy migration duplicates) |
| VResume | None |

## UNFOLD Admin Sidebar — Per-Site Architecture

The Django admin uses [Unfold](https://github.com/unfoldadmin/django-unfold) for modern styling.
The sidebar navigation is configured per-site using a **shared baseline + per-site override** pattern.

### Shared Baseline (`configs/base/admin_site.py`)

All sites start with a minimal generic `UNFOLD` configuration:

```python
UNFOLD = {
    "SITE_HEADER": _("Admin"),
    "SITE_TITLE": _("Site Admin"),
    "SITE_SYMBOL": "school",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,  # Auto-discover registered apps
    },
    # ... shared color palette, display options, dropdowns ...
}
```

Key design decisions:
- **`show_all_applications: True`** — LMS sites (ctc-research, lms-demo) auto-discover their
  registered apps, so they get a correct sidebar without hardcoded model admin links.
- **Generic branding** — "Admin" / "Site Admin" instead of VResume-specific text.
- **No hardcoded navigation** — no model admin URLs that might not exist for a given site.

### VResume Override (`VResume/settings.py`)

After `from configs.settings import *`, VResume mutates the shared `UNFOLD` dict in place
with its curated sidebar and branding:

```python
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD["SITE_HEADER"] = _("VResume")
UNFOLD["SITE_TITLE"] = _("VResume Admin")
UNFOLD["SITE_SYMBOL"] = "person"
UNFOLD["LOGIN"] = {
    "image": lambda request: static("images/avatar/01.jpg"),
}
UNFOLD["SIDEBAR"] = {
    "show_search": True,
    "show_all_applications": False,  # Curated navigation, not auto-discovered
    "navigation": [
        # Dashboard, Content (blog posts/authors/tags),
        # Portfolio (projects/tags), Connect (submissions/campaigns),
        # Site Settings (vResume settings/services/testimonials),
        # Automation (celery beat tasks), Users & Auth
    ],
}
```

### Adding a New Site's Sidebar

1. Keep the shared baseline minimalist (auto-discovery for new sites).
2. In the new site's `settings.py`, mutate `UNFOLD` to override branding and add
   model admin links specific to that site's installed apps.
3. Use `reverse_lazy` for model admin URLs — they only resolve at render time.

### Site UNFOLD Summary

| Site | Sidebar | Branding |
|---|---|---|
| ctc-research | Auto-discovered (shared baseline) | "Admin" / "Site Admin" |
| lms-demo | Auto-discovered (shared baseline) | "Admin" / "Site Admin" |
| VResume | Curated navigation (site override) | "VResume" / "VResume Admin" |

## Celery Beat Schedule — Per-Site Architecture

Periodic tasks are configured per-site so LMS sites don't attempt to import
VResume-specific task modules (`pages.connect.*`, `pages.blog.*`) that don't exist
in their app sets.

### Shared Baseline (`configs/base/celery_beat.py`)

The shared file provides an empty schedule.  It is **not** imported via
`configs/base/__init__.py` — each site defines its own `CELERY_BEAT_SCHEDULE`
in its `settings.py`.

```python
CELERY_BEAT_SCHEDULE = {}
```

### VResume Schedule (`VResume/settings.py`)

VResume defines its own periodic tasks after `from configs.settings import *`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Campaign Tasks (pages.connect — VResume only)
    "process-scheduled-campaigns": {
        "task": "pages.connect.services.campaign_tasks.process_scheduled_campaigns",
        "schedule": 300.0,  # Every 5 minutes
        "options": {"queue": "default", "priority": 5},
    },
    "cleanup-old-campaigns": {
        "task": "pages.connect.services.campaign_tasks.cleanup_old_campaigns",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2:00 AM UTC
        "options": {"queue": "default", "priority": 3},
        "kwargs": {"days_old": 30},
    },
    # Analytics Tasks (pages.blog — VResume only)
    "update-article-engagement-metrics": {
        "task": "pages.blog.services.analytics_tasks.update_article_engagement_metrics",
        "schedule": crontab(hour="*/4", minute=0),
        "options": {"queue": "default", "priority": 2},
    },
    "generate-trending-articles": {
        "task": "pages.blog.services.analytics_tasks.generate_trending_articles",
        "schedule": crontab(hour=0, minute=0),
        "options": {"queue": "default", "priority": 2},
        "kwargs": {"days": 7, "limit": 10},
    },
    "cleanup-old-article-reads": {
        "task": "pages.blog.services.analytics_tasks.cleanup_old_article_reads",
        "schedule": crontab(hour=3, minute=0),
        "options": {"queue": "default", "priority": 1},
        "kwargs": {"days_old": 90},
    },
}
```

### LMS Sites

ctc-research and lms-demo define no periodic tasks.  Their Celery Beat scheduler
runs with an empty database schedule.

### Site Schedule Summary

| Site | Tasks | Task Modules |
|---|---|---|
| ctc-research | None | — |
| lms-demo | None | — |
| VResume | 5 tasks (2 campaign + 3 analytics) | `pages.connect.*`, `pages.blog.*` |

## Running Website Commands

```bash
# From the workspace root (applications/)
cd applications

# Django management commands
uv run ctc-research check
uv run ctc-research migrate
uv run ctc-research runserver

uv run lms-demo check
uv run lms-demo migrate
uv run lms-demo runserver

uv run vresume check
uv run vresume migrate
uv run vresume runserver

# Via Makefile shortcuts
make check WEBSITE=ctc
make run-dev WEBSITE=structa
make tests-website WEBSITE=vresume
```

## Site Directory Structure

Each site follows this layout:

```
<site>/
├── settings.py          # Site-local Django settings
├── manage.py            # Delegates to workspace manage.py
├── server.py            # ASGI/WSGI application
├── __main__.py          # uv run entry point
├── __init__.py
├── www/                 # Site WWW application
│   ├── core/            # Core models and page handlers
│   ├── pages/           # Page-specific apps
│   └── urls.py          # Site URL configuration
├── plugins/             # Site-specific plugins
│   ├── accounts/        # User accounts plugin
│   ├── lms/             # LMS plugin (CTC/LMS only)
│   ├── blog/            # Blog plugin (CTC/LMS only)
│   ├── products/        # Products plugin (CTC/LMS only)
│   └── profile/         # Profile plugin (CTC/LMS only)
├── pages/               # Page apps (VResume only)
│   ├── home/
│   ├── about/
│   ├── cv/
│   ├── connect/
│   ├── portfolio/
│   ├── blog/
│   └── events/
├── assets/              # Site asset files
│   ├── templates/       # Site template overrides
│   ├── static/          # Site static files
│   └── bundles/         # Webpack build output
├── templates/           # Site root templates
├── docker-compose.yml   # Site Docker configuration
├── Dockerfile           # Site Docker image
└── Makefile             # Site Makefile
```
