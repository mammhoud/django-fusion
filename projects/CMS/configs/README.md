# 📐 Syntara (Cypercloud) — Project Configs (`configs/`)

Two layers coexist in this directory:

1. **Dynaconf loader files** — `settings.yml` + `settings.{env}.yml` + `models.yml`
   are read by `django_fusion.config.loader.DynaconfSettings` for AI model
   registry, template sites, and environment-scoped settings.
2. **YAML cascade (django-fusion `config.project`)** — `defaults.yml`,
   `site.yml`, `admin.yml` are the project-owned layer of the layered config
   cascade (same layout as `structa.cloud/configs/` and
   `precis/precis-ctc/configs/`). YAML holds **defaults**; the project `.env`
   holds customization; environment variables (`CYPERCLOUD_*` / `DJANGO_*`)
   hold deploy-time truth.

## Cascade order (low → high)

| # | Layer | Location |
|---|-------|----------|
| 1 | Dynaconf loader files | `settings.yml` + `settings.{env}.yml` (models/registry) |
| 2 | **Project configs** | **`defaults.yml` / `site.yml` / `admin.yml`** |
| 3 | Dotenv | `<repo>/.env` → `<project>/.env` |
| 4 | Environment | `CYPERCLOUD_*` / `DJANGO_*` — **always wins** |

Files load in order: `defaults.yml` → `site.yml` → `admin.yml` → `theme.yml`
(any other `*.yml` afterwards). Each may use Dynaconf-style environment
sections (`default:`, `development:`, `production:`).

## Consumers

- **Backend** — `settings.py` sources identity defaults (`WEBSITE_NAME`,
  `ALLOWED_HOSTS`, `DEFAULT_FROM_EMAIL`) from the cascade via `load_config`;
  `CYPERCLOUD_*` env vars win. AI models still come from Dynaconf.
- **Tooling** — `make config-check` / `make config-show` (Dynaconf) plus the
  cascade identity view printed by `make config-show`.

## Quick commands

```bash
make config-check      # Dynaconf configuration loads
make config-show       # Dynaconf config + cascade SITE/ADMIN identity + static plan
```

## Remarks & Notes

- Keep `SITE.runtime_name: cypercloud` — the runtime alias is an external
  contract; never rename it in customer-facing copy.
- Never commit secrets here — use the project `.env` (gitignored).
