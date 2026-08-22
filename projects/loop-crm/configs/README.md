# 📐 Loop-CRM — Project Configs (`configs/`)

Two complementary things live in this directory:

1. **Env catalog (Python, stdlib-only)** — `env.py` + `validate.py` are the
   canonical, documentation-first description of every environment variable
   the project reads. `make validate-env` checks the current environment;
   `make env-example` regenerates `.env.example` from the same source.
2. **YAML cascade (django-fusion `config.project`)** — `defaults.yml`,
   `site.yml`, `admin.yml` are the project-owned layer of the layered config
   cascade (same layout as `precis/precis-main/configs/` and
   `precis/precis-ctc/configs/`). YAML holds **defaults**; the project `.env`
   holds customization; Compose `environment:` holds deploy-time truth.

## Cascade order (low → high)

| # | Layer | Location | Notes |
|---|-------|----------|-------|
| 1 | Shared product defaults | *(none — Loop-CRM is standalone)* | env catalog supplies the variable contract |
| 2 | **Project configs** | **`configs/*.yml` (this dir)** | local-dev defaults, site identity/domains, admin, CSS panel |
| 3 | Site overrides | `Env/_site.yml` | per-environment flags (DEBUG, origins) |
| 4 | Dotenv | `<repo>/.env` → `<project>/.env` | uncommitted secrets + customization |
| 5 | Environment | `DJANGO_*` / bare keys (Compose) | container truth — **always wins** |

Files load in order: `defaults.yml` → `site.yml` → `admin.yml` → `theme.yml`.
Each file may use Dynaconf-style environment sections (`default:`,
`development:`, `production:`).

## Consumers

- **Backend** — `backend/configs/site.py` seeds env defaults from the merged
  `SITE`/`ADMIN` sections via `os.environ.setdefault`; an explicit environment
  always wins. Django settings read `os.environ` directly (no dynaconf).
- **Frontend** — Astro reads identity via `PUBLIC_SITE_URL` / `PUBLIC_*` env
  (`frontend/.env.example`); `configs/site.yml` is the source of the defaults.
- **Tooling** — `make config-show` / `make config-check` (merged view +
  static-files plan); `make validate-env` checks the env contract.

## Quick commands

```bash
make config-show      # merged cascade + static-files plan (read/output/deploy)
make config-check     # validate required identity keys resolve
make validate-env     # check the current environment against the catalog
make env-example      # regenerate .env.example.generated from env.py
```

## Remarks & Notes

- The `configs/` Python package (env catalog) and the YAML cascade are
  complementary: the catalog documents *variables*, the YAMLs document
  *defaults* for identity/admin/static paths. Keep both in sync.
- Never commit secrets here — use the project `.env` (gitignored).
