# applications/configs — Shared Django Configuration

This package contains the shared Django configuration used by every site in the `applications/` monorepo. It is the single source of truth for settings, template configuration, database configuration, authentication, caching, email, i18n, logging, middleware, security, and URL routing.

## Scope

- **Base configuration modules** (`base/`): settings fragments imported by every site.
- **Environment/site settings** (`settings/`): Dynaconf/YAML-driven environment configuration.
- **Test settings** (`tests/`): shared test configuration and helpers.
- **Site discovery** (`site.py`): resolves the active website from env vars, cwd, or aliases.

## Integration

Each site imports the shared configuration in its `settings.py`:

```python
from configs.settings import *  # noqa: F401,F403
```

The shared `TEMPLATES` setting in `base/templates.py` already registers `django_fusion` component tags and `unfold` tags as Django template builtins, so templates can use `{% comp %}` and Unfold tags without `{% load %}`.

## Project Django Documentation Links

| Topic | File | Description |
|-------|------|-------------|
| Templates & builtins | `base/templates.py` | Shared `TEMPLATES_DIRS`, component builtins, context processors |
| Site discovery | `site.py` | `active_website_name()`, `site_config()`, `configure_site_environment()` |
| Environment config | `settings/conf.py` | `MainSettings`, Dynaconf integration, env validation |
| Apps & installed apps | `base/apps.py` | Shared `INSTALLED_APPS`, `LOCAL_APPS` pattern |
| Auth | `base/auth.py` | allauth, social auth, MFA settings |
| Databases | `base/databases.py` | PostgreSQL, Redis, database routing |
| Security | `base/security.py` | `ALLOWED_HOSTS`, CSRF, CORS, SSL settings |
| Email | `base/emails.py` | SMTP, backend, template snippet settings |
| Logging | `base/logging.py` | Structlog/Django logging configuration |
| Middleware | `base/middlewares.py` | Shared middleware stack |
| i18n | `base/i18n.py` | Language, timezone, translation settings |
| URLs | `base/urls.py` | Shared URL configuration helpers |

## Package of django-fusion Integrations

`configs/base/templates.py` is the integration point for django-fusion:

```python
# Register django_fusion component tags as builtins
if importlib.util.find_spec("django_fusion") is not None:
    from django_fusion.comp.configuration.conf import COMPONENTS_BUILTINS, COMPONENTS_BUILTINS_UI
    _TEMPLATE_BUILTINS.append(COMPONENTS_BUILTINS)
    _TEMPLATE_BUILTINS.append(COMPONENTS_BUILTINS_UI)
```

This makes the following available in every template:

- `{% comp %}` — render any registered or include-path component
- `{% prop %}` — declare component props
- `{% slot %}` — declare named/default slots
- `{% var %}` — mutable template variables
- `{% css %}` / `{% js %}` — component asset helpers
- `{% table %}`, `{% pagination %}`, `{% search %}`, `{% form_field %}` — UI helpers

## Models, Managers, and Services

The `configs/` package itself does not define models, managers, or services. Those live in:

- **Shared libraries**: `applications/libs/django-fusion/src/django_fusion/projects/models.py`, `managers.py`, `services.py`
- **Per-site models**: `applications/<site>/www/<app>/models.py`
- **Per-site managers**: `applications/<site>/www/<app>/managers.py`
- **Per-site services**: `applications/<site>/www/<app>/services.py`

When adding a new model, manager, or service, follow the site-specific `AGENTS.md` and `PROMPTS.md` for the target site.

## Usage

### Run checks for a site

```bash
make -C applications check WEBSITE=ctc-research
```

### Add a new shared config module

1. Create `applications/configs/base/<name>.py`.
2. Import it from `applications/configs/base/__init__.py`.
3. Import it from `applications/configs/settings/conf.py` or each site's `settings.py` as needed.
4. Run checks across all sites:

```bash
make -C applications check WEBSITE=ctc-research
make -C applications check WEBSITE=lms-demo
make -C applications check WEBSITE=vresume
```

## Related Documentation

- [Project AGENTS.md](../../AGENTS.md)
- [Project PROMPTS.md](../../PROMPTS.md)
- [django-fusion Component System](../../applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md)
- [django-fusion Component Tag API](../../applications/libs/django-fusion/docs/COMPONENT_TAG.md)
- [docs/configs/README.md](../../docs/configs/README.md)

## Directory Tree

```
applications/configs/
├── README.md              # this file
├── site.py              # website discovery helpers
├── base/
│   ├── __init__.py      # exports all base modules
│   ├── admin_site.py    # shared admin/Unfold configuration
│   ├── apps.py          # INSTALLED_APPS and AppConfig helpers
│   ├── assets.py        # static/media/webpack asset settings
│   ├── auth.py          # allauth / social auth / MFA settings
│   ├── databases.py     # PostgreSQL / Redis configuration
│   ├── emails.py        # email backend and template settings
│   ├── i18n.py          # language / timezone / translation
│   ├── logging.py       # logging configuration
│   ├── middlewares.py   # shared middleware stack
│   ├── security.py      # ALLOWED_HOSTS, CSRF, CORS, SSL
│   ├── templates.py     # TEMPLATES_DIRS, builtins, component tags
│   └── urls.py          # shared URL helpers
├── settings/
│   ├── conf.py          # MainSettings / Dynaconf / env validation
└── tests/
    └── ...              # shared test settings
```
