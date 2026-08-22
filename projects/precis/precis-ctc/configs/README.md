# 📐 CTC Research — Project Configs (`configs/`)

Project-owned layer of the layered configuration cascade, sitting **beside
`frontend/` and `backend/`** (same layout as `precis/precis-main/configs/`).
YAML holds **defaults**; the project `.env` holds local customization;
`docker-compose.yml` / `backend/docker-compose.yml` hold deploy-time truth.

## Cascade order (low → high)

| # | Layer | Location | Notes |
|---|-------|----------|-------|
| 1 | Shared product defaults | `projects/precis/configs/Env/*.yml` | site registry, database, security, storage, email, logging, payments |
| 2 | **Project configs** | **`configs/*.yml` (this dir)** | local-dev defaults, site identity/domains, admin, CSS panel |
| 3 | Site overrides | `Env/_site.yml` | merged last by Dynaconf — highest YAML priority |
| 4 | Dotenv | `<repo>/.env` → `<project>/.env` | uncommitted secrets + customization |
| 5 | Environment | Compose `environment:` (`DJANGO_*` / bare) | container truth — **always wins** |

Files load in order: `defaults.yml` → `site.yml` → `admin.yml` → `theme.yml`.
Each file may use Dynaconf-style environment sections (`default:`,
`development:`, `production:`) — the active env section merges on top of
`default:`.

## Consumers

- **Backend** — `projects/precis/configs/settings/conf.py` appends these files
  (before `Env/_site.yml`); every value resolves through `cfg()` in
  `configs.default` (env var → YAML → fallback).
- **Frontend** — Astro reads identity via `PUBLIC_SITE_URL` / `PUBLIC_*` env
  (Compose `frontend/docker-compose.yml`); `configs/site.yml` is the source of
  the defaults those vars override.
- **Tooling** — `make config-show` / `make config-check` (merged view +
  static-files plan).

## Quick commands

```bash
make config-show    # merged config + static-files plan (read/output/deploy)
make config-check   # validate required identity keys resolve
```

## Remarks & Notes

- Keep `STATIC:` in sync with `backend/settings/assets.py` and the Compose
  mounts (`backend/assets/staticfiles` → proxy site root, shared media tree).
- Never commit secrets here — use the project `.env` (gitignored).
