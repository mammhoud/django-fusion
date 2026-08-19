# ☁️ Cloud CRM & Data Sync

> Cloud CRM server, data synchronization, and multi-store architecture for the POS system.

---

## Architecture

```
┌──────────────────────┐       sync push       ┌──────────────────────┐
│   POS Terminal #1    │ ───────────────────→  │                      │
│   (pos-solo)          │  products, sales,     │   Cloud CRM Server   │
│   port 8765           │  customers            │   (shared-portal/cloud/)   │
└──────────────────────┘                        │   port 8766           │
                                                 │                       │
┌──────────────────────┐       sync push       │  ┌─────────────────┐  │
│   POS Terminal #2    │ ───────────────────→  │  │ CRM Entities    │  │
│   (pos-solo)          │                       │  │ • contacts      │  │
│   port 8765           │                       │  │ • companies     │  │
└──────────────────────┘                        │  │ • deals         │  │
                                                 │  │ • pipelines     │  │
┌──────────────────────┐       sync push       │  │ • activities    │  │
│   POS Terminal #3    │ ───────────────────→  │  │ • notes         │  │
│   (pos-solo)          │                       │  └─────────────────┘  │
│   port 8765           │                       │                       │
└──────────────────────┘                        │  ┌─────────────────┐  │
                                                 │  │ Dashboard       │  │
                    ↓                            │  │ • stats         │  │
           ┌──────────────────┐                  │  │ • export/import │  │
           │  Cloud CRM Master │                  │  └─────────────────┘  │
           │  (shared-portal/cloud/) │                 └──────────────────────┘
           │  • Sanic :8766    │
           │  • CRM CRUD       │
           │  • Sync proxy     │
           │  • Webhooks       │
           └──────────────────┘
```

---

## Components

### Cloud CRM Server (`shared-portal/cloud/`)

| File | Purpose |
|------|---------|
| `server.py` | Standalone Sanic server (port 8766) |
| `crm_api.py` | CRM REST API endpoints |
| `crm_models.py` | CRM data models |
| `sync_proxy.py` | Accepts entity pushes from Solo terminals |
| `sync_models.py` | Sync status tracking models |
| `webhook_receiver.py` | Incoming webhook event handler |
| `sync_client.py` | Client-side sync trigger |

### Solo Sync Client (`pos-solo/sidecar/`)

| File | Purpose |
|------|---------|
| `sync_client.py` | Push POS data to Cloud CRM |
| `sync_routes.py` | Sync API: status, config, trigger, push |
| `webhook_sender.py` | Send webhook events to external services |

---

## Data Flow

### Sync Push (Solo → Cloud)

```
1. POS creates/updates entity (product, sale, customer)
2. Rust backend writes to SQLite
3. Rust emits change signal (tokio broadcast)
4. Sidecar sync_client.py receives signal
5. sync_client.py pushes to Cloud CRM via HTTP POST
6. Cloud sync_proxy.py validates and stores
7. Cloud CRM updates dashboard
```

### Sync Status

```python
# sync_routes.py — Solo edition
# GET /sync/status — Check sync health
# GET /sync/config  — View sync configuration
# POST /sync/trigger — Manually trigger a full sync
# POST /sync/push   — Push specific entity types
```

### Webhook Flow

```
1. Event occurs in POS (e.g., order completed)
2. Sidecar webhook_sender.py fires
3. HTTP POST to configured webhook URL
4. External service receives event
```

---

## Cloud CRM Server

### Start the Server

```bash
cd projects/formints/shared-portal/cloud
pip install -r requirements.txt
python server.py --port 8766
```

### CRM Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/crm/contacts` | List contacts |
| POST | `/crm/contacts` | Create contact |
| GET | `/crm/companies` | List companies |
| POST | `/crm/companies` | Create company |
| GET | `/crm/deals` | List deals |
| POST | `/crm/deals` | Create deal |
| GET | `/crm/pipelines` | List pipelines |
| GET | `/crm/dashboard` | CRM stats |
| POST | `/crm/export` | Export data |
| POST | `/crm/import` | Import data |

### Sync Proxy

```python
# cloud/sync_proxy.py — Accepts pushes from Solo editions
@app.post("/sync/push")
async def sync_push(request):
    """Accept entity pushes from Solo POS terminals.
    
    Body: {
        "source": "pos-solo-terminal-1",
        "entity_type": "products",
        "entities": [...]
    }
    """
    data = request.json
    source = data["source"]
    entity_type = data["entity_type"]
    
    # Validate + store in CRM database
    for entity in data["entities"]:
        store_entity(entity_type, entity)
    
    # Update sync status
    update_sync_status(source, entity_type, "synced")
    
    return {"ok": True, "synced": len(data["entities"])}
```

---

## Cloud Sync Plan (Future)

### Phase 1: Real-time Sync (WebSocket)

Replace periodic HTTP push with WebSocket-based real-time sync:

```
POS Terminal ←→ WebSocket ←→ Cloud CRM
   ↓                              ↓
SQLite                       PostgreSQL
```

### Phase 2: Conflict Resolution

For multi-terminal scenarios where the same entity is modified on two terminals:

```
Algorithm: Last-Write-Wins with merge
1. Each write gets a vector clock
2. Cloud CRM detects conflicts
3. Conflict resolver picks winner or merges
4. Conflicting terminal gets notified
```

### Phase 3: Offline Queue

When a terminal goes offline:

```
1. Queue all changes locally (SQLite queue table)
2. On reconnect, push queue in order
3. Cloud CRM acknowledges each push
4. Terminal clears acknowledged items from queue
```

### Phase 4: Multi-Store Dashboard

Web-based dashboard showing all stores:

```
Cloud CRM Dashboard (React/Vue)
├── Store list (all synced terminals)
├── Per-store sales charts
├── Inventory across stores
├── Employee scheduling
└── Consolidated reports
```

---

## Related

| Topic | Path |
|-------|------|
| Cloud sync plan | [`sync-plan.md`](sync-plan.md) |
| Sidecar overview | [`../sidecar/README.md`](../sidecar/README.md) |
| django-bolt integration | [`../sidecar/django-bolt-integration.md`](../sidecar/django-bolt-integration.md) |
| POS infrastructure | [`../infrastructure.md`](../infrastructure.md) |
