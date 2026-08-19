# POS — Editions Guide

> **3 Editions:** Minimal | Solo | Full  
> All share the same React 19 + Tauri 2 + Rust + SQLite core.

---

## Edition Comparison

| Feature | Minimal | Solo | Full |
|---------|:-------:|:----:|:----:|
| React 19 + TypeScript frontend | ✅ | ✅ | ✅ |
| Tauri 2 + Rust backend | ✅ | ✅ | ✅ |
| SQLite database (37 tables) | ✅ | ✅ | ✅ |
| i18n (en/fr/ar) | ✅ | ✅ | ✅ |
| POS terminal + inventory + analytics | ✅ | ✅ | ✅ |
| Employees, payroll, scheduling | ✅ | ✅ | ✅ |
| Kitchen display system | ✅ | ✅ | ✅ |
| POS-KO Gaming Center | ✅ | ✅ | ✅ |
| Django Portal (admin UI) | ✅ | ✅ | ✅ |
| Python/Robyn sidecar API | ❌ | ✅ (60+ endpoints) | ✅ (70+ endpoints) |
| django-bolt API (Django portal) | ❌ | ❌ | ✅ |
| REST API (35+ endpoints) | ❌ | ✅ | ✅ |
| Invoice PDF generation | ❌ | ✅ | ✅ |
| Chat support widget | ❌ | ✅ | ✅ |
| Cloud CRM sync client | ❌ | ✅ | ✅ |
| Django ORM models (organized packages) | ❌ | ✅ 17 tables (models/) | ✅ 7+30 tables (models/ + posapp/) |
| WebSocket real-time streaming | ❌ | ✅ /ws/config | ✅ /ws/config + /ws/nodes |
| Django Signals (config_changed, etc.) | ❌ | ✅ | ✅ |
| Token-based auth (DeviceToken) | ❌ | ✅ | ✅ |
| Moderated Approvals (SyncApproval) | ❌ | ✅ | ✅ |
| Product Sync Engine | ❌ | ✅ (child) | ✅ (master) |
| Cross-device data sync | ❌ | ✅ (push to master) | ✅ (cloud master) |
| Cloud CRM (shared-portal) | ❌ | ✅ sync client | ✅ sync master |
| JSON seed fixtures | ❌ | ❌ | ✅ |
| Change signals (broadcast) | ❌ | ❌ | ✅ |
| django-bolt API | ❌ | ❌ | ✅ (60k+ RPS) |

---

## Minimal Edition

**Directory:** `projects/formints/pos-minimal/`  
**Use case:** Core POS — fast, offline-first, no external dependencies.

```bash
cd pos-minimal && pnpm install && pnpm dev
```

**Architecture:** React → Tauri invoke → Rust → SQLite

---

## Solo Edition

**Directory:** `projects/formints/pos-solo/`  
**Use case:** POS + REST API for external integrations + Cloud CRM sync.

```bash
cd pos-solo && pnpm install
python3 sidecar/server.py --db restaurant.db --port 8765 &
pnpm dev
```

**Architecture:** React → Tauri invoke → Rust → SQLite ← Robyn sidecar (60+ endpoints) → Cloud Master

**Models:** Organized in `sidecar/models/` package:
- `models/pos.py` — Category, Product, Customer, Sale, SaleItem, Inventory, Employee
- `models/menu.py` — MenuItem, Menu, MenuItemAssignment
- `models/node.py` — Node, Heartbeat, NodeEvent
- `models/config.py` — DeviceConfig, MasterDevice, CloudLink
- `models/sync.py` — SyncLog

**Cloud Sync:** The Solo edition pushes products, sales, and nodes to the Full edition's Cloud Master via the `SyncClient`.

```bash
cd pos-solo && pnpm install
python3 sidecar/server.py --port 8765 &
pnpm dev
```

---

## Full Edition

**Directory:** `projects/formints/pos-full/`  
**Use case:** Enterprise POS with Django ORM, WebSocket, Cloud CRM master, cross-device sync, django-bolt high-performance API.

```bash
cd pos-full && pnpm install
pip install -r sidecar/requirements.txt
pip install django-bolt
python3 sidecar/server.py &
pnpm dev
```

**Architecture:** React → Tauri → Rust → SQLite ← Robyn (70+ endpoints) + Django ORM + WebSocket ← Cloud CRM master

**Models:** Organized in `sidecar/models/` package + `posapp/models.py`:
- `models/node.py` — Node, Heartbeat, NodeEvent (managed=True)
- `models/config.py` — DeviceConfig, MasterDevice, CloudLink (managed=True)
- `models/sync.py` — SyncLog (managed=True)
- `posapp/models.py` — 30+ Rust-mirror tables (managed=False)

**Django Signals:** Both editions use signals (`config_changed`, `config_synced`, `device_status_changed`) wired into all endpoints via `shared/signals/` and `shared/handlers/signal.py`.

**django-bolt Integration:** The Full edition's Django portal uses [django-bolt](https://github.com/dj-bolt/django-bolt) for high-performance API endpoints (60k+ RPS) at `http://localhost:8080/bolt/`.

**Token Auth:** Both editions support DeviceToken-based authentication via `shared/models/token.py` + `shared/middleware/auth.py`.

```bash
cd pos-full && pnpm install
pip install -r sidecar/requirements.txt
python3 sidecar/server.py --port 8766 &
pnpm dev
```

---

## Generating Editions

All editions are generated from the Full edition source:

```bash
cd projects/formints
make editions          # Generate minimal + solo from full
```

The generation strips Solo-only and Full-only files while preserving the shared core.

---

## Related

| Resource | Path |
|----------|------|
| POS overview | [`README.md`](README.md) |
| Rust backend | [`rust-backend.md`](backend/rust-backend.md) |
| TypeScript frontend | [`typescript-frontend.md`](frontend/typescript-frontend.md) |
| Sidecar API | [`sidecar-readme.md`](sidecar/README.md) |
