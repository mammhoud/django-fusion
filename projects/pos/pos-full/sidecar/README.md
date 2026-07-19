# 📁 POS Sidecar Server (`sidecar/`)

## What's Here

Python/Sanic server providing HTTP REST API and WebSocket support for the POS desktop app.

> **CRM moved to `cloud/`**: The CRM module now runs as an independent cloud server
> (see [`cloud/README.md`](../cloud/README.md)). Run it alongside the sidecar for
> full CRM capabilities.

```
sidecar/
├── server.py             # 🔴 Sanic app — all routes + WS
├── requirements.txt      #    Python dependencies
├── build.py              #    PyInstaller build script
├── build.sh              #    Build shell wrapper
└── posapp/               # 🔵 Django models (Rust-mirror tables)
    ├── __init__.py
    ├── apps.py
    ├── models.py          # 29 Rust-managed mirror tables + SupportTicket
    └── fixtures/
        └── seed_data.json
```

## Customization Tags

| Module | Tag | How to customize |
|--------|-----|-----------------|
| `server.py` routes | 🟢 `customizable` | Add new endpoints |
| `server.py` WebSocket | 🔴 `not-customizable` | Protocol must match frontend `chat.ts` |
| `server.py` INVOICE_TEMPLATE | 🟢 `customizable` | Edit HTML template freely |
| `server.py` DESIGN_CONFIGS | 🟢 `customizable` | Add new invoice designs |
| `posapp/models.py` | 🔵 `template` | Mirrors Rust schema — keep in sync |

## Cloud CRM Integration

The CRM system has been extracted into its own standalone cloud server at
[`cloud/`](../cloud/). The sidecar communicates with the cloud server via HTTP
using the `SyncClient`:

```python
from cloud.sync_client import SyncClient

client = SyncClient(base_url="http://localhost:8766")
client.push_contact({"first_name": "John", "last_name": "Doe"})
```

See [`cloud/README.md`](../cloud/README.md) for full CRM API reference.

## Running

```bash
pip install -r requirements.txt
python server.py --db ../restaurant.db --port 8765
```

## Running with Cloud CRM

```bash
# Terminal 1: Cloud CRM server (port 8766)
python ../cloud/server.py --port 8766 --data-dir ../cloud_data

# Terminal 2: Sidecar (port 8765)
python server.py --db ../restaurant.db --port 8765
```

## Reference

- [Sidecar Docs →](../../docs/server/README.md)
- [API Reference →](../../docs/server/api-reference.md)
- [WebSocket Protocol →](../../docs/server/websocket.md)
- [Cloud CRM Docs →](../cloud/README.md)
