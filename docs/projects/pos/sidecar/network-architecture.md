# POS Network Architecture

> Master document for the three-tier POS network architecture:
> **Minimal (Node)** → **Solo (Server/Aggregator)** → **Full/Cloud (Master)**

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        POS NETWORK TOPOLOGY                           │
│                                                                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐  │
│  │  MINIMAL      │     │  SOLO         │     │  FULL / MASTER       │  │
│  │  (Node)       │────▶│  (Server)     │────▶│  (Cloud CRM)         │  │
│  │               │     │               │     │                      │  │
│  │ sidecar/      │     │ sidecar/      │     │ cloud/               │  │
│  │  node_agent   │     │  server.py    │     │  server.py           │  │
│  │               │     │  node_scanner │     │  crm_api.py          │  │
│  │ port: none    │     │  webhook_send │     │  sync_proxy.py       │  │
│  │               │     │  sync_client  │     │  webhook_receiver    │  │
│  │ node_id: UUID │     │  sync_routes  │     │  sync_client.py      │  │
│  └──────────────┘     └──────────────┘     └──────────────────────┘  │
│         │                     │                       │               │
│         │  POST heartbeats    │  POST webhooks        │               │
│         │  + transactions     │  + aggregated data    │  stores in    │
│         └─────────────────────┘───────────────────────┘  JSON files   │
│                                                                       │
│  Webhooks: node_aggregate │ transaction_batch │ product_update        │
│           settings_sync   │ heartbeat         │                       │
└──────────────────────────────────────────────────────────────────────┘
```

## Edition Roles

| Edition | Role | Sidecar | Network Function |
|---------|------|---------|-----------------|
| **Minimal** | Node/Client | `node_agent.py` | Sends heartbeats to Solo; no API server |
| **Solo** | Server/Aggregator | `server.py` + `node_scanner.py` + `webhook_sender.py` + `sync_routes.py` | Accepts node connections; aggregates & forwards to Master |
| **Full** | Master/Cloud | `server.py` (sidecar) + `cloud/` (standalone CRM) | Receives webhooks; stores CRM data; sync proxy |

## Data Flow

### 1. Node Registration (Minimal → Solo)

```
Minimal Node                 Solo Server
    │                            │
    │  POST /api/nodes/<id>/     │
    │       heartbeat            │
    │  {node_id, status,         │
    │   product_count,           │
    │   last_transactions}       │
    ├───────────────────────────▶│  Registers node in
    │                            │  node_registry.json
    │  {"status":"registered"}   │
    │◀───────────────────────────│
```

**Node Agent** (`pos-minimal/sidecar/node_agent.py`):
- Runs as a background process on each Minimal POS instance
- Reports every N seconds (configurable via `--interval`)
- Includes: node_id, status, product_count, recent_products, last_transactions
- Sends individual transactions via `POST /api/nodes/<id>/transactions`

### 2. Data Aggregation (Solo Server)

```
Solo Server                     Cloud Master
    │                                │
    │  POST /api/webhooks/           │
    │       node-aggregate           │
    │  {source, nodes: [...]}        │
    ├──────────────────────────────▶│  Stores in cloud_data/
    │                                │  webhooks/node_aggregate.jsonl
    │  {"webhook_id":"...",          │
    │   "status":"received"}         │
    │◀──────────────────────────────│
