# 📁 POS Full Sidecar Server (`sidecar/`)

## What's Here

**Robyn** async Python server with **Django ORM** providing high-performance REST API (60k+ RPS), WebSocket real-time streaming, and Cloud Master orchestration for the POS Full desktop app.

```
sidecar/
├── server.py                 # 🟢 Robyn app — REST + WebSocket (70+ endpoints)
├── models/                   # 🔵 Django ORM models (managed=True)
│   ├── __init__.py
│   ├── node.py               # Node, Heartbeat, NodeEvent
│   ├── config.py              # DeviceConfig, MasterDevice, CloudLink
│   └── sync.py                # SyncLog
├── posapp/                   # 🔵 Django ORM models (managed=False, Rust-owned)
│   ├── __init__.py
│   └── models.py              # 30+ Rust-mirror tables
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── tests/                    # Pytest test suites
│   ├── test_server.py        # 53 server tests
│   └── test_webhook_e2e.py   # 10 webhook E2E tests
├── Makefile                  # Sidecar commands
├── pyproject.toml            # Python project metadata
└── build.py / build.sh       # Build scripts
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  POS Full Server (Robyn, port 8766)                         │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌────────────────┐ │
│  │ POS API  │ │ Node API │ │ Config  │ │ Sync / Approval │ │
│  │ (CRUD)   │ │(register,│ │(devices,│ │(status, push,   │ │
│  │          │ │ heartbeat)│ │ master, │ │ receive, queue) │ │
│  │          │ │          │ │ cloud)  │ │                 │ │
│  └────▲─────┘ └────▲─────┘ └────▲────┘ └───────▲────────┘ │
│       │            │            │               │          │
│       └────────────┴────────────┴───────────────┘          │
│                         │                                  │
│              Django ORM (full_portal.db)                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ models/node.py  (Node, Heartbeat, NodeEvent)       │    │
│  │ models/config.py (DeviceConfig, MasterDevice, CL)  │    │
│  │ models/sync.py   (SyncLog)                         │    │
│  │ posapp/models.py (30+ Rust-backed, managed=False)  │    │
│  │ shared/models/   (SignalEvent, SyncApproval, Token)│    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────┘

                         │ WebSockets
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  /ws/nodes   — Node event stream (register, heartbeat, ...)│
│  /ws/config  — Config change stream (config, approval, sync)│
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
pip install -r requirements.txt
python3 server.py --port 8766                    # Start Robyn server
DJANGO_SETTINGS_MODULE='' python3 -m pytest      # Run tests
```

## Key Features

| Feature | Description |
|---------|-------------|
| 🔄 **Product Sync** | Master→Child product/config push + Child→Master sales/reports with approval |
| ✅ **Moderated Approvals** | `SyncApproval` model with approve/reject workflow |
| 🔌 **Django Signals** | `config_changed`, `config_synced`, `device_status_changed` wired into endpoints |
| 🌐 **WebSocket Streams** | `/ws/nodes` (node events) + `/ws/config` (config changes) with filters |
| 🔑 **Token Auth** | DeviceToken system with SHA-256 hashing, roles, expiry, capabilities |

## Package Structure

| Path | Purpose | Tag |
|------|---------|:---:|
| `server.py` | Robyn app — all routes, middleware, WS | 🟢 customizable |
| `models/node.py` | Node, Heartbeat, NodeEvent | 🔵 template |
| `models/config.py` | DeviceConfig, MasterDevice, CloudLink | 🔵 template |
| `models/sync.py` | SyncLog | 🔵 template |
| `posapp/models.py` | Rust-mirror models (30+ tables) | 🔵 template |
| `tests/` | Pytest tests (63 total) | 🟢 customizable |

## Related Docs

- [Architecture](ARCHITECTURE.md)
- [Sidecar v2 Reference](../../docs/SIDECAR_V2.md)
- [POS Editons Overview](../README.md)
