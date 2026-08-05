# Formint POS — Architecture

> **Formint POS Professional** is the merged package that consolidates
> `pos-full` (cloud master manager) and `pos-solo` (standalone device) into a
> single product boundary with the same Tauri shell architecture.

| | |
|---|---|
| **Location** | [`../formint-pos/`](../formint-pos/) |
| **Status** | Phase 2 — merge complete |
| **API** | Django Ninja + ninja-extra (fusion encoder/decoder) |
| **Admin** | Django Unfold dashboard (loyalty/settings focus) |
| **Data components** | django-fusion tables + forms (HTMX) |
| **Frontend** | Astro + Alpine.js + HTMX |
| **Desktop** | Tauri v2 shell |
| **Manifest** | [`../formint-pos/migration/compatibility-manifest.json`](../formint-pos/migration/compatibility-manifest.json) |

---

## 1. Purpose

Formint is the canonical Professional POS product name. The legacy
`pos-full`, `pos-solo`, and Forge directories remain on disk for parity and
rollback; all new work uses `formint-pos` / `Formint` identifiers.

The package keeps the established Tauri architecture (Rust shell + sidecar
backend + web frontend) while upgrading the backend to a fully typed REST API
with server-rendered data components and a modern admin panel.

---

## 2. Directory map

```text
formint-pos/
├── backend/                     # Django boundary — no Wagtail
│   ├── config/                  # settings (Unfold), URLs (admin + API)
│   ├── formint/
│   │   ├── models/              # 45+ merged domain models (pos, menu, node,
│   │   │                        #   config, sync, inventory, ops, hr, notes,
│   │   │                        #   extra, loyalty, approval, token, audit, crm)
│   │   ├── schemas.py           # ninja_schema Out schemas + writable/patch factory
│   │   ├── controllers.py       # ninja-extra ModelController CRUD (45 resources)
│   │   ├── api.py               # NinjaAPI + fusion JSONRenderer + system endpoints
│   │   ├── components.py        # django-fusion table/form data components
│   │   ├── views.py             # HTMX table/form fragment views
│   │   ├── admin.py             # Unfold ModelAdmin registrations (all models)
│   │   ├── dashboard.py         # Unfold dashboard callback (KPIs/charts/tables)
│   │   ├── fusion_components.py # branch summary fragment
│   │   └── templates/           # fusion table + form templates
│   ├── templates/admin/         # Unfold admin index override (dashboard UI)
│   ├── manage.py                # CLI + --ensure-superuser bootstrap
│   └── sidecar.py               # PyInstaller sidecar entry point
├── frontend/                    # Astro shell
│   ├── astro.config.mjs         # dev proxy → backend :8000 (/api, /htmx)
│   └── src/pages/               # index.astro, data.astro (+ contract tests)
├── src-tauri/                   # Tauri shell (sidecar supervision + native)
├── assets/                      # shared static assets
└── migration/
    └── compatibility-manifest.json
```

---

## 3. Backend

### 3.1 Stack

- **Django** — models, migrations, admin
- **django-ninja + ninja-extra** — typed REST API with `ModelControllerBase`
- **django_fusion encoder/decoder** — every API response wrapped in the fusion
  envelope `{ status, message, data }`
- **django_fusion.fragments.tables / .forms** — server-rendered data
  components as tables and forms
- **django-unfold** — modern admin theme with custom dashboard

### 3.2 REST API (`/api/v1/`)

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
| `/api/v1/{resource}/{id}` | DELETE | Delete (204) |

**Resources** (45 controllers): products, categories, customers, sales,
sale-items, inventory-transactions, employees, menu-items, menus,
menu-assignments, nodes, heartbeats, node-events, device-configs,
master-devices, cloud-links, sync-logs, suppliers, purchase-orders,
purchase-order-items, kitchen-tickets, support-tickets, payroll,
employee-schedules, tax-reports, notes, ingredients, recipes,
receipt-templates, roles, inventory-adjustments, client-categories,
loyalty-transactions, user-settings, sync-approvals, device-tokens,
signal-events, crm/companies, crm/pipelines, crm/stages, crm/contacts,
crm/deals, crm/activities, crm/notes.

### 3.3 Schema factory

`schemas.py` builds writable (create/update) and patch schemas dynamically via
`ninja_schema`:

- **writable schema** — `include` of editable fields only; read-only
  (`created_at`, `updated_at`) and `URLField` columns excluded.
- **patch schema** — same fields, all optional (`optional` config) so
  partial updates work.
- Static `*Out` schemas mirror the model fields with `include`.

### 3.4 HTMX data components (`/htmx/`)

| Endpoint | Description |
|---|---|
| `/htmx/tables/{resource}/` | Server-rendered fusion table (`X-Formint-Table-Resource`) |
| `/htmx/forms/{resource}/` | Fusion form (GET) / save (POST, `X-Formint-Saved`, `HX-Trigger`) |
| `/htmx/branches/summary/` | Branch summary fragment (phase-1 vertical slice) |

All fragments support the fusion **render-first** contract when
`X-Fusion-Render-First: true` is sent — the response becomes a fusion JSON
envelope. Resource names use hyphens; template files use underscores
(`client-categories` → `client_categories.html`).

### 3.5 Unfold admin (`/admin/`)

