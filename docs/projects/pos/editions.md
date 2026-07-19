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
| REST API (35+ endpoints) | ❌ | ✅ | ✅ |
| Invoice PDF generation | ❌ | ✅ | ✅ |
| Chat support widget | ❌ | ✅ | ✅ |
| Cloud CRM sync client | ❌ | ✅ | ✅ |
| Django ORM models (30 tables) | ❌ | ❌ | ✅ |
| WebSocket real-time chat | ❌ | ❌ | ✅ |
| Cross-device data sync | ❌ | ❌ | ✅ |
| Cloud CRM master server | ❌ | ❌ | ✅ |
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

---

## Full Edition

**Directory:** `projects/pos/pos-full/`  
**Use case:** Enterprise POS with Django ORM, WebSocket, Cloud CRM master, cross-device sync.

```bash
cd pos-full && pnpm install
pip install -r sidecar/requirements.txt
python3 sidecar/server.py &
pnpm dev
```

**Architecture:** React → Tauri → Rust → SQLite ← Sanic + Django ORM + WebSocket ← Cloud CRM master

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
