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
├── Makefile                     # root orchestrator (frontend + backend + full + env)
├── backend/                     # Django boundary — no Wagtail
│   ├── Makefile                 # backend targets (dev/check/migrate/test/seed)
│   ├── config/                  # settings (Unfold + fusion render-mode) + URL wiring
│   ├── formint/
│   │   ├── models/              # domain models (products, sales, inventory, crm, hr, …)
│   │   ├── schemas.py           # ninja_schema models + writable/patch schema factory
│   │   ├── controllers.py       # ninja-extra ModelController CRUD for 45 entities
│   │   ├── api.py               # NinjaAPI with fusion encoder renderer + system endpoints
│   │   ├── components.py        # django-fusion table/form components
│   │   ├── fusion_components.py # branch summary fragment (FusionDualModeMixin)
│   │   ├── core.py              # FormintSite (django-fusion Site — nav source of truth)
│   │   ├── fusion.py            # render-mode/nav/assets contract (landing-fusion parity)
│   │   ├── handlers.py          # class-based HTMX fragment handlers
│   │   ├── views.py             # thin URL-facing delegation + /fusion/* endpoints
│   │   └── templates/           # fusion table + form templates
│   └── manage.py
├── frontend/                    # Astro shell
│   ├── Makefile                 # frontend targets (install/dev/build/check/test)
│   ├── astro.config.mjs         # dev proxy → backend :8767
│   └── src/pages/data.astro     # data management showcase (API + HTMX)
├── src-tauri/                   # Tauri desktop shell
├── assets/                      # shared assets
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
| `/htmx/tables/{resource}/` | Server-rendered fusion table (`X-Formint-Table-Resource`) |
| `/htmx/forms/{resource}/` | Server-rendered fusion form (GET) / save (POST, `X-Formint-Saved`, `HX-Trigger`) |
| `/htmx/branches/summary/` | Branch summary fragment (render-first by default) |

All fragment responses support the fusion **render-first** contract — the
`X-Fusion-Render-First: true|false` header switches between django-fusion
rendered fragments and lean HTMX data-only responses (see `formint/fusion.py`).

### Fusion render-mode (landing-fusion parity)

| Endpoint | Description |
|---|---|
| `/api/v1/render-mode` | Active mode (`fusion-render` vs `data-api`) |
| `/api/v1/navigation` | Nav from `FormintSite` (Home / Data / Admin) |
| `/api/v1/assets` | `FUSION_ASSETS` manifest |
| `/fusion/render-mode/` · `/fusion/navigation/` · `/fusion/assets/` | Same contract at the fragment path |

### Quick start (make)

```bash
cd projects/pos/formint-pos
make install   # backend .venv + deps + migrate + frontend npm install
make seed      # migrate + idempotent superuser (admin@formint.local / admin123)
make env       # tmux: backend :8767 + frontend :4321 (health-checked)
#   API      → http://127.0.0.1:8767/api/v1/docs
#   Admin    → http://127.0.0.1:8767/admin/
#   Shell    → http://127.0.0.1:4321/
#   Render   → http://127.0.0.1:4321/fusion/render-mode/

make status    # tmux sessions + endpoint health
make test      # 35 backend tests + frontend contract tests
make stop      # stop the tmux env
```

Full command list: `make help`. The parent `projects/pos/Makefile` delegates
`make formint-{install,run,env,stop,test,check,clean}` here.

Validation: `make check` (django check + astro check), `make test`.

## Frontend

```bash
cd projects/pos/formint-pos/frontend
make install   # npm install
make dev       # astro dev :4321
```

`astro.config.mjs` proxies `/api`, `/htmx` and `/fusion` to the backend at
`:8767`. The `/data` page showcases the API and the HTMX table/form
components with frontend-owned loading states.

Validation: `make check` (astro check) and `make build`.

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
