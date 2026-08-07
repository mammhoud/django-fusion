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
