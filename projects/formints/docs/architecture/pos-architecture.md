# POS Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────┐
│                   Tauri Desktop Shell                │
│  ┌─────────────────────────────────────────────┐   │
│  │          React Frontend (Vite)               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│  │  │ Pages    │  │Components│  │  Store   │   │   │
│  │  │ Home     │  │PageLayout│  │RTK Query │   │   │
│  │  │ Products │  │Cards     │  │  (API)   │   │   │
│  │  │ Sales    │  │Modals    │  │ Pinia    │   │   │
│  │  │ Reports  │  │Forms     │  │ (State)  │   │   │
│  │  └──────────┘  └──────────┘  └──────────┘   │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │ HTTP / WS                      │
│  ┌──────────────────▼──────────────────────────┐   │
│  │        Rust Backend (Tauri Commands)         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│  │  │ Commands │  │  Diesel  │  │  Sidecar │   │   │
│  │  │ products │  │   ORM    │  │  Manager │   │   │
│  │  │  sales   │  │ SQLite   │  │  (Robyn) │   │   │
│  │  └──────────┘  └──────────┘  └──────────┘   │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │                                │
│  ┌──────────────────▼──────────────────────────┐   │
│  │     Python Sidecar (Robyn + Django ORM)      │   │
│  │  - REST API on port 8766                    │   │
│  │  - WebSocket /ws/entities                   │   │
│  │  - Django ORM for shared database            │   │
│  │  - Sync engine (multi-node)                  │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Data Flow

1. **Frontend** → RTK Query mutations → Rust Tauri commands → Diesel ORM → SQLite
2. **Frontend** → HTTP → Python Robyn sidecar → Django ORM → SQLite
3. **WebSocket** → `/ws/entities` ← Entity change events (real-time)
4. **Multi-node** → Sync engine pushes approved changes between instances

## Key Design Decisions

- **SQLite** for embedded database (zero-config, single-file)
- **Tauri commands** for native operations (file I/O, printing, system dialogs)
- **Python sidecar** for complex business logic (sync, webhooks, reporting)
- **RTK Query** for API caching and optimistic UI updates
- **Shared database** between Rust and Python via `restaurant.db`

---

## Cloud Edition — `formintB/` (pos-cloud)

> Hosted multi-terminal SaaS master. Not a Tauri app — a two-package layout:
> `backend/` (Django ASGI server + admin) and `sidecar/` (Robyn async API),
> both sharing `pos_cloud.db`.

```
┌─────────────────────────────────────────────────────────────┐
│            Django backend (backend/, pos-cloud)              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ apps/core     models, Ninja API, viewsets, admin       │  │
│  │ apps/domain   sync_broker, sync_queue, conflict_resolver│  │
│  │ apps/handlers sync_api, sync_dashboard, consumers,      │  │
│  │               fusion fragments                         │  │
│  │ configs/      asgi/wsgi (channels/daphne), Unfold+bolt  │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────┬──────────────────────────┬──────────────────┘
                │ pos_cloud.db (shared)    │ Django ORM
┌───────────────▼──────────────────────────▼──────────────────┐
│            Robyn sidecar (sidecar/, pos-cloud-sidecar) :8767 │
│  server.py → generic CRUD for all core models + /health,     │
│              /stats                                          │
│  routes/fusion.py → /fusion/health, /render-mode, /nav,      │
│                     /session-mode, /assets                   │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow (Cloud)

1. **Branches** → `sync_push` / `heartbeat` WebSockets → Django channels consumers (`apps/handlers/consumers.py`) → broker → `SyncQueueItem` → conflict resolution → broadcast back
2. **Read-heavy clients** → Robyn sidecar (`:8767`) → Django ORM → shared `pos_cloud.db`
3. **Fusion contract** — the sidecar mirrors the Django backend's `/fusion/*` render-mode endpoints so consumers can target either server
