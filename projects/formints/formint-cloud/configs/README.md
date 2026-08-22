# 📐 Formint Cloud — Project Configs (`configs/`)

Project-owned layer of the layered configuration cascade, sitting beside
`backend/` and `frontend/` (same layout as `precis/precis-main/configs/`).
YAML holds **defaults**; the project `.env` holds local customization;
environment variables (`DJANGO_*`) hold deploy-time truth.

> The Django settings package lives at `backend/configs/` (env-driven) — this
> directory is the *cascade YAML layer*, not the settings module.

## Cascade order (low → high)

| # | Layer | Location |
|---|-------|----------|
| 1 | **Project configs** | **`configs/*.yml` (this dir)** — defaults / site / admin |
| 2 | Dotenv | `<repo>/.env` → `<project>/.env` |
| 3 | Environment | `DJANGO_*` / bare keys — **always wins** |

Files load in order: `defaults.yml` → `site.yml` → `admin.yml` → `theme.yml`
(any other `*.yml` afterwards). Each may use Dynaconf-style environment
sections (`default:`, `development:`, `production:`).

## Consumers

- **Tooling** — `make config-show` / `make config-check` (merged view +
  static-files plan, via django-fusion `config.project`).
- **Backend** — `backend/configs/__init__.py` remains env-driven; the YAMLs
  document the defaults those env vars override.

## Quick commands

```bash
make config-show      # merged cascade + static-files plan (read/output/deploy)
make config-check     # validate required identity keys resolve
```

## Remarks & Notes

- Formint edition identity is distinct per package (`formint-cloud` vs
  `formint-pro` vs `formint-community`) — never alias them in configs.
- Never commit secrets here — use the project `.env` (gitignored).
