# POS Solo

> Desktop POS + Python/Sanic sidecar API server with cloud CRM sync.

This is the **solo edition** of POS (formerly pos-extended). It includes everything from the
minimal edition **plus** a Python/Sanic sidecar server providing a REST API,
WebSocket support, and **cloud CRM sync** to pos-full's cloud server.

## What's Included

Everything from minimal, plus:

- **Python/Sanic sidecar server** (`sidecar/server.py`)
- **REST API** (35+ endpoints for products, sales, inventory, customers...)
- **WebSocket support** for real-time communication
- **Cloud CRM sync** — push products, sales, customers to pos-full/cloud/
- **Sync client** (`sidecar/sync_client.py`) — HTTP client for cloud CRM
- **Sync API** (`sidecar/sync_routes.py`) — manage sync status, trigger, logs
- **Background sync loop** — automatic periodic sync with configurable interval
- **Django Ninja-style endpoints** via Sanic Blueprints
- **Django cache integration** — `django.core.cache` for sync state
- **Invoice PDF generation** (jspdf-based)
- **Chat support widget** (connected to sidecar)
- **Sidecar build scripts** (PyInstaller-based)

## What's NOT Included

- Django ORM models (`sidecar/posapp/` — Django app directory removed)
- JSON seed fixtures for Django
- Full cloud CRM server (that's in `pos-full/cloud/`)

> Need full cloud CRM server? Use the [`pos-full`](../pos-full/) edition.

## Quick Start

```bash
pnpm install && cd src-tauri && cargo fetch && cd ..
cd sidecar && pip install -r requirements.txt && cd ..

# Terminal 1: Start sidecar server
python3 sidecar/server.py

# Terminal 2: Start frontend
pnpm dev
```

## Cloud CRM Sync

The solo edition can sync local POS data to the pos-full cloud CRM server:

```bash
# Start cloud CRM server (separate terminal)
cd ../pos-full/cloud && python3 server.py --port 8766

# Configure sync on solo sidecar
curl -X POST http://127.0.0.1:8765/api/sync/config \
  -H "Content-Type: application/json" \
  -d '{"cloud_url": "http://localhost:8766", "sync_interval": 60}'

# Check sync status
curl http://127.0.0.1:8765/api/sync/status

# Trigger manual sync
curl -X POST http://127.0.0.1:8765/api/sync/trigger
```

## Sidecar API

The sidecar runs on `http://127.0.0.1:8765` by default.

```bash
# Health check
curl http://127.0.0.1:8765/health

# List products
curl http://127.0.0.1:8765/api/products

# Sync status
curl http://127.0.0.1:8765/api/sync/status

# WebSocket chat
ws://127.0.0.1:8765/ws/chat
```

## Sync Architecture

```
+-------------------+       HTTP REST        +-------------------+
|  pos-solo         |  ──────────────────>  |  pos-full/cloud/  |
|  sidecar/server.py |  push products, sales |  cloud CRM server |
|  port 8765        |  <──────────────────  |  port 8766        |
+-------------------+       pull CRM data    +-------------------+
```

## Build

```bash
pnpm build:desktop     # Production desktop app
pnpm build:sidecar     # Build sidecar binary (PyInstaller)
```

## Environment

```bash
SUPERUSER_EMAIL=admin@pos.local
SUPERUSER_PASSWORD=changeme
DATABASE_URL=restaurant.db
SIDECAR_HOST=127.0.0.1
SIDECAR_PORT=8765
CLOUD_CRM_URL=http://localhost:8766
CLOUD_CRM_API_KEY=
SYNC_INTERVAL=60
```
