# 🌐 Server — Sidecar (Python/Sanic)

Lightweight Sanic server providing chat, support tickets, customer service, and data APIs for POS.

## Use Cases

### 1. Read-Only Data API (`/api/*`)
- **Purpose:** Expose POS SQLite data (sales, products, settings) via REST endpoints for external dashboards, reporting tools, and frontend data grids
- **Key traits:** Read-only SQLite access via URI `?mode=ro` ensures data integrity; endpoints mirror Rust backend operations for cross-platform access

### 2. Real-Time Chat (`WS /ws/chat/*`)
- **Purpose:** Power the inline chat support widget — customers can message staff via WebSocket for real-time assistance during POS operations
- **Key traits:** Room-based messaging with typing indicators; supports both REST (POST/GET) and WebSocket transports; full chat history stored in JSON files

### 3. Support Ticket Management (`/api/support/*`)
- **Purpose:** Create, update, and track support tickets — enabling customer service workflows without leaving the POS app
- **Key traits:** CRUD operations with status tracking; ticket data persisted in JSON storage (`POS_DATA_DIR`); exposed via typed frontend API (`tickets.ts`)

### 4. Invoice Rendering (`/invoice/render/*`)
- **Purpose:** Generate print-ready A4 invoice HTML for any sale — supporting tax, commercial, proforma, credit, and receipt formats
- **Key traits:** Self-contained HTML output (print-ready); 3 design presets (modern/teal, classic/blue, minimal/dark); `INVOICE_TEMPLATE` and `DESIGN_CONFIGS` are 🟢 customizable

---

## Architecture

```
Tauri Desktop App
├── React/TypeScript ←→ HTTP/WS on 127.0.0.1:8765 → Sanic Sidecar
│                                                      ├── REST API
│                                                      ├── WebSocket chat
│                                                      └── SQLite read-only
└── Rust backend ←→ SQLite (restaurant.db)
```

## Project Structure

```
projects/formints/sidecar/
├── server.py                   # 🔴 Sanic app — all routes + WS handlers
├── requirements.txt            # Python dependencies
├── build.py                    # PyInstaller build script
├── build.sh                    # Build shell wrapper
├── README.md                   # Sidecar documentation
└── posapp/                     # 🔵 Django models (mirrors Rust schema)
    ├── __init__.py
    ├── apps.py                 # Django AppConfig
    └── models.py               # Unmanaged Django models
```

## API Endpoints

### Health
```
GET  /                           # Service info + version
GET  /health                     # Health check (includes db_available)
```

### Chat
```
GET  /chat/<room_id>             # Get chat history
POST /chat/<room_id>             # Post chat message
WS   /ws/chat/<room_id>          # WebSocket real-time chat
WS   /chat/ws/<room_id>          # Legacy WebSocket path
```

### Support Tickets
```
GET    /api/support/tickets         # List all tickets
POST   /api/support/ticket          # Create a ticket
PATCH  /api/support/ticket/<id>     # Update ticket status
```

### Customer Service
```
GET    /customers                   # List customers
POST   /customers                   # Create customer
PATCH  /customers/<id>              # Update customer
```

### Data (read-only SQLite access)
```
GET  /api/sales                     # List all sales with items
GET  /api/sales/<id>                # Get sale by ID with items
GET  /api/products                  # List all products
GET  /api/settings                  # Get app settings
GET  /invoice/render/<id>?type=&design=  # Render printable invoice HTML
```

## Customization Guide

### 🟢 Customizable
| What | How |
|------|-----|
| Invoice HTML template | Edit `INVOICE_TEMPLATE` in `server.py` |
| Invoice designs | Add to `DESIGN_CONFIGS` dict |
| Data storage | Replace JSON files with a real database |
| Add new endpoint | Add route handler in `server.py` |

### 🔴 Not Customizable
| What | Why not |
|------|---------|
| WebSocket protocol | Frontend `ChatSupport.tsx` depends on exact format |
| Ticket schema | Frontend `tickets.ts` API depends on field names |
| Port/host defaults | Must match `SIDECAR_BASE` in frontend |

### ⚪ Config Only
| Setting | Env var | Default |
|---------|---------|---------|
| Host | `POS_SIDECAR_HOST` | `127.0.0.1` |
| Port | `POS_SIDECAR_PORT` | `8765` |
| Data dir | `POS_DATA_DIR` | `./data` |
| DB path | `--db` CLI arg | (none — data API disabled) |

## Solo Extended — Robyn Variant

For the Solo edition, an optional Robyn-based sidecar is available as a drop-in replacement for Sanic. See the [Robyn migration plan](robyn-migration.md) for details.

```bash
# Robyn sidecar (Solo Extended)
pip install robyn[all]
python3 robyn_server.py --db ../restaurant.db --port 8765
```

| Feature | Sanic (default) | Robyn (extended) |
|---------|:---:|:---:|
| Throughput | ~25k RPS | 60k+ RPS |
| OpenAPI | Manual | Built-in |
| Pydantic | Manual | Built-in |
| WebSocket | ✅ | ✅ |
| Hot reload | ✅ | ✅ |
| AI/MCP | ❌ | ✅ |

## Development

```bash
# Run sidecar manually
cd projects/formints/sidecar
pip install -r requirements.txt
python server.py --db ../restaurant.db --port 8765

# Build for bundling
cd projects/formints
make build-sidecar
```

## Invoice Rendering

```
GET /invoice/render/<sale_id>?type=commercial&design=modern
```

| Param | Values | Default |
|-------|--------|---------|
| `type` | `tax`, `commercial`, `proforma`, `credit`, `receipt` | `commercial` |
| `design` | `modern` (teal), `classic` (blue), `minimal` (dark) | `modern` |

Returns self-contained HTML (print-ready A4) with company info, line items, and totals.

## WebSocket Protocol

```json
// Client → Server
{ "type": "message", "text": "Hello!", "sender": "user" }
{ "type": "typing", "sender": "user" }

// Server → Client
{ "id": "uuid", "room_id": "room-1", "user": "support", "content": "Hi!", "timestamp": "..." }
```

---

→ [Back to docs](../README.md)
