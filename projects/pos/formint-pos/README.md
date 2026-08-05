# Formint POS

> **Phase 2 status:** Merge complete — `pos-full` + `pos-solo` consolidated into this package.
>
> Formint is the canonical Professional POS product name. The legacy `pos-solo`, `pos-full`, and Forge directories remain on disk for parity and rollback work.

## Purpose

Formint POS Professional is the restaurant-focused POS product built from the existing POS capabilities. This directory is the product boundary for:

- `backend/` — Django data/API/HTMX boundary (Django Ninja + ninja-extra + django-fusion)
- `frontend/` — Astro + Alpine.js + HTMX shell
- `src-tauri/` — Tauri desktop shell (same architecture as the merged packages)
- `assets/` — shared source assets and static build inputs
- `migration/` — compatibility manifests and migration notes

## Architecture

```text
formint-pos/
├── backend/                    # Django boundary — no Wagtail
│   ├── config/                 # settings + URL wiring
│   ├── formint/
│   │   ├── models/             # domain models (products, sales, inventory, crm, hr, …)
│   │   ├── schemas.py          # ninja_schema models + writable/patch schema factory
│   │   ├── controllers.py      # ninja-extra ModelController CRUD for 45 entities
│   │   ├── api.py              # NinjaAPI with fusion encoder renderer + system endpoints
│   │   ├── components.py       # django-fusion table/form components
│   │   ├── views.py            # HTMX table/form fragment views
│   │   └── templates/          # fusion table + form templates
│   └── manage.py
├── frontend/                   # Astro shell
│   ├── astro.config.mjs        # dev proxy → backend :8000
│   └── src/pages/data.astro    # data management showcase (API + HTMX)
├── src-tauri/                  # Tauri desktop shell
├── assets/                     # shared assets
└── migration/
    └── compatibility-manifest.json
```

## Backend

### Stack

- **Django** — models, migrations, admin
- **django-ninja + ninja-extra** — typed REST API with `ModelControllerBase` CRUD
- **django_fusion encoder/decoder** — all API responses wrapped in the fusion envelope (`{ status, message, data }`)
- **django_fusion.fragments.tables / .forms** — server-rendered data components as tables and forms
- **HTMX** — fragment swapping for table/form regions

### API

Base URL: `http://127.0.0.1:8000/api/v1/`

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/health` | GET | Service health + product + model count (fusion envelope) |
| `/api/v1/stats` | GET | System stats (counts per resource) |
| `/api/v1/openapi.json` | GET | OpenAPI schema |
| `/api/v1/docs` | GET | Swagger UI |
| `/api/v1/{resource}` | GET | List (paginated, `results` array) |
| `/api/v1/{resource}` | POST | Create |
| `/api/v1/{resource}/{id}` | GET | Retrieve |
| `/api/v1/{resource}/{id}` | PATCH | Partial update (all-optional schema) |
| `/api/v1/{resource}/{id}` | DELETE | Delete |

Resources (45 controllers): products, categories, customers, client-categories, sales, sale-items, suppliers, purchase-orders, purchase-order-items, inventory, inventory-transactions, recipes, ingredients, menus, menu-item-assignments, menu-items, employees, employee-schedules, payroll, kitchen-tickets, support-tickets, nodes, master-devices, cloud-links, device-tokens, sync-approvals, heartbeat, node-events, signal-events, companies, user-settings, receipt-templates, roles, deals, activities, crm-notes, contacts, stages, pipelines, notes, loyalty-transactions, tax-reports, and more.

### HTMX fragments

| Endpoint | Description |
|---|---|
| `/htmx/tables/{resource}/` | Server-rendered fusion table (`X-Formint-Response-Mode: table`) |
| `/htmx/forms/{resource}/` | Server-rendered fusion form (GET) / save (POST, `X-Formint-Saved`, `HX-Trigger`) |
| `/htmx/branches/summary/` | Legacy branch summary fragment |

All fragment responses support the fusion render-first contract when `X-Fusion-Render-First: true` is sent — the response body is a fusion JSON envelope.

### Run

```bash
cd projects/pos/formint-pos/backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Validation: `python manage.py check`, `python manage.py test` (see `tests/`).

## Frontend

```bash
cd projects/pos/formint-pos/frontend
pnpm install
pnpm dev
```

`astro.config.mjs` proxies `/api` and `/htmx` to the backend at `:8000`. The `/data` page showcases the API and the HTMX table/form components with frontend-owned loading states.

Validation: `pnpm check` (astro check) and `pnpm build`.

## Tauri shell

`src-tauri/` keeps the same desktop shell architecture as the merged editions. The sidecar/desktop layer consumes the same Robyn/Django APIs — see [`../docs/`](../docs/) for the full architecture documentation.

## Migration notes

- `migration/compatibility-manifest.json` records the merge, accepted legacy identifiers, canonical identifiers, and retirement gates.
- Legacy directories are preserved for parity/rollback. New work uses `formint-pos` / `Formint` identifiers.

## Validation gates

- `frontend`: `pnpm check` and `pnpm build`
- `backend`: `python manage.py check` and `python manage.py test`
- migration: inspect `migration/compatibility-manifest.json`
- backup: follow [`../../../docs/plans/pos/formint-backup-20260804.md`](../../../docs/plans/pos/formint-backup-20260804.md)

## Related

- [`../../../docs/plans/pos/formint-pos-professional-plan.md`](../../../docs/plans/pos/formint-pos-professional-plan.md)
- [`../README.md`](../README.md)
- [`migration/compatibility-manifest.json`](migration/compatibility-manifest.json)
