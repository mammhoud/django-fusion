# Configuration — DF-007

> Source of truth: `src/django_fusion/config/conf.py`, `conf_utils.py`,
> `constants.py`, `dynaconf_loader.py`, `pyproject.toml`,
> `src/django_fusion/core/middlewares.py`.

## Required `INSTALLED_APPS`

| App | Purpose |
|-----|---------|
| `django_fusion.comp` | Component system, registry, tag, routing |
| `django_fusion.core` | Handlers, models, managers, services, cache, middlewares |
| `django_fusion.config` | Multi-environment YAML loader (Dynaconf) |
| `django_fusion.infrastructure` | Management commands, scripts, locale |
| `django_fusion.site` | Allauth adapter, context processors, auth mixins |
| `django_fusion.web` | Allauth adapters, view mixins |
| `django_fusion.health` *(optional)* | `/health/`, `/health/db/`, `/health/assets/` |
| `django_fusion.analyzer` *(optional)* | `{% comp %}` usage scanner |
| `django_fusion.wagtail` *(if using Wagtail)* | Blocks, snippets, viewsets |
| `django_fusion.contrib` *(optional)* | Admin, privacy, debug tools |

## Recognized settings

Only `DJANGO_DEBUG_CONFTEST` is registered as an opt-in diagnostic
at this version (see the comment block under `[tool.pytest.ini_options]`
in `pyproject.toml`). All other configuration flows through
`INSTALLED_APPS`, `MIDDLEWARE`, and the per-key overrides in
`dynaconf_loader.py` — there is **no canonical `DJANGO_FUSION_*`
settings table** at v0.2.0.

| Setting | Default | Purpose |
|---------|---------|---------|
| `DJANGO_DEBUG_CONFTEST` *(test only)* | unset, must be exactly `== "1"` | When set, conftest prints active Django `TEMPLATES` config + `DJANGO_SETTINGS_MODULE`. Enforced by `tests/test_conftest_debug_is_quiet.py`. |

> Remark: if a future version introduces `DJANGO_FUSION_*` settings,
> update this table from `src/django_fusion/config/constants.py` —
> never invent names that aren't present in source.

## Dynaconf multi-environment YAML

`django_fusion.config.dynaconf_loader.load_dynaconf_settings()` reads
YAML files from any of these locations (first found wins):

```text
config/settings.yml
config/settings.yaml
config/settings.toml
config/settings.json
config/settings.env
```

Per-environment overrides are matched against `DJANGO_ENV`:

```yaml
default:
  DEBUG: false
  ALLOWED_HOSTS: ["localhost"]

development:
  DEBUG: true
  ALLOWED_HOSTS: ["localhost", "127.0.0.1"]

production:
  DEBUG: false
  ALLOWED_HOSTS: ["example.com"]
```

```bash
DJANGO_ENV=production python manage.py runserver
```

`DynaconfSettings` is a thin schema wrapper declared in
`dynaconf_loader.py`. `ModelsRegistry` and `TemplateRegistry` are the
companion registries used by `comp.routes.model.ModelViewset` for
runtime model kwargs.

### Imports

```python
from django_fusion.config.dynaconf_loader import (
    DynaconfSettings, ModelsRegistry, TemplateRegistry,
    load_dynaconf_settings,
)
from django_fusion.config.conf_utils import (
    ImportStrategy, import_attribute, import_model, import_form, import_adapter,
)
```

## Middleware ordering

`django_fusion.core.middlewares` ships module-level helpers; sites opt
in to the ones they want. The standard Structa Cloud ordering is:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # django-fusion opt-ins inserted by the importing site
    # (specific class names live in src/django_fusion/core/middlewares.py)
]
```

> Remark: read the source of `core.middlewares.py` for the exact
> class names you want to opt in to; this version does not export a
> fixed list of `ComponentErrorMiddleware` / `PrivacyMiddleware` /
> `LanguageMiddleware` constants. When adding error-tracking
> middleware, place it **after** `AuthenticationMiddleware` so it can
> read `request.user`, and **before** any middleware that swallows
> 500s silently.

## Cache backends

`django_fusion.comp.cache` exports `ComponentMappingCache` (a
component-name → template-path cache) and `get_component_map_cache()`
(singleton accessor). The module relies on Django's standard `cache`
framework and falls back to the default backend if Redis is unavailable
— see `src/django_fusion/comp/cache.py` for the exact fallback
semantics.

Recommended cache settings:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),
    },
}
```

> Remark: `ComponentMappingCache` does not require the third-party
> `cachetools` library at this version — its in-memory behaviour comes
> from Django's standard cache framework. If you change `CACHES`,
> nothing else needs to be updated — it follows Django.

## Cross-references

- [DF-009 — Health checks](./09-health.md) — JSON response shape
- [DF-005 — Routing](./05-routing.md) — `Site`, `Application`
- [DF-008 — API Reference](./08-api-reference.md) — exact symbol list
