# Configuration — DF-007

> Source of truth: `src/django_fusion/config/conf.py`, `conf_utils.py`,
> `constants.py`, `loader.py`, `pyproject.toml`,
> `src/django_fusion/projects/middlewares.py`.

## Required `INSTALLED_APPS`

| App | Purpose |
|-----|---------|
| `django_fusion.comp` | Component system, registry, tag, routing |
| `django_fusion.core` | Handlers, models, managers, services, cache, middlewares |
| `django_fusion.config` | Multi-environment YAML loader (Dynaconf) |
| `django_fusion.infrastructure` | Management commands, scripts, locale |
| `django_fusion.site` | Allauth adapter, context processors, auth mixins |
| `django_fusion.web` | Allauth adapters, view mixins |
| `django_fusion.core.health` *(optional)* | `/health/`, `/health/db/`, `/health/assets/` |
| `django_fusion.analyzer` *(optional)* | `{% comp %}` usage scanner |
| `django_fusion.wagtail` *(if using Wagtail)* | Blocks, snippets, viewsets |
| `django_fusion.contrib` *(optional)* | Admin, privacy, debug tools |

## Recognized settings

The runtime settings are read from the Django settings module by name
(no canonical `DJANGO_FUSION_*` namespace). The canonical names and
their legacy fallbacks are:

| Setting | Legacy alias | Purpose |
|---------|--------------|---------|
| `FUSION_RENDER_FIRST` | `FUSION_RENDER_FIRST_DEFAULT` / `COMPONENTS_FUSION_RENDER_FIRST_DEFAULT` | Global render-mode default (component HTML vs data API). |
| `FUSION_PIPELINE` | `FUSION_ASSET_PIPELINE` | Asset-pipeline options (webpack, components, `render_first_gates_assets`). |
| `FUSION_ASSETS` | — | Explicit top/bottom link configuration merged into the manifest. |
| `FUSION_COMPONENTS` | `FUSION_COMPONENT_ASSETS` | `{"ENABLED": True}` gate for the `fusion_component_assets_json` tag. |
| `FUSION_SKELETON` | — | App-skeleton options for `fusion_skeleton` rendering. |
| `COMPONENTS_DIR_NAMES` | — | Component directory names (default `components`, `partials`, `tags`). |
| `COMPONENTS_ENABLE_BLOCK_ATTRS` | — | Emit `data-block-*` attributes on components. |
| `COMPONENTS_INCLUDE_PATH_ROOTS` | — | Template subdirs auto-registered as path-style components. |

`DJANGO_DEBUG_CONFTEST` remains the only opt-in diagnostic (see the
comment block under `[tool.pytest.ini_options]` in `pyproject.toml`).

> Remark: if a future version introduces `DJANGO_FUSION_*` settings,
> update this table from `src/django_fusion/config/constants.py` —
> never invent names that aren't present in source.

## Unified asset pipeline

The package exposes a single resolved asset contract through
`django_fusion.config.assets.AssetPipelineOptions`. Sites configure source,
webpack, and collected-static paths independently; django-fusion merges their
public links without copying generated files into source directories.

```python
FUSION_ASSET_PIPELINE = {
    "enabled": True,
    "static_url": "/static/",
    "webpack": {
        "enabled": True,
        "stats_file": "/site/assets/bundles/site/bundles.json",
        "bundle_dir": "bundles/site/",
    },
    "components": {
        "enabled": True,
        "manifest_path": "/site/assets/staticfiles/components/manifest.json",
    },
}
```

`FUSION_ASSETS` remains the explicit top/bottom link configuration. The merged
manifest adds valid CSS/JS entries from webpack `bundles.json`, deduplicates
links while preserving order, and is consumed by the asset API and
`fusion_assets` template tags. Import the implementation directly:

```python
from django_fusion.config.assets import AssetPipelineOptions, get_asset_pipeline_options
from django_fusion.config.manifest import load_merged_asset_manifest
```

Keep `assets/` source files, webpack bundles, and `STATIC_ROOT` as separate
filesystem locations. Do not expose source assets directly or create duplicate
static roots.

## Dynaconf multi-environment YAML

`django_fusion.config.loader.load_dynaconf_settings()` reads
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
`loader.py`. `ModelsRegistry` and `TemplateRegistry` are the
companion registries used by `comp.routes.model.ModelViewset` for
runtime model kwargs.

### Imports

```python
from django_fusion.config.loader import (
    DynaconfSettings, ModelsRegistry, TemplateRegistry,
    load_dynaconf_settings,
)
from django_fusion.config.conf_utils import (
    ImportStrategy, import_attribute, import_model, import_form, import_adapter,
)
```

## Layered project config (`config.project`)

`django_fusion.config.project.ProjectConfig` (loaded via `load_config`)
implements the layered cascade used by Structa Cloud products: shared product
Env YAML → project `configs/*.yml` → `Env/_site.yml` → dotenv → environment
variables (highest). It is Django-free and never raises, so it is safe to call
at `settings.py` import time; environment variables always win and the YAML
layers only supply defaults.

```python
from django_fusion.config.project import load_config, staticfiles_plan

config = load_config(project_dir="projects/precis/precis-main")
domain = config.get("SITE.primary_domain", "structa.cloud")   # dotted keys
admin = config.section("ADMIN")                                # section dict

# Base-URL priority: resolve identity for a specific origin (front/back road).
backend_view = config.resolve("https://lms.structa.cloud", side="back")

plan = staticfiles_plan(project_dir="projects/precis/precis-main")
print(plan.render())   # static read → output → deploy reference table
```

Conventional project `configs/` files load in order `defaults.yml` →
`site.yml` → `admin.yml` → `theme.yml` (any extra `*.yml` after); each may use
Dynaconf-style environment sections (`default:`, `development:`,
`production:`). Dotenv keys are normalized (`DJANGO_DEBUG=0` drives `DEBUG`)
and every `DJANGO_*` env var maps to its base key at the top layer.

`resolve(base_url, side)` matches the origin host against `SITE`
(`primary_domain` / `domains` / `allowed_hosts`, plus well-known localhost
front/back ports) and overlays the matched site identity — still below
environment variables.

`staticfiles_plan()` resolves the conventional static layout — read dirs
(`STATICFILES_DIRS`), output (`STATIC_ROOT`), media (`MEDIA_ROOT`), webpack
bundle stats, the compiled design-system stylesheet, and deploy destinations
(named volumes, shared-proxy) — and honors `STATIC:` overrides from the
project cascade. See the monorepo guide `docs/guides/config-cascade.md` and
the tests in `tests/test_config_project.py` for the full contract.

## Middleware ordering

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
    # (specific class names live in src/django_fusion/projects/middlewares.py)
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

`django_fusion.comp.cache` exports `ComponentMapCache` (a
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

> Remark: `ComponentMapCache` does not require the third-party
> `cachetools` library at this version — its in-memory behaviour comes
> from Django's standard cache framework. If you change `CACHES`,
> nothing else needs to be updated — it follows Django.

## Cross-references

- [DF-009 — Health checks](./09-health.md) — JSON response shape
- [DF-005 — Routing](./05-routing.md) — `Site`, `Application`
- [DF-008 — API Reference](./08-api-reference.md) — exact symbol list
