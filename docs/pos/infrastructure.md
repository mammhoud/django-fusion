# 🔧 POS — Infrastructure

> Infrastructure specifics for the POS (Point of Sale) Tauri desktop application.

---

## Editions & Infrastructure

| Edition | Backend | Frontend | Database |
|---------|---------|----------|----------|
| **Minimal** | Embedded Rust | React 19 (Tauri) | SQLite (file) |
| **Solo** | Robyn + Django ORM (sidecar) | React 19 (Tauri) | SQLite (file, solo_portal.db) |
| **Full** | Robyn + Django ORM + posapp (sidecar) | React 19 (Tauri) | SQLite (file, full_portal.db) |

---

## Sidecar Architecture

Both editions use **Robyn** (Rust-powered Python async framework) with **Django ORM**.

### Solo (Standalone Node)

```
┌────────────────────────────────────────────┐
│     Tauri App / REST Client                 │
│     (port 1420 for dev)                     │
└──────────────────┬─────────────────────────┘
                   │ HTTP REST / WebSocket
┌──────────────────▼─────────────────────────┐
│  Robyn Server (port 8765)                   │
│  ┌─────────────────────────────────────┐   │
│  │  Django ORM (solo_portal.db)        │   │
│  │  models/pos.py, menu.py, node.py,   │   │
│  │  models/config.py, sync.py          │   │
│  └─────────────────────────────────────┘   │
│  • 60+ REST endpoints                      │
│  • WebSocket /ws/config                    │
│  • Cloud sync client → Full master         │
└────────────────────────────────────────────┘
```

### Full (Cloud Master)

```
┌──────────────────┐     ┌──────────────────┐
│  Tauri App #1    │     │  Tauri App #2    │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         └──────────┬─────────────┘
                    │ HTTP REST
┌───────────────────▼─────────────────────────┐
│  Robyn Server (port 8766)                   │
│  ┌─────────────────────────────────────┐   │
│  │  Django ORM (full_portal.db)        │   │
│  │  models/node.py, config.py, sync.py │   │
│  │  posapp/models.py (Rust-backed)     │   │
│  └─────────────────────────────────────┘   │
│  • 70+ REST endpoints                      │
│  • WebSocket /ws/nodes + /ws/config        │
│  • Approval + product sync engine          │
│  • django-bolt API (option, 60k+ RPS)      │
└────────────────────────────────────────────┘

                    │ accepts pushes from
┌───────────────────▼─────────────────────────┐
│  POS Solo / Minimal Nodes                   │
│  (port 8765)                                │
└────────────────────────────────────────────┘
```

### Shared Module Infrastructure

```
projects/pos/shared/        (reusable across both editions)
├── signals/                Django signal definitions
├── models/                 Shared models (audit, approval, token)
├── handlers/               @receiver signal handlers
├── services/               ProductSyncEngine
├── middleware/              Auth middleware (bearer token + API key)
├── api/                    CRUD helpers (_ser, _register_crud)
├── portal_viewsets.py      Django Portal viewsets
└── portal_urls.py          Portal URL patterns
```

---

## Network Requirements

| Edition | Network |
|---------|---------|
| Minimal | None (embedded) |
| Solo | None (localhost sidecar) |
| Full | LAN/WiFi for multi-terminal |

### Port Assignments

| Service | Port | Protocol |
|---------|------|----------|
| Solo Robyn API | `8765` | HTTP REST + WebSocket |
| Full Robyn API | `8766` | HTTP REST + WebSocket |
| Solo Django Portal | `8080` | HTTP (Django) |
| Full Django Portal | `8082` | HTTP (Django) |
| Full Bolt API | `8082/bolt` | HTTP (django-bolt) |
| Tauri Dev Server | `1420` | HTTP (Vite) |
| Cloud CRM (legacy) | `8767` | HTTP (planned) |

---

## Build

```bash
# Solo sidecar
cd projects/pos/pos-solo/sidecar
pip install -r requirements.txt
python3 server.py --port 8765
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -v  # 155 tests

# Full sidecar
cd projects/pos/pos-full/sidecar
pip install -r requirements.txt
python3 server.py --port 8766
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -v  # 63 tests
```

---

## Related

| Topic | Path |
|-------|------|
| POS editions | [`editions.md`](editions.md) |
| Rust backend | [`rust-backend.md`](backend/rust-backend.md) |
| TypeScript frontend | [`typescript-frontend.md`](frontend/typescript-frontend.md) |
| Sidecar API | [`sidecar-readme.md`](sidecar/README.md) |
