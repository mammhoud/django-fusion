# POS — Sidecar API Reference

> **Path:** `sidecar/server.py` | **Framework:** Sanic (Python 3) | **Port:** 8765 | **Edition:** Solo / Full

---

## Overview

The Python/Sanic sidecar server provides a REST + WebSocket API layer on top of the POS SQLite database. It enables:

- **External API access** to POS data (sales, products, inventory)
- **Real-time chat** support via WebSocket
- **Invoice rendering** with multiple templates
- **Support ticket** management
- **Cloud CRM sync** (Solo edition → Cloud master)

---

## Architecture

```
POS Desktop App (Tauri)
    │
    ├── Tauri invoke ──→ Rust backend (SQLite)
    │
    └── HTTP/WS ──────→ Sidecar (Sanic :8765)
                           │
                           ├── Reads SQLite directly
                           ├── Django Portal (port 8080) [Full edition]
                           └── Cloud CRM sync [Solo edition]
```

The sidecar runs as an external binary spawned by Tauri on app startup (`operations/sidecar.rs`).

---

## Base URLs

| Protocol | URL |
|----------|-----|
| **REST** | `http://127.0.0.1:8765` |
| **WebSocket** | `ws://127.0.0.1:8765` |

---

## Health Check

### `GET /health`

Check if the sidecar is running.

**Response (200):**
```json
{
  "status": "ok",
  "timestamp": "2026-07-19T12:00:00Z",
  "service": "pos-sidecar",
  "db_available": true
}
```

---

## Sales

### `GET /api/sales`

List all sales with line items.

**Response (200):**
```json
[
  {
    "id": 1,
    "total_amount": 45.50,
    "currency": "USD",
    "date": "2026-07-19",
    "time": "14:30:00",
    "order_type": "dine_in",
    "status": "completed",
    "table_number": 5,
    "items": [
      {
        "product_name": "Espresso",
        "price": 3.50,
        "quantity": 2,
        "unit": "cup",
        "subtotal": 7.00
      }
    ]
  }
]
```

### `GET /api/sales/{id}`

Get a single sale with items.

**Response (200):** Same as above, single object.

---

## Products

### `GET /api/products`

List all products.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Espresso",
    "price": 3.50,
    "unit": "cup",
    "category_name": "Coffee"
  }
]
```

### `POST /api/products`

Create a new product.

**Request:**
```json
{
  "name": "Latte",
  "price": 4.50,
  "unit": "cup",
  "category_id": 1
}
```

**Response (201):**
```json
{
  "id": 42,
  "name": "Latte",
  "price": 4.50,
  "unit": "cup",
  "category_id": 1
}
```

---

## Settings

### `GET /api/settings`

Get restaurant settings.

**Response (200):**
```json
{
  "restaurant_name": "My Cafe",
  "address": "123 Main St",
  "phone": "+1-555-0123",
  "tax_rate": "8.5",
  "currency": "USD",
  "dine_in_tables": 15,
  "delivery_fee": 5.00,
  "delivery_fee_per_km": 1.50
}
```

---

## Invoice Rendering

### `GET /invoice/render/{sale_id}`

Render a printable invoice HTML page.

**Query Parameters:**

| Param | Values | Default |
|-------|--------|---------|
| `type` | `tax`, `commercial`, `proforma`, `credit`, `receipt` | `commercial` |
| `design` | `modern` (teal), `classic` (blue), `minimal` (dark) | `modern` |

**Example:**
```
http://127.0.0.1:8765/invoice/render/42?type=commercial&design=modern
```

---

## Support Tickets

### `GET /api/support/tickets`

List all support tickets.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Printer issue",
    "message": "Receipt printer not working",
    "status": "open",
    "created_at": "2026-07-19T10:00:00Z"
  }
]
```

### `POST /api/support/ticket`

Create a support ticket.

**Request:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "subject": "Cannot add product",
  "message": "Getting error when adding new product to inventory"
}
```

### `PATCH /api/support/ticket/{id}`

Update ticket status.

**Request:**
```json
{
  "status": "resolved"
}
```

---

## Chat (WebSocket)

### `WS /ws/chat/{room}`

Persistent WebSocket connection for real-time support chat.

**Connect:**
```
ws://127.0.0.1:8765/ws/chat/support
```

**Send message:**
```json
{
  "type": "message",
  "text": "Hello! I need help with the inventory system.",
  "sender": "user"
}
```

**Receive message:**
```json
{
  "type": "message",
  "text": "Sure! What seems to be the issue?",
  "sender": "support",
  "timestamp": "2026-07-19T12:00:00Z"
}
```

### TypeScript Client (`src/api/chat.ts`)

```typescript
import { createChatWs } from '../api';

const conn = createChatWs({
  room: 'support',
  onMessage: (msg) => console.log('Received:', msg),
});

conn.send({ type: 'message', text: 'Hello!', sender: 'user' });
conn.close();
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "Human-readable error message",
  "status": 404
}
```

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request (invalid input) |
| 404 | Resource not found |
| 500 | Internal server error |

---

## Development (Standalone)

```bash
cd sidecar
pip install -r requirements.txt

# Start with default settings
python3 server.py --db ../restaurant.db --port 8765

# Test health endpoint
curl http://127.0.0.1:8765/health

# Test WebSocket chat
wscat -c ws://127.0.0.1:8765/ws/chat/test
```

---

## Related Docs

- [`ARCHITECTURE.md`](../../sidecar/ARCHITECTURE.md) — Sidecar architecture
- [`customization-tauri.md`](../customization-tauri.md) — Sidecar lifecycle management
- [Sanic Documentation](https://sanic.dev/)
