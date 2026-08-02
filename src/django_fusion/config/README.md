# django-fusion configuration

The `django_fusion.config` package contains runtime configuration helpers and
registries. Import concrete implementations directly; this package does not
provide compatibility re-export modules.

## Modules

- `conf.py` — Django-fusion configuration defaults and import helpers.
- `conf_utils.py` — safe dotted-path and model/form import utilities.
- `constants.py` — package constants and runtime limits.
- `loader.py` — Dynaconf multi-environment settings loader and registries.
- `logging.py` — structured logging configuration helpers.
- `manifest.py`, `options.py`, `params.py`, `plugins.py`, `staticfiles.py` —
  component and asset configuration primitives.

## Dynaconf loader

Use the canonical module directly:

```python
from django_fusion.config.loader import (
    DynaconfSettings,
    ModelsRegistry,
    TemplateRegistry,
    load_dynaconf_settings,
)

settings = load_dynaconf_settings(config_dir="configs/")
dynaconf = settings.load()
models = ModelsRegistry(dynaconf)
templates = TemplateRegistry(dynaconf)
```

The loader supports environment-specific YAML files, `.env` values, and
optional Pydantic validation. `dynaconf` is a direct package dependency because
`loader.py` imports it when the module is loaded.

## Import policy

Do not add legacy loader aliases, package-level forwarding shims,
`sys.modules` entries, or duplicate configuration implementations. When the
configuration tree changes, update active imports, tests, documentation, and
agent guidance together, then scan for stale paths.