The admin panel is the master-manager surface with special focus on
**loyalty & settings**:

| Section | Models |
|---|---|
| Loyalty & Clients | Client Categories (people as a client category), Loyalty Transactions, Customers |
| Settings | User Settings, Users, Groups |
| POS Core | Products, Categories, Sales, Employees, Inventory |
| Operations | Suppliers, Purchase Orders, Kitchen Tickets, Support Tickets, Menu |
| Nodes & Sync | Nodes, Heartbeats, Events, Device Configs, Master Devices, Cloud Links, Sync Logs |
| CRM | Companies, Pipelines, Stages, Contacts, Deals, Activities, Notes |

The admin index is overridden by `templates/admin/index.html`, which renders
the dashboard injected by `UNFOLD["DASHBOARD_CALLBACK"]` →
`formint.dashboard.formint_dashboard_callback`:

- **10 KPI cards** — today's sales, monthly revenue, AOV, active products,
  customers, branch nodes, loyalty members, points issued/redeemed, settings
  rows + 2FA coverage, open alerts.
- **5 charts** — daily revenue (bar), top products (pie), payment methods
  (doughnut), hourly revenue (bar), loyalty transaction mix (doughnut).
- **3 tables** — recent sales, recent loyalty transactions, node status.

Superuser bootstrap (idempotent): `python manage.py --ensure-superuser`,
which reads `FORMINT_ADMIN_EMAIL` / `FORMINT_ADMIN_PASSWORD` /
`FORMINT_ADMIN_NAME` (defaults in `config/settings.py`) and seeds a
`UserSettings` row. **When `DJANGO_DEBUG=0` the default password is refused.**

---

## 4. Frontend

- **Astro shell** with Alpine.js + HTMX; frontend owns layout, skeletons,
  retry, and empty/error states.
- `astro.config.mjs` proxies `/api` and `/htmx` to the backend at `:8000`.
- `src/pages/data.astro` showcases the API + HTMX table/form components.
- Frontend contract tests live alongside pages (`index.test.ts`) and are
  collected by the unified vitest config (`tests/js/vitest.config.ts`).

---

## 5. Tauri shell

`src-tauri/` keeps the same desktop shell architecture as the merged
editions: Rust supervises the sidecar process and exposes native
capabilities; Django owns domain rules, persistence, permissions, audit, and
fusion fragment rendering. The sidecar entry point is `backend/sidecar.py`
(PyInstaller-packaged as `formint-backend`).

---

## 6. Migration & compatibility

- `migration/compatibility-manifest.json` records the merge (phase 2
  `merge-complete`), canonical identifiers, and retirement gates.
- Legacy table names are preserved (`full_*`, `pos_crm_*`, …) so existing POS
  databases remain readable during the migration window.
- Legacy directories (`pos-full`, `pos-solo`, `forge-pos`, `pos-cloud`) stay
  preserved for parity/rollback.

---

## 7. Testing

Unified test directory: [`../tests/`](../tests/)

| Suite | Location | Runner |
|---|---|---|
| Backend (26 tests) | `tests/py/formint/run.sh` | `manage.py test formint` |
| Frontend contract | `tests/js/vitest.config.ts` | `npx vitest run` |
| Admin selenium | `tests/selenium/formint/` | `pytest tests/selenium/formint/` |

Backend coverage: ninja CRUD (create/list/patch/delete), pagination,
openapi, fusion envelope, HTMX table/form fragments, render-first, admin
login/dashboard/changelists for loyalty + settings models.

---

## 8. Quick start

```bash
# Backend (API + admin)
cd projects/pos/formint-pos/backend
python3 -m venv .venv && . .venv/bin/activate && pip install -e .
python manage.py migrate
python manage.py --ensure-superuser
python manage.py runserver 127.0.0.1:8000
#   API    → http://127.0.0.1:8000/api/v1/docs
#   Admin  → http://127.0.0.1:8000/admin/  (admin@formint.local / admin123)

# Frontend
cd ../frontend && pnpm install && pnpm dev
#   Shell  → http://localhost:4321/  (proxies /api and /htmx)
```

---

## 9. Extending

- **New model** → add to `formint/models/` + export in `models/__init__.py`,
  run `makemigrations`/`migrate`, register a controller in `controllers.py`
  (via `_config(model, OutSchema)`), and add an admin class in `admin.py`.
- **New API endpoint** → add a `@http_get/@http_post` on a controller or the
  `SystemController` in `api.py`; responses render through the fusion
  encoder automatically.
- **New table/form fragment** → add a component in `components.py`, register
  it in `TABLE_COMPONENTS` / `FORM_COMPONENTS`, and add templates under
  `formint/templates/formint/{tables,forms}/`.
- **Dashboard KPI/chart** → add to the relevant `compute_*` function in
  `dashboard.py`; the template renders any list entry automatically.

---

## 10. Related docs

- [`README.md`](../formint-pos/README.md) — package readme
- [`compatibility-manifest.json`](../formint-pos/migration/compatibility-manifest.json)
- [`POS_ARCHITECTURE.md`](POS_ARCHITECTURE.md) — all-editions architecture
- [`SIDECAR_V2.md`](SIDECAR_V2.md) — sidecar API reference
- [`tests/README.md`](../tests/README.md) — unified test suite
