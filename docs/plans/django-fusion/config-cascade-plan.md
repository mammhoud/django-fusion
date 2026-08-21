# 🧅 Config Cascade — Recommendations & Guided Plan

> **Status:** Active — baseline implemented
> **Date:** 2026-08-20
> **Scope:** django-fusion (`config.project`), Precis Main + CTC (`configs/`), Docker env cascade
> **Guide:** [`guides/config-cascade.md`](../../guides/config-cascade.md)
> **Module:** `libs/django-fusion/src/django_fusion/config/project.py`

## What shipped (baseline)

- **`django_fusion.config.project`** — layered loader (`ProjectConfig` /
  `load_config`): shared product Env YAML → project `configs/*.yml` →
  `Env/_site.yml` → dotenv → environment variables, plus base-URL priority
  resolution (`resolve(base_url, side)` for front/back roads) and
  `staticfiles_plan()` (read → output → deploy static-files reference).
  Django-free, never raises, env always wins.
- **Precis Main project `configs/`** — `defaults.yml` (local-dev + `STATIC:`
  reference), `site.yml` (identity/domains), `admin.yml` (admin panel + CSS
  panel), `README.md`; wired into `backend/settings.py` as env-read defaults
  and into the Astro road via `make config-front` →
  `frontend/src/config/project.json` + `project.ts`.
- **CTC Research `configs/`** — same layout (defaults/site/admin); the shared
  `configs/settings/conf.py` loads project YAMLs before `Env/_site.yml`;
  `make config-show`/`config-check` added.
- **Loop-CRM `configs/`** — defaults/site/admin beside the existing env
  catalog; `backend/configs/site.py` seeds env defaults from the cascade
  (`SITE`/`ADMIN` sections); `make config-show`/`config-check`.
- **Syntara `configs/`** — defaults/site/admin alongside the dynaconf loader
  files; `settings.py` identity defaults via `load_config` (`SITE.runtime_name`
  keeps the `cypercloud` contract); `make config-show` cascade view.
- **Formint Cloud `configs/`** — defaults/site/admin (env-driven settings);
  `make config-show`/`config-check` diagnostics.
- **Docker cascade** — `docker-compose.override.yml` (local dev ports/debug),
  `configs/` baked into backend images + mounted read-only, `.env.example`
  rewritten around the cascade contract.
- **Tooling** — `make config-show` / `make config-check` on every product above.
- **Tests** — `libs/django-fusion/tests/test_config_project.py` (14 cases,
  incl. base-URL resolution).

## Recommendations (apply next)

| # | Recommendation | Rationale | Effort |
|---|----------------|-----------|--------|
| 1 | **Standardize the `configs/` layout across products** — replicate `defaults.yml`/`site.yml`/`admin.yml`/`theme.yml` (or a subset) in `precis-ctc`, `syntara`, and `loop-crm` when they adopt the cascade. | One mental model per product; `make config-show` works everywhere. | M |
| 2 | **Keep defaults in YAML, customization in `.env`, deploy truth in Compose `environment:`.** | New developers get a working stack from `cp .env.example .env`; secrets stay out of VCS. | S |
| 3 | **Never let YAML win over env** — the cascade contract is env-first; any future layer must sit *below* environment variables. | Prevents Docker/deploy drift and surprise overrides. | S |
| 4 | **Sync `STATIC:` with `settings.py` + Docker volumes** — add a CI check that `staticfiles_plan()` paths match the compose volume paths. | `make config-show` renders from YAML; a drift check keeps it truthful. | S |
| 5 | **Use `docker-compose.override.yml` only for local dev**; production deploys must use explicit `-f` flags from the proxy/root compose files so dev overrides never leak. | Overrides apply automatically and silently otherwise. | S |
| 6 | **Frontend parity** — surface `SITE.*` identity defaults to Astro via a tiny `PUBLIC_*` env bridge generated from `configs/site.yml` (a small Vite plugin or build script). | One source of identity for both render roads. | M |
| 7 | **Validate configs at container start** — call `config-check` in the backend entrypoint (warn-only) so a malformed cascade fails fast without breaking boot. | Early signal in CI/deploy. | S |

## Guided plan (rollout order)

1. **Precis Main (done)** — `config.project` module + `configs/` + Docker
   override + frontend wire (`make config-front`) + tests.
2. **django-fusion docs (done)** — `07-configuration.md` cascade/staticfiles
   sections (mirror of `guides/config-cascade.md`).
3. **CTC Research (done)** — `configs/` dir + shared `conf.py` wiring +
   `make config-show`/`config-check`; verified `manage.py check`.
4. **Syntara (done)** — `configs/` defaults/site/admin + `settings.py`
   identity wire (cypercloud runtime name preserved) + cascade view in
   `make config-show`.
5. **Loop-CRM (done)** — `configs/` defaults/site/admin + `site.py` cascade
   wire + `make config-show`/`config-check`.
6. **Formint Cloud (done)** — `configs/` defaults/site/admin + `make
   config-show`/`config-check` diagnostics (env-driven settings unchanged).
7. **CI drift check** — assert `staticfiles_plan().output_dir` matches the
   compose `STATIC_ROOT` volume for every deployed product.
8. **Frontend bridge parity** — extend `make config-front` to Syntara/CTC
   Astro roads (Precis Main done).
9. **Formint Pro / Standard / Community** — adopt the layout when a Django
   backend is present (⏳ optional).

## Success criteria

- `make config-show` on every product prints the merged cascade with correct
  env-section selection.
- `cp .env.example .env && make backend-dev` boots without any edits.
- `docker compose up -d --build` + override file gives a working local stack;
  production compose runs unaffected.
- Static-files paths in `STATIC:` match `settings.py` and the named volumes.

## Remarks & Notes

- The cascade is optional sugar by design: products without `configs/` behave
  exactly as before (env-only).
- Env normalization: dotenv `DJANGO_DEBUG=0` drives `DEBUG`; any `DJANGO_*`
  env var maps to its base key; a bare `KEY` beats the prefixed value.
- Keep this plan, `guides/config-cascade.md`, and the module docstrings in sync.
