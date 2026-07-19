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
| Python/Sanic sidecar API | ❌ | ✅ | ✅ |
| Python/Robyn sidecar (extended) | ❌ | 🟡 | ❌ |
| django-bolt API (Django portal) | ❌ | ❌ | ✅ |
| REST API (35+ endpoints) | ❌ | ✅ | ✅ |
| Invoice PDF generation | ❌ | ✅ | ✅ |
| Chat support widget | ❌ | ✅ | ✅ |
| Cloud CRM sync client | ❌ | ✅ | ✅ |
| Django ORM models (30 tables) | ❌ | ❌ | ✅ |
| WebSocket real-time chat | ❌ | ❌ | ✅ |
| Cross-device data sync | ❌ | ❌ | ✅ |
| Cloud CRM (shared-portal) | ❌ | ✅ | ✅ |
| JSON seed fixtures | ❌ | ❌ | ✅ |
| Change signals (broadcast) | ❌ | ❌ | ✅ |

---

## Minimal Edition

**Directory:** `projects/pos/pos-minimal/`  
**Use case:** Core POS — fast, offline-first, no external dependencies.

```bash
cd pos-minimal && pnpm install && pnpm dev
```

**Architecture:** React → Tauri invoke → Rust → SQLite

---

## Solo Edition

**Directory:** `projects/pos/pos-solo/`  
**Use case:** POS + REST API for external integrations + Cloud CRM sync.

```bash
cd pos-solo && pnpm install
python3 sidecar/server.py --db restaurant.db --port 8765 &
pnpm dev
```

**Architecture:** React → Tauri invoke → Rust → SQLite ← Sanic sidecar → Cloud CRM

**Cloud Sync:** The Solo edition syncs products, sales, and customers to the Full edition's Cloud CRM server via `sync_client.py`.

### Solo Extended (Robyn)

An optional Robyn-based sidecar variant is available for the Solo edition, replacing Sanic with [Robyn](https://github.com/sparckles/Robyn) — a Rust-powered async Python web framework providing:
- Higher throughput and lower latency vs Sanic
- Built-in OpenAPI generation
- Native WebSocket and SSE support
- Pydantic validation integration

```bash
# Solo Extended with Robyn sidecar
cd pos-solo && pnpm install
pip install robyn[all]
python3 sidecar/robyn_server.py --db restaurant.db --port 8765 &
pnpm dev
```

The Robyn variant is opt-in — the original Sanic sidecar remains the default for backward compatibility.

---

## Full Edition

**Directory:** `projects/pos/pos-full/`  
**Use case:** Enterprise POS with Django ORM, WebSocket, Cloud CRM master, cross-device sync, django-bolt high-performance API.

```bash
cd pos-full && pnpm install
pip install -r sidecar/requirements.txt
pip install django-bolt
python3 sidecar/server.py &
pnpm dev
```

**Architecture:** React → Tauri → Rust → SQLite ← Sanic + Django ORM + django-bolt API + WebSocket ← Cloud CRM master

**django-bolt Integration:** The Full edition's Django portal uses [django-bolt](https://github.com/dj-bolt/django-bolt) for high-performance API endpoints (60k+ RPS), replacing standard Django views with Rust-powered async handlers. The bolt API is available at `http://localhost:8080/bolt/` alongside the standard Django admin at `/admin/`.

**Change Signals:** The Full edition includes a tokio broadcast-based change signal system that emits events when settings, products, or CRM entities are modified.

---

## Generating Editions

All editions are generated from the Full edition source:

```bash
cd projects/pos
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
