---
title: structa.cloud Templates & Apps
description: Main application module for structa.cloud and ctc-research.com — apps, templates, and CI/CD
inclusion: auto
---

# structa.cloud Templates & Apps

## Overview

**structa.cloud** is the umbrella platform and development team name. It covers two production sites:

| Site | Brand | Purpose |
|---|---|---|
| `structa.cloud` | structa.cloud | Tech Bridges Platform — Wagtail CMS, blog, components |
| `ctc-research.com` | CTC Research | LMS & Blog Platform — courses, enrollments, research content |

Both sites share an identical Django project layout, the same plugin set, and a unified frontend build. They are managed as a **uv workspace** under `websites/`.

## Shared Website Structure

Both **structa.cloud** and **ctc-research.com** follow the same layout under `websites/`:

```
websites/
├── structa.cloud/          # structa.cloud — Tech Bridges Platform
│   ├── www/
│   │   ├── apps/           # Django applications (blog, profile, lms, accounts, etc.)
│   │   ├── core/
│   │   │   └── routes.py   # django-osoul routable component tree
│   │   ├── asgi.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── plugins/            # Feature plugins (blog, lms, accounts, profile, components)
│   │   ├── blog/
│   │   ├── lms/
│   │   ├── accounts/
│   │   ├── profile/
│   │   └── components/
│   ├── configs/
│   │   └── settings/       # Dynaconf settings (base, production, testing)
│   ├── templates/          # Root templates
│   │   ├── base_page.html
│   │   ├── base_auth.html
│   │   ├── base_modal.html
│   │   └── base_profile.html
│   ├── assets/
│   │   └── static/         # Site-specific styles only
│   ├── manage.py
│   └── pyproject.toml
│
└── ctc-research.com/       # ctc-research.com — LMS & Blog Platform
    └── ...                 # Identical layout
```

## Template Hierarchy

All templates extend a base template. The hierarchy is:

```
base_page.html          ← public pages (Wagtail + Django views)
base_auth.html          ← authentication pages (allauth)
base_profile.html       ← authenticated user sections (profile, dashboard)
base_modal.html         ← HTMX modal dialogs
base_email.html         ← transactional email templates
```

### Base Template Pattern

```html
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
    {% load static webpack_loader %}
    {% render_bundle 'static' 'CSS' %}
</head>
<body>
    {% include 'partials/header.html' %}
    <main>{% block content %}{% endblock %}</main>
    {% include 'partials/footer.html' %}
    {% render_bundle 'static' 'JS' %}
    {% block scripts %}{% endblock %}
</body>
</html>
```

## Plugin Architecture

Plugins live in `plugins/` and are self-contained Django apps. Each plugin follows this structure:

```
plugins/<name>/
├── __init__.py
├── apps.py             # AppConfig with ready() for signal registration
├── models.py
├── views/              # Class-based views
├── viewsets.py         # django-osoul ModelViewset / ReadonlyModelViewset
├── components.py       # django-osoul FragmentComponent / RoutableComponent
├── urls.py             # Layer 2 URL patterns (manual)
├── admin.py
├── wagtail_hooks.py    # Wagtail snippet registration
├── templates/
│   └── <name>/
│       ├── *.html              # Full-page templates
│       └── fragments/          # HTMX partial templates
├── migrations/
└── tests/
```

### Component Class Selection

Always use the correct base class:

| Scenario | Base Class | Import |
|---|---|---|
| HTMX partial (list, form, etc.) | `FragmentComponent` | `django_osoul.routes` |
| Full-page in `/osoul/` tree | `RoutableComponent` | `django_osoul.routes` |
| Staff CRUD admin | `ModelViewset` | `django_osoul.routes` |
| Read-only list | `ReadonlyModelViewset` | `django_osoul.routes` |
| Legacy profile page (avoid) | `PageHandler` | `django_osoul.site.page_handler` |

**Never** import from `django_osoul.comp.site` — that path is deprecated.

### Fragment Naming Convention

Use dotted `fragment_name` — it maps directly to a template path:

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

## CI/CD Management Commands

### verify_deployment

```bash
python manage.py verify_deployment
```

Checks:
- Docker container health
- Database connectivity
- Static file serving
- URL accessibility

### build_assets

```bash
python manage.py build_assets --no-input
```

Runs `collectstatic` and verifies webpack bundles are present.

## Related Components

- `websites/webpack/` — Shared webpack build (see `webpack-frontend` steering)
- `websites/assets/static/` — Shared static source (JS, fonts, images)
- `websites/bundles/structa.cloud/` — Webpack output for structa.cloud
- `websites/bundles/ctc-research.com/` — Webpack output for ctc-research.com
- `websites/tests/` — Shared test suite covering both sites
- `libs/` — Internal Python libraries (django-grep, django-osoul, django-rseal)
