# 📁 POS-Solo Sidecar Server (`sidecar/`)

## What's Here

**Robyn** async Python server with **Django ORM** providing a consolidated REST API (60+ endpoints), WebSocket real-time config streaming, and cloud sync client for the POS Solo desktop app.

```
sidecar/
├── server.py                 # 🟢 Robyn app — all routes (60+ endpoints) + middleware + WS
├── models/                   # 🔵 Django ORM models (managed=True)
│   ├── __init__.py
│   ├── pos.py                # Category, Product, Customer, Sale, SaleItem, etc.
│   ├── menu.py               # MenuItem, Menu, MenuItemAssignment
│   ├── node.py               # Node, Heartbeat, NodeEvent
│   ├── config.py              # DeviceConfig, MasterDevice, CloudLink
│   └── sync.py                # SyncLog
├── tests/
│   └── test_unified_api.py   # 155 pytest tests
├── requirements.txt          # Python dependencies
├── Makefile                  # Sidecar commands
├── build.py / build.sh       # Build scripts
├── ARCHITECTURE.md           # Architecture docs
└── README.md                 # This file
```

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  POS Solo Server (Robyn, port 8765)                  │
│  ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐│
│  │ POS API │ │Menu API│ │Node API│ │ Sync / Config││
│  │ (CRUD)  │ │ (CRUD) │ │(manage)│ │ (status,     ││
│  └────▲────┘ └────▲───┘ └────▲───┘ │  push, WS)  ││
│       │           │          │     └──────▲───────┘│
│       └───────────┴──────────┴────────────┘        │
│                         │                          │
│              Django ORM (restaurant.db)             │
│  ┌───────────────────────────────────────────────┐ │
│  │ models/pos.py   (Product, Sale, Customer...)  │ │
│  │ models/menu.py  (MenuItem, Menu, Assignment)  │ │
│  │ models/node.py  (Node, Heartbeat, Event)      │ │
│  │ models/config.py (DeviceConfig, Master, Link) │ │
│  │ models/sync.py  (SyncLog)                     │ │
│  │ shared/models/  (SignalEvent, Approval, Token)│ │
│  └───────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## Quick Start

```bash
pip install -r requirements.txt
python3 server.py --port 8765                     # Start Robyn server
DJANGO_SETTINGS_MODULE='' python3 -m pytest -v    # Run 155 tests
```

## Key Features

| Feature | Description |
|---------|-------------|
| ⚡ **High Performance** | Robyn Rust-powered async server (60k+ RPS) |
| 🔄 **Django ORM** | 15 unified models in organized packages |
| 🌐 **WebSocket** | Real-time config streaming via `/ws/config` |
| 🔑 **Token Auth** | DeviceToken SHA-256 auth system |
| ☁️ **Cloud Sync** | Push products, sales, nodes to Cloud Master |
| ✅ **Full Test Suite** | 155 tests covering CRUD + relationships + edge cases |

## Models Package Structure

| Module | Models | Purpose |
|--------|--------|---------|
| `models/pos.py` | Category, Product, Customer, Sale, SaleItem, InventoryTransaction, Employee | POS core entities |
| `models/menu.py` | MenuItem, Menu, MenuItemAssignment | Menu management |
| `models/node.py` | Node, Heartbeat, NodeEvent | Node registry |
| `models/config.py` | DeviceConfig, MasterDevice, CloudLink | Configuration management |
| `models/sync.py` | SyncLog | Sync operation audit |

## Related Docs

- [Architecture](ARCHITECTURE.md)
- [Sidecar v2 Reference](../../docs/SIDECAR_V2.md)
