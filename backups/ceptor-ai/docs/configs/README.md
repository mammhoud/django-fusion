# Configs — Shared Django Configuration

> Location: `applications/configs/`

## Directory Layout

```
applications/configs/
├── base/           # Base configuration modules
│   ├── assets.py   # Webpack loader & bundle path resolution
│   ├── paths.py    # Project path helpers
│   └── ...
├── settings/       # Environment/site settings
│   ├── conf.py     # Shared settings entry point
│   └── ...
├── site.py         # Site detection & module resolution
└── tests/          # Test configuration helpers
```

## Key Config Files

| File | Purpose |
|------|---------|
| `base/assets.py` | `WEBPACK_LOADER` config, `STATS_FILE` path, bundle dir normalization |
| `base/paths.py` | Project root and site directory resolution |
| `site.py` | Maps `WEBSITE` env var to site module (`ctc` → `ctc-research`) |
| `settings/conf.py` | Shared settings: databases, cache, auth, email, installed apps |

## Bundle Path Resolution

The `BUNDLE_SITE_NAME` in `base/assets.py` normalizes the VResume directory
name (`VResume` → `vresume`) to match webpack's lowercase output directory.
This ensures `{% render_bundle %}` finds the correct `bundles.json` manifest.

## Adding a New Config Module

1. Create module in `applications/configs/base/<name>.py`
2. Import from `applications/configs/settings/conf.py` or site `settings.py`
3. Never duplicate a setting across sites — canonical location is `configs/base/`
4. Run: `make -C applications check WEBSITE=<site>` across all sites

## Project Scope README

For the full project-scope README (Django documentation links, django-fusion integration, models/managers/services guidance), see [`applications/configs/README.md`](../../applications/configs/README.md).

## Directory Tree

```
docs/configs/
├── README.md              # this file
├── settings-readme.md     # (reserved for settings-specific notes)
└── tests-readme.md       # shared test configuration notes
```