```

**Node Scanner** (`pos-solo/sidecar/node_scanner.py`):
- Maintains a registry (`node_registry.json`) of all known Minimal nodes
- Tracks last_seen, product_count, last_transactions per node
- Removes stale nodes (>24h inactivity)
- Forwards aggregated data to Cloud Master via webhook

**Webhook Sender** (`pos-solo/sidecar/webhook_sender.py`):
- Sends typed webhooks to the Cloud Master
- Event types: `node_aggregate`, `transaction_batch`, `product_update`, `settings_sync`, `heartbeat`
- Each webhook includes: version, source_id, event_type, timestamp, data

### 3. Master Reception (Cloud Full)

```
Cloud Master
    │
    │  POST /api/webhooks/*  ──▶  webhook_receiver.py
    │                                │
    │                           stores in cloud_data/webhooks/*.jsonl
    │                                │
    │                           returns {webhook_id, status, timestamp}
```

**Webhook Receiver** (`pos-full/cloud/webhook_receiver.py`):
- Accepts all webhook types on `/api/webhooks/*`
- Stores each event as a JSONL record
- Maintains stats for monitoring
- Returns `202 Accepted` with unique webhook_id

### 4. Cloud CRM Sync (Solo → Cloud)

```
Solo Server                     Cloud Master
    │                                │
    │  POST /api/sync/push/products  │
    │  POST /api/sync/push/sales     │  sync_proxy.py
    │  POST /api/sync/push/customers │  stores in cloud_data/sync_proxy/
    ├──────────────────────────────▶│
    │                                │
    │  GET /api/sync/status          │
    │◀──────────────────────────────│
```

**Sync Client** (`pos-solo/sidecar/sync_client.py`):
- Typed HTTP client for pushing POS entities
- Methods: `push_product()`, `push_sale()`, `push_customer()`, `push_inventory()`, `push_employee()`, `push_settings()`
- Bulk operations: `bulk_push()`

**Sync Proxy** (`pos-full/cloud/sync_proxy.py`):
- Generic receiver for POS entity pushes
- Stores in `cloud_data/sync_proxy/<type>.json`
- Maintains a sync log (last 1000 entries)

## Configuration

### Minimal Node Agent

```bash
# Command-line args
python3 node_agent.py \
  --master http://solo-host:8765 \
  --node-id POS-NODE-001 \
  --db ./restaurant.db \
  --interval 60 \
  --once           # Single heartbeat, then exit
  --verbose        # Debug logging
```

### Solo Server (existing)

```bash
# Environment variables
SIDECAR_HOST=127.0.0.1
SIDECAR_PORT=8765
DATABASE_URL=restaurant.db
CLOUD_CRM_URL=http://localhost:8766
CLOUD_CRM_API_KEY=
```

### Cloud Master (existing)

```bash
# Environment variables
CLOUD_HOST=127.0.0.1
CLOUD_PORT=8766
CLOUD_DATA_DIR=./cloud_data
CLOUD_API_KEY=
```

## File Reference

### pos-minimal/sidecar/

| File | Purpose |
|------|---------|
| `node_agent.py` | Lightweight sync agent with unique node_id; sends heartbeats + transactions to Solo |

### pos-solo/sidecar/

| File | Purpose |
|------|---------|
| `server.py` | Sanic app — REST + WebSocket + Node scanner routes + Sync blueprint |
| `node_scanner.py` | Discovers & tracks Minimal nodes; maintains registry; forwards to Master |
| `webhook_sender.py` | Sends typed webhooks to Cloud Master |
| `sync_client.py` | HTTP client for pushing POS entities to Cloud |
| `sync_routes.py` | Sync API blueprint (status, config, trigger, push) |

### pos-full/cloud/

| File | Purpose |
|------|---------|
| `server.py` | Sanic app — CRM API + Sync Proxy + Webhook Receiver |
| `crm_api.py` | CRM entity CRUD (contacts, companies, deals, etc.) |
| `crm_models.py` | Django models for CRM entities |
| `sync_proxy.py` | Generic receiver for POS entity pushes from Solo |
| `webhook_receiver.py` | Webhook receiver — accepts aggregated data from Solo |
| `sync_client.py` | HTTP client for sidecar ↔ cloud communication |
| `sync_models.py` | Django models for sync tracking |

## Webhook Plan

The webhook system uses three tiers of webhook communication:

### Tier 1: Minimal → Solo (HTTP POST)
```
Endpoint:  POST /api/nodes/<node_id>/heartbeat
Payload:   {node_id, status, product_count, recent_products, last_transactions}
Frequency: Every 60 seconds (configurable)
```
- Minimal nodes send heartbeats to the Solo server
- Solo maintains a registry of all known nodes

### Tier 2: Solo → Cloud Master (Webhook)
```
Endpoint:  POST /api/webhooks/node-aggregate
Endpoint:  POST /api/webhooks/transaction-batch
Endpoint:  POST /api/webhooks/product-update
Frequency: On data change or every 5 minutes
```
- Solo aggregates data from multiple Minimal nodes
- Forwards to Cloud Master via typed webhooks
- Each webhook includes source_id, event_type, timestamp

### Tier 3: Master Processing (Cloud)
```
Endpoint:  POST /api/webhooks/* (receiver)
Processing: Store in JSONL → optional forward to Django → trigger sync
```
- Cloud Master accepts all webhooks
- Stores raw events in `cloud_data/webhooks/`
- Django models available for relational storage
- Sync proxy handles entity-specific data

## Related Documentation

| Resource | Path |
|----------|------|
| This document | [`docs/pos/network-architecture.md`](network-architecture.md) |
| POS site docs | [`docs/sites/pos.md`](../editions.md) |
| Cloud CRM docs | [`projects/pos/pos-full/cloud/README.md`](https://github.com/mammhoud/structa.cloud/tree/generic/projects/pos/pos-full/cloud) |
| Solo sidecar docs | [`projects/pos/pos-solo/sidecar/README.md`](https://github.com/mammhoud/structa.cloud/tree/generic/projects/pos/pos-solo/sidecar) |
| Minimal node agent | [`projects/pos/pos-minimal/sidecar/node_agent.py`](https://github.com/mammhoud/structa.cloud/blob/generic/projects/pos/pos-minimal/sidecar/node_agent.py) |
| Root Makefile | [`projects/pos/Makefile`](../../projects/pos/Makefile) |
