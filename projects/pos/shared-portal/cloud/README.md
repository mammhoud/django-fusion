# ☁️ Cloud CRM Server (`cloud/`)

## What's Here

Standalone Sanic HTTP server providing cloud-synced Customer Relationship Management for the POS Full Edition. Runs alongside the POS sidecar on a separate port (default **8766**).

```
cloud/
├── server.py          # 🔴 Standalone Sanic server (auth, CORS, health)
├── crm_api.py         # 🟢 Enhanced CRM REST API (20+ endpoints)
├── crm_models.py      # 🔵 Django models (Company, Contact, Pipeline, Stage, Deal, Activity, Note)
├── sync_models.py     # 🟡 Cloud sync models (SyncLog, SyncQueue, CloudConfig)
├── sync_client.py     # 🟢 HTTP client for sidecar → cloud communication
├── requirements.txt   # Python dependencies
├── __init__.py
└── README.md
```

## Guide

| Command | Description |
|---------|-------------|
| `python server.py` | Start with defaults (`127.0.0.1:8766`, data in `./cloud_data/`) |
| `python server.py --port 8766 --data-dir ./cloud_data` | Custom port & data dir |
| `python server.py --host 0.0.0.0 --api-key mysecret` | Public + API key auth |
| `python server.py --verbose` | Debug logging |
| `pip install -r requirements.txt` | Install dependencies |

## Code Map

| File | Purpose | Customization |
|------|---------|:------------:|
| `server.py` | Server entry point — middleware (CORS, auth), health, CRM blueprint registration | 🟢 `customizable` |
| `crm_api.py` | CRM REST blueprint — CRUD + search + pagination + export/import + dashboard + sync | 🟢 `customizable` |
| `crm_models.py` | Django model definitions — 7 entities with indexes, properties, meta | 🔵 `template` |
| `sync_models.py` | Sync tracking — SyncLog, SyncQueue, CloudConfig with conflict strategies | 🟡 `delegate` |
| `sync_client.py` | HTTP client — typed methods for push/pull/bulk/sync management | 🟢 `customizable` |

## Remarks

1. **Separate port**: Cloud server runs on port **8766** (sidecar runs on **8765**). Configure via `CLOUD_PORT` env var or `--port` flag.
2. **Optional auth**: Set `CLOUD_API_KEY` env var or `--api-key` to require `X-API-Key` header on all requests except `/` and `/health`.
3. **JSON storage**: Data stored in `CLOUD_DATA_DIR/crm/` as JSON files (same pattern as sidecar). Default: `./cloud_data/crm/`.
4. **Default pipeline**: Auto-created on first run — 6 stages (New Lead → Closed Lost).
5. **Pagination**: All list endpoints support `page` and `per_page` query params (max 200 per page).
6. **Search**: Use `q=` query param for full-text search across names, email, phone, tags.
7. **Export**: `GET /api/crm/export/<type>` returns CSV by default, JSON if `Accept: application/json` header.

## Customization Key

| Tag | Meaning |
|:---:|---------|
| 🟢 `customizable` | Safe to modify freely — no downstream dependencies |
| 🔴 `not-customizable` | Do not change — required by frontend or protocol contracts |
| 🟡 `delegate` | Extend by subclassing or configuration — don't modify core |
| 🔵 `template` | Follow existing patterns exactly — model definitions |

## Related Documentation

- [POS Site Docs →](../../../docs/sites/pos.md)
- [Sidecar Server →](../sidecar/README.md)
- [Rust Backend →](../../../docs/rust/README.md)
- [Server Architecture →](../../../docs/server/README.md)
- [Features Overview →](../../../docs/features/README.md)
