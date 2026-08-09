# POS Architecture

> **Last Updated:** 9 August 2026  

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

> Hosted multi-terminal SaaS master. Not a Tauri app — a single Django package
> (`pos-cloud`, `backend/`) serving the full surface on `:8767` (API + fusion
> contract + Community-UI bridges) and the bolt/unfold admin on `:8082`, over
> `pos_cloud.db`. The Robyn sidecar that previously served this surface has
> been removed — Django answers the same paths.

```
┌─────────────────────────────────────────────────────────────┐
│            Django backend (backend/, pos-cloud) :8767        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ apps/core     models, Ninja API, viewsets, admin       │  │
│  │ apps/domain   sync_broker, sync_queue, conflict_resolver│  │
│  │ apps/handlers sync_api, sync_dashboard, consumers,      │  │
│  │               fusion.py + surface.py (fusion contract,  │  │
│  │               root CRUD, /api/* bridges, /stats)       │  │
│  │ configs/      asgi/wsgi (channels/daphne), Unfold+bolt  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow (Cloud)

1. **Branches** → `sync_push` / `heartbeat` WebSockets → Django channels consumers (`apps/handlers/consumers.py`) → broker → `SyncQueueItem` → conflict resolution → broadcast back
2. **Read-heavy clients** → Django (`:8767`) → Django ORM → `pos_cloud.db` (the `/fusion/*` contract, root CRUD, and `/api/*` bridges are served directly by Django)
3. **Fusion contract** — `apps/handlers/fusion.py` mirrors the endpoint contract the sidecar previously exposed so consumers can target the same paths unchanged
