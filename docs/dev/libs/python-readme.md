# 🐍 Python/Django — Core Backend

Django monorepo with multiple site projects, shared libraries, and a component framework.

## Use Cases

### 1. Django Site Management (`projects/<site>/`)
- **Purpose:** Run and maintain multiple Django sites (precis-ctc, lms, VResume) from a shared monorepo — each with its own templates, plugins, Django apps, and settings
- **Key traits:** Single `make` command with `WEBSITE=...` dispatches checks, tests, migrations; per-site logical databases in shared PostgreSQL

### 2. Component Framework (`django-fusion`)
- **Purpose:** Build reusable UI components with `{% comp "name" %}` template tags, routed viewsets, and HTMX fragment rendering — reducing template duplication across sites
- **Key traits:** Component namespace dot-notation (`contact.sections.form`); include-path tracking via `register_include_path()`; fragment detection for HTMX swap targets

### 3. Shared Templates & Assets (`projects/assets/`)
- **Purpose:** Maintain cross-site template base (layouts, components, blocks) and static files (CSS, JS, locale) that all sites inherit, with override layers per site
- **Key traits:** 10-layer template resolution order; BEM-style CSS; plugins/templates/ is the canonical source for reusable partials

### 4. Multi-Site Orchestration (`projects/configs/`)
- **Purpose:** Centralize Django settings, database routing, Celery task routing, and cache configuration so adding a new site is a one-entry YAML addition
- **Key traits:** Site registry in `sites.yml` auto-registers new tenants; base settings modules enforce consistency; env vars override per deployment

---

## Project Structure

```
projects/
├── configs/                     # ⚪ Shared Django configuration
│   ├── base/                    # Base settings modules
│   └── settings/                # Per-environment YAML settings
│       └── ENV/sites.yml        # Site registry
├── assets/                      # 🔵 Shared frontend assets
│   ├── templates/               # Cross-site Django templates
│   │   ├── base.html            # Base template with blocks
│   │   ├── components/          # Reusable template components
│   │   └── content/             # Content blocks (gallery, media)
│   ├── static/                  # CSS, JS, images
│   └── locale/                  # Translation files
├── www/                         # 🔴 Shared Django application code
├── libs/                        # 📦 Local reusable libraries
│   ├── django-fusion/           # 🔴 Component system + routing framework
│   └── ceptor-ai/               # 🟢 AI assistant + MCP server
│
├── precis-ctc/                # 🌐 CTC Research site
│   ├── templates/               # Site-specific templates
│   ├── plugins/                 # Site plugins (accounts, blog, components)
│   │   ├── accounts/            # Auth adapters, MFA
│   │   ├── blog/                # Blog models/templates
│   │   └── components/          # Site-specific UI components
│   ├── www/                     # Django apps
│   └── settings.py              # Site settings
│
├── lms/                    # 🌐 LMS Demo site
│   ├── templates/
│   ├── plugins/
│   ├── www/
│   └── settings.py
│
├── VResume/                     # 🌐 VResume site
│   ├── templates/
│   ├── plugins/
│   ├── www/
│   └── settings.py
│
├── cypercloud/                  # 🟢 AI Chat Customizer site
│   ├── templates/
│   ├── plugins/
│   ├── www/
│   └── settings.py
│
├── Makefile                     # Primary dispatcher
├── manage.py                    # Django management
├── cli.py                       # CLI utilities
└── pyproject.toml               # Python project config
```

## Customization Guide

### 🟢 Customizable
| Module | How to customize |
|--------|-----------------|
| Site `settings.py` | Add apps, middleware, database config |
| Site `templates/` | Override any template from `assets/templates/` |
| Site `plugins/` | Add site-specific functionality |
| `cypercloud/` | AI Chat template customizer |
| `ENV/sites.yml` | Add/remove sites from the registry |

### 🔴 Not Customizable (framework core)
| Module | Why not |
|--------|---------|
| `django-fusion/` | Component system core — use its public API |
| `configs/base/` | Base settings — override in site settings |
| `www/` | Shared app code — depend on, don't modify |

### ⚪ Config (env/settings only)
| What | Where |
|------|-------|
| Site domains & hosts | `ENV/sites.yml` |
| Database connection | `.env` / environment |
| SMTP settings | `.env` / environment |
| Feature flags | Site `settings.py` |

### 🟡 Delegate Pattern
| Pattern | How |
|---------|-----|
| Add Django app | Create in site `www/` → add to `INSTALLED_APPS` |
| Override template | Copy from `assets/templates/` → edit in site `templates/` |
| Add plugin | Create in site `plugins/` → add to `PLUGINS` setting |
| Use fusion component | `{% comp "name" %}` in templates |

## django-fusion Quick Reference

```python
# Routing
from django_fusion.comp.routes import Site, Application, route

# Components
from django_fusion.comp import Component

# Template tags
{% comp "component.name" %}              # Render a component
{% comp_include "path/to/template" %}    # Tracked include

# Viewsets
from django_fusion.comp.routes import ModelViewset

class ProductViewset(ModelViewset):
    model = Product
    fields = ['name', 'price']
```

## Managing Sites

```bash
cd projects
make check WEBSITE=precis-ctc     # Django checks for a site
make test WEBSITE=precis-ctc      # Run tests for a site
make migrate WEBSITE=precis-ctc   # Run migrations for a site
```

## Key Conventions

1. **Template layering**: site `templates/` > `assets/templates/`
2. **Component naming**: `components/blocks/` for content blocks, `components/partials/` for UI fragments
3. **Fragment IDs**: Always use `fragment_name` (not `fragment`, `name`, or `fragment_slug`)
4. **Imports**: Use canonical import paths (no re-export shims)
5. **Auth**: All sites use `django-allauth` + `django-fusion` auth mixins

---

→ [Back to docs](../README.md)
