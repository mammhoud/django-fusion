# Formint POS — Architecture

> **Formint POS Professional** is the merged package that consolidates
> `pos-full` (cloud master manager) and `pos-solo` (standalone device) into a
> single product boundary with the same Tauri shell architecture.

| | |
|---|---|
| **Location** | [`../formint-pos/`](../formint-pos/) |
| **Status** | Phase 2 — merge complete + landing-fusion render-mode parity |
| **API** | Django Ninja + ninja-extra (fusion encoder/decoder) |
| **Admin** | Django Unfold dashboard (loyalty/settings focus) |
| **Data components** | django-fusion tables + forms (HTMX) |
| **Render mode** | Dual-mode contract (render-first / data-API), mirroring landing-fusion |
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
│   ├── config/                  # settings (Unfold + fusion render-mode), URLs
│   ├── formint/
│   │   ├── models/              # 45+ merged domain models (pos, menu, node,
│   │   │                        #   config, sync, inventory, ops, hr, notes,
│   │   │                        #   extra, loyalty, approval, token, audit, crm)
│   │   ├── schemas.py           # ninja_schema Out schemas + writable/patch factory
│   │   ├── controllers.py       # ninja-extra ModelController CRUD (45 resources)
│   │   ├── api.py               # NinjaAPI + fusion JSONRenderer + system endpoints
│   │   ├── components.py        # django-fusion table/form data components
│   │   ├── fusion_components.py # branch summary fragment (FusionDualModeMixin)
│   │   ├── core.py              # FormintSite (django-fusion Site — nav source of truth)
│   │   ├── fusion.py            # render-mode/nav/assets contract (get_effective_render_first)
│   │   ├── handlers.py          # class-based HTMX fragment handlers (mirrors landing handlers)
│   │   ├── views.py             # thin URL-facing delegation to handlers + /fusion/* endpoints
│   │   ├── admin.py             # Unfold ModelAdmin registrations (all models)
│   │   ├── dashboard.py         # Unfold dashboard callback (KPIs/charts/tables)
│   │   └── templates/           # fusion table + form templates
│   ├── templates/admin/         # Unfold admin index override (dashboard UI)
│   ├── Makefile                 # backend targets (dev/check/migrate/test/seed/env)
│   ├── manage.py                # CLI + --ensure-superuser bootstrap
│   └── sidecar.py               # PyInstaller sidecar entry point
├── Makefile                     # root orchestrator (frontend + backend + full + env)
├── frontend/                    # Astro shell
│   ├── Makefile                 # frontend targets (install/dev/build/check/test)
│   ├── astro.config.mjs         # dev proxy → backend :8767 (/api, /htmx, /fusion)
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

### 3.5 Fusion render-mode contract (landing-fusion parity)

The backend mirrors landing-fusion's dual-mode content delivery — the same
contract as `projects/landing-fusion/backend/apps/pages/api.py`:

| Endpoint | Description |
|---|---|
| `/api/v1/render-mode` | Report active mode (`fusion-render` vs `data-api`) |
| `/api/v1/navigation` | Nav items from `FormintSite` (single source of truth) |
| `/api/v1/assets` | `FUSION_ASSETS` manifest (bundle parity) |
| `/fusion/render-mode/` | Same report at the fragment path (HTMX shell) |
| `/fusion/navigation/` | Nav JSON at the fragment path |
| `/fusion/assets/` | Asset manifest at the fragment path |

* **`formint/fusion.py`** — `get_effective_render_first(request)` reads the
  `X-Fusion-Render-First: true|false` header (per-request override), falling
  back to `FUSION_RENDER_FIRST_DEFAULT` (env `FUSION_RENDER_FIRST`, default
  `1`). This is the same precedence django-fusion's
  `FusionDualModeMixin.get_effective_render_first()` uses.
* **`formint/core.py`** — `FormintSite(Site)` from `django_fusion.routes.core.sites`
  with `NAV_ITEMS` (Home / Data / Admin) — mirrors landing-fusion's
  `apps/core/site.py`.
* **`formint/handlers.py`** — class-based HTMX fragment handlers
  (`BranchSummaryHandler`, `TableFragmentHandler`, `FormFragmentHandler`)
  mirroring landing-fusion's `apps/handlers/views.py` organization;
  `views.py` stays a thin URL-facing delegation layer so routes never break.

Settings (`config/settings.py`):

```python
FUSION_RENDER_FIRST_DEFAULT = os.environ.get('FUSION_RENDER_FIRST', '1') == '1'
COMPONENTS_FUSION_RENDER_FIRST_DEFAULT = FUSION_RENDER_FIRST_DEFAULT
FUSION_ASSETS = {...}  # frontend bundle parity
FUSION_ASSET_PIPELINE = {...}
```

### 3.6 Unfold admin (`/admin/`)

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
| Backend (35 tests) | `tests/py/formint/run.sh` | `manage.py test formint` |
| Frontend contract | `tests/js/vitest.config.ts` | `npx vitest run` |
| Admin selenium | `tests/selenium/formint/` | `pytest tests/selenium/formint/` |

