# 📐 Precis Landing (legacy copy) — Project Configs (`configs/`)

This directory is kept in **parity with `projects/precis/precis-main/configs/`**
so the two Precis Landing trees resolve the same layered configuration. Only
the database layer is wired here (the marketing/catalog shell's other defaults
live in `configs/*.yml` under `precis-main`, which the dispatcher routes to).

## Cascade order (low → high)

| # | Layer | Location | Holds |
|---|-------|----------|-------|
| 1 | Shared product defaults | `projects/precis/configs/Env/*.yml` | site registry, database, security, storage, email |
| 2 | **Project configs** | **`configs/*.yml` (this dir)** | database (type-wired) |
| 3 | Site overrides | `Env/_site.yml` | per-site identity/feature contract |
| 4 | Dotenv | `<repo>/.env` → `<project>/.env` | uncommitted secrets + local customization |
| 5 | Environment | `DJANGO_*` / bare keys (Compose `environment:`) | container/deploy truth — **always wins** |

## Files

| File | Contents |
|------|----------|
| `database.yml` | **Database wired by type** (`DATABASE.type: sqlite\|postgres`); name/credentials resolve from `.env` (`DB_NAME_LANDING`, `POSTGRES_PASSWORD`) — never inlined |

## Consumers

- **Backend** — `backend/settings.py` sources env-read *defaults* from the
  cascade (`DB_TYPE` env is authoritative; `DATABASE.type` is the fallback).
- **Tooling** — the compose file mounts this directory read-only into the
  container for parity (`./configs:/app/precis-landing/configs:ro`).

## Remarks & Notes

- Never commit secrets into `configs/*.yml` — put them in the project `.env`
  (gitignored) or pass them via Compose `environment:`.
- This is a **kept legacy copy** — the dispatcher routes `precis-landing` to
  `precis-main`. Keep changes here in parity with `precis-main/configs/`.
