# 📐 Precis Main — Project Configs (`configs/`)

This directory sits **beside `frontend/` and `backend/`** and is the
project-owned layer of the layered configuration cascade. It holds the
site identity, admin panel, design-system (CSS panel), and local-dev defaults
as **YAML defaults**; private/local customization belongs in the project
`.env` (never committed); deploy-time values belong in
`docker-compose.yml` / `docker-compose.override.yml`.

## Cascade order (low → high)

| # | Layer | Location | Holds |
|---|-------|----------|-------|
| 1 | Shared product defaults | `projects/precis/configs/Env/*.yml` | site registry, database, security, storage, email, logging, payments |
| 2 | **Project configs** | **`configs/*.yml` (this dir)** | local-dev defaults, site identity/domains, admin, CSS panel |
| 3 | Site overrides | `Env/_site.yml` | per-site identity/feature contract (kept in parity with other Precis sites) |
| 4 | Dotenv | `<repo>/.env` → `<project>/.env` | uncommitted secrets + local customization |
| 5 | Environment | `DJANGO_*` / bare keys (Compose `environment:`) | container/deploy truth — **always wins** |

Files load in order: `defaults.yml` → `site.yml` → `admin.yml` → `database.yml` → `theme.yml`
(any other `*.yml` afterwards). Each file may use Dynaconf-style environment
sections (`default:`, `development:`, `production:`) — the active environment
section is deep-merged on top of `default:`.

## What each file is for

| File | Contents |
|------|----------|
| `defaults.yml` | Local-dev defaults (DEBUG, hosts, ports, render mode) + the **static files reference** (`STATIC:` read → output → deploy paths) |
| `site.yml` | Site identity: name, aliases, public domains, allowed hosts, default email, module |
| `admin.yml` | Admin panel paths/URLs + **CSS panel** (design-system source → compiled `fusion.css` → served URL) |
| `database.yml` | **Database wired by type** (`DATABASE.type: sqlite\|postgres`); name/credentials resolve from `.env` (`DB_NAME_LANDING`, `POSTGRES_PASSWORD`) — never inlined |
| `theme.yml` | *(optional)* design tokens / brand overrides for the CSS panel |

## Who reads it

- **Backend** — `backend/settings.py` sources env-read *defaults* from the
  cascade via `django_fusion.config.project.load_config(...)`, and resolves
  identity per origin with `ProjectConfig.resolve(base_url, side)`.
  Environment variables always win; YAML only supplies fallbacks.
- **Frontend** — `make config-front` generates `frontend/src/config/project.json`
  from these YAML files; `frontend/src/config/project.ts` reads it so
  identity/domains never drift between roads.
- **Tooling** — `make config-show` / `make config-check` print the merged
  cascade (incl. resolved front/back views) and the static-files plan;
  `docker-compose.override.yml` mounts this directory read-only into the
  container for parity.

## Quick commands

```bash
make config-show    # merged cascade + resolved front/back views + static plan
make config-check   # validate required identity keys are resolvable
make config-front   # regenerate frontend/src/config/project.json (Astro wire)
```

## Remarks & Notes

- Never commit secrets into `configs/*.yml` — put them in the project `.env`
  (gitignored) or pass them via Compose `environment:`.
- Keep `STATIC:` in `defaults.yml` in sync with `backend/settings.py`
  (`STATICFILES_DIRS` / `STATIC_ROOT` / `MEDIA_ROOT`) and the Docker volumes
  in `docker-compose.yml` — the docs and `make config-show` render from this
  file so the paths stay truthful.