Backend coverage: ninja CRUD (create/list/patch/delete), pagination,
openapi, fusion envelope, HTMX table/form fragments, render-first + data-
mode (header override), render-mode/navigation/assets endpoints, admin
login/dashboard/changelists for loyalty + settings models.

---

## 8. Quick start

```bash
# One-shot: install + seed + run both servers (backend :8767 + frontend :4321)
cd projects/pos/formint-pos
make install        # backend .venv + deps + migrate + frontend npm install
make seed           # migrate + idempotent superuser (admin@formint.local / admin123)
make env            # tmux: backend :8767 + frontend :4321 (proxies /api, /htmx, /fusion)
#   API      → http://127.0.0.1:8767/api/v1/docs
#   Admin    → http://127.0.0.1:8767/admin/
#   Shell    → http://127.0.0.1:4321/
#   Render   → http://127.0.0.1:4321/fusion/render-mode/

make status         # show tmux sessions + endpoint health
make stop           # stop the tmux env
```

---

## 9. Make commands

The package ships three Makefiles with full delegation (mirrors
landing-fusion's root + backend split):

**`formint-pos/Makefile`** (root orchestrator)

| Command | Action |
|---|---|
| `make install` | Backend .venv + deps + migrate + frontend npm install |
| `make seed` | Migrate + idempotent superuser |
| `make env` | Run backend (:8767) + frontend (:4321) in tmux + health check |
| `make dev-backend` / `make dev-frontend` | Foreground servers |
| `make stop` / `make status` | Manage the running env |
| `make check` | Django check + astro check |
| `make test` | Backend 35-test suite + frontend contract tests |
| `make build` / `make preview` | Frontend build (+ collectstatic) / preview |
| `make clean` | Remove db + staticfiles + node_modules |
| `make backend-*` / `make frontend-*` | Delegate to the layer Makefiles |
| `make tauri` / `make tauri-dev` / `make tauri-build` | Tauri CLI / dev / build |

**`formint-pos/backend/Makefile`** — `install`, `migrate`, `dev` (:8767),
`server` (gunicorn), `check`, `test`, `seed`, `ensure-superuser`, `shell`,
`collectstatic`, `clean`.

**`formint-pos/frontend/Makefile`** — `install`, `dev` (:4321), `build`,
`preview`, `check`, `test` (vitest), `clean`.

Parent `projects/pos/Makefile` delegates: `make formint-install`,
`make formint-run` (:8767), `make formint-env`, `make formint-stop`,
`make formint-test`, `make formint-check`, `make formint-clean`.

---

## 10. Extending

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

## 11. Related docs

- [`README.md`](../formint-pos/README.md) — package readme
- [`compatibility-manifest.json`](../formint-pos/migration/compatibility-manifest.json)
- [`POS_ARCHITECTURE.md`](POS_ARCHITECTURE.md) — all-editions architecture
- [`SIDECAR_V2.md`](SIDECAR_V2.md) — sidecar API reference
- [`tests/README.md`](../tests/README.md) — unified test suite

## 12. django-fusion enhancement surface (available features)

Features from the django-fusion library that Formint uses today and others
that can be enabled incrementally:

**In use:**

- `FusionDualModeMixin` + `FragmentComponent` — `formint/fusion_components.py`
  (render-first vs data-mode with header/session precedence).
- `TableMixin` + `RowGenerator` (`django_fusion.fragments.tables`) —
  `formint/components.py` table fragments.
- `FormMixin` + `FormTagGenerator` (`django_fusion.fragments.forms`) —
  form fragments with model defaults patched.
- `ModelSchema` (`django_fusion.routes.schemas.model_schema`) — decoders for
  every Out schema; `JSONRenderer` (encoder) wraps every API response.
- `Site` (`django_fusion.routes.core.sites`) — `FormintSite` nav context.
- `fusion_json_response` (`routes.rendering.renderers`) — render-first
  table responses.

**Available to enable (settings-only or small additions):**

- `register_include_paths()` + `COMPONENTS_INCLUDE_PATH_ROOTS` — bridge any
  `{% include %}` partial into the component registry for stable identity.
- `COMPONENTS_ENABLE_BLOCK_ATTRS` — emit `data-block-*` attributes on
  components for headless/CMS inspection.
- `FusionCodec` / `get_session_render_first` (`routes.rendering.session`) —
  per-session render-mode preference (beyond the header override).
- `django_fusion.plugins.htmx.is_htmx_request` — centralized HTMX detection
  (already used internally by dual-mode).
- `PageHandler` (`routes.pages.handler`) — full-page fragment/layout render
  pipeline (used by landing-fusion; Formint currently uses lean fragments).
- `comp`/`comp_include` template tags + component registry — server-side
  component reuse across templates.
- `django_fusion.contrib.api` — extra API helpers for Ninja-based apps.
