# Formint Django server

This directory is the application backend for the Formint Tauri shell.
Django owns domain rules, persistence, permissions, audit, and the first
`django-fusion` fragment render. Rust only supervises the process and exposes
native capabilities.

## Local development

```bash
cd projects/formints/formint-pro/server
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python manage.py runserver 127.0.0.1:8767
```

The Astro dev proxy and the Tauri shell use port `8767`. Browser requests to
`/htmx/` and `/fusion/` remain same-origin from the frontend through the dev
proxy.

## Admin panel (Unfold)

The merged package ships a modern Unfold-themed Django admin panel covering
**loyalty & settings** plus the full POS domain:

| Section | Models |
|---|---|
| **Loyalty & Clients** | Client Categories (people as a client category), Loyalty Transactions (points ledger), Customers |
| **Settings** | User Settings (per-user POS settings mirroring the front Settings page), Users, Groups |
| **POS Core** | Products, Categories, Sales, Employees, Inventory |
| **Operations** | Suppliers, Purchase Orders, Kitchen Tickets, Support Tickets, Menu |
| **Nodes & Sync** | Nodes, Heartbeats, Events, Device Configs, Master Devices, Cloud Links, Sync Logs |
| **CRM** | Companies, Pipelines, Stages, Contacts, Deals, Activities, Notes |

### Dashboard

The admin index is a custom dashboard with KPI cards (today's sales, monthly
revenue, AOV, loyalty members, points issued/redeemed, settings rows, 2FA
coverage, …), Chart.js charts (revenue, top products, payment methods, hourly
activity, loyalty transaction mix), and recent activity tables. Injected via
`UNFOLD["DASHBOARD_CALLBACK"]` → `formint.dashboard.formint_dashboard_callback`.

### Run

```bash
cd projects/formints/formint-pro/backend
python manage.py migrate
python manage.py --ensure-superuser   # auto-creates admin + UserSettings row
python manage.py runserver 127.0.0.1:8000
# → http://localhost:8000/admin/
```

Superuser env vars (defaults): `FORMINT_ADMIN_EMAIL=admin@formint.local`,
`FORMINT_ADMIN_PASSWORD=admin123`, `FORMINT_ADMIN_NAME=Formint Admin`.
The command is idempotent and seeds a `UserSettings` row for the admin user.

> **Deployment warning:** when `DJANGO_DEBUG=0`, `--ensure-superuser` refuses
to create an account with the default password — always set a strong
`FORMINT_ADMIN_PASSWORD` (see [`../.env.example`](../.env.example)).

## Tauri server packaging

Build a platform-specific executable named `formint-backend` and place it in
`../src-tauri/binaries/` with Tauri's target-triple suffix (see
`../src-tauri/tauri.conf.json` → `externalBin` and `src-tauri/src/server.rs`).

The binary is intentionally not committed (gitignored by `src-tauri/.gitignore`).

From this directory, with the `.venv` already created (`make install`):

```bash
# 1. Install the build tool once (PyInstaller) — the app deps come from the venv.
.venv/bin/pip install pyinstaller

# 2. Freeze the Django server into a onefile executable.
.venv/bin/pyinstaller formint-backend.spec --clean --noconfirm

# 3. Drop it where Tauri expects it, with the host target-triple suffix.
cp dist/formint-backend \
  ../src-tauri/binaries/formint-backend-$(rustc -vV | sed -n 's/^host: //p')

# Smoke test: the binary must pass Django system checks.
../src-tauri/binaries/formint-backend-$(rustc -vV | sed -n 's/^host: //p') check
```

Or use the convenience target: `make server-binary` (root Makefile).

> **Why the spec, not `pyinstaller --onefile server.py`?** Django discovers
> apps dynamically (`configs/`, `formint/`, `models/`, `wagtail`, `unfold`,
> `django_fusion`, …), so the spec (`server/formint-backend.spec`) collects
> every app submodule plus template/metadata data files. It also adds the
> project dir to `sys.path` — the spec process cannot import local packages
> otherwise.
>
> **django-bolt is optional.** `configs/urls.py` guards its absence
> (`HAS_DJANGO_BOLT` in `configs/__init__.py`), so the venv/recipe above
> intentionally omits it to avoid a Rust/maturin build.

Release automation should build it from the locked backend environment,
checksum it, and attach the checksum to the release manifest.

## Rendering boundary

- `formint/fusion_components.py` is the first django-fusion component.
- `formint/views.py` exposes the explicit `X-Fusion-Render-First: true` proof
  path and the lean HTMX data path.
- Astro owns page layout, skeletons, retry, and empty/error states.
- No Wagtail or backend-rendered full page is required by this server.
