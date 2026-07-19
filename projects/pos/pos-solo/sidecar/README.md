# 📁 POS-Solo Sidecar Server (`sidecar/`)

## What's Here

Python/Sanic server providing HTTP REST API, WebSocket support, and **cloud CRM sync** for the POS Solo desktop app.

```
sidecar/
├── server.py           # 🔴 Sanic app — all routes + WS + sync blueprint
├── sync_client.py      # 🟢 HTTP client for cloud CRM sync (shared-portal/cloud/)
├── sync_routes.py      # 🟢 Sync API blueprint (status, config, trigger, push)
├── requirements.txt    #    Python dependencies (sanic + httpx)
├── build.py            #    PyInstaller build script
├── build.sh            #    Build shell wrapper
└── posapp/             # 🔵 Django models (Category, Product, Customer, Sale, ...)
    ├── __init__.py
    └── models.py       #    Independent Django models (not Rust mirrors)
```

## Customization Tags

| Module | Tag | How to customize |
|--------|-----|-----------------|
| `server.py` routes | 🟢 `customizable` | Add new endpoints |
| `server.py` WebSocket | 🔴 `not-customizable` | Protocol must match frontend `chat.ts` |
| `server.py` INVOICE_TEMPLATE | 🟢 `customizable` | Edit HTML template freely |
| `server.py` DESIGN_CONFIGS | 🟢 `customizable` | Add new invoice designs |
| `sync_client.py` | 🟢 `customizable` | Add push methods for new entity types |
| `sync_routes.py` | 🟢 `customizable` | Add new sync API endpoints |
| `posapp/models.py` | 🔵 `template` | Django models — independent from Rust schema |

## Cloud CRM Sync

The solo edition can sync local POS data to the **pos-full cloud CRM server** (`shared-portal/cloud/`).

### Sync Architecture

```
+--------------------+       HTTP REST        +---------------------+
|  pos-solo          |  ──────────────────>  |  shared-portal/cloud/    |
|  sidecar/server.py |  push products, sales |  cloud CRM server   |
|  port 8765         |  <──────────────────  |  port 8766          |
+--------------------+       status, config   +---------------------+
```

### Sync API Endpoints (Blueprint: `/api/sync/*`)

| Endpoint | Description |
|----------|-------------|
| `GET /api/sync/status` | Current sync state (config, last_sync, items) |
| `POST /api/sync/config` | Update sync config (cloud_url, interval, api_key) |
| `POST /api/sync/trigger` | Trigger manual sync |
| `GET /api/sync/log` | Sync history log |
| `POST /api/sync/push/<type>` | Push single entity (products, sales, customers, etc.) |
| `POST /api/sync/bulk-push/<type>` | Bulk-push multiple entities |

### Quick Start (with Cloud CRM)

```bash
# Terminal 1: Start cloud CRM server
cd ../shared-portal/cloud && python3 server.py --port 8766

# Terminal 2: Start solo sidecar with sync
cd ../pos-solo/sidecar && python3 server.py --db ../restaurant.db --port 8765

# Configure sync
curl -X POST http://127.0.0.1:8765/api/sync/config \
  -H "Content-Type: application/json" \
  -d '{"cloud_url": "http://localhost:8766", "sync_interval": 60}'
```

## Running

```bash
pip install -r requirements.txt
python server.py --db ../restaurant.db --port 8765
```

## Reference

- [POS-Solo README →](../README.md)
- [POS-Full Cloud CRM →](../../shared-portal/cloud/README.md)
- [Sidecar Docs →](../../docs/server/README.md)
- [WebSocket Protocol →](../../docs/server/websocket.md)
