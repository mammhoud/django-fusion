# 🌐 Sidecar API Reference

Full API reference for the POS Sanic sidecar server (`projects/formints/sidecar/server.py`).

## Tag Legend

| Tag | Meaning |
|-----|---------|
| 🟢 `customizable` | Safe to modify/extend |
| 🔴 `not-customizable` | Core contract — change breaks frontend |
| ⚪ `config-only` | Configure via env vars/CLI only |

---

## Base URL

```
http://127.0.0.1:8765          # 🔴 Default (matches frontend SIDECAR_BASE)
```

| Setting | Env var | Default |
|---------|---------|---------|
| Host | `POS_SIDECAR_HOST` ⚪ | `127.0.0.1` |
| Port | `POS_SIDECAR_PORT` ⚪ | `8765` |

---

## Common Response Format

All endpoints return JSON with:

```json
{
  "ok": true,           // boolean — success
  "data": {...},        // payload (on success)
  "error": "message"    // error string (on failure)
}
```

HTTP status codes:
- `200` — Success
- `400` — Bad request (validation error)
- `404` — Not found
- `500` — Server error

---

## Health & Meta

### `GET /` 🔴

Service info.

**Response:**
```json
{
  "service": "POS Sidecar",
  "version": "1.0.0",
  "endpoints": ["/health", "/chat", "/api/support", "/api/sales", "/api/products"]
}
```

### `GET /health` 🔴

Health check. Used by Tauri frontend via `sidecar.healthCheck()`.

**Response:**
```json
{
  "status": "ok",
  "db_available": true,
  "uptime": 1234.5
}
```

---

## Chat API

### `GET /chat/<room_id>` 🟢

Get chat history for a room.

**Parameters:**
| Param | Type | Required | Default |
|-------|------|----------|---------|
| `room_id` | string | ✅ (path) | — |
| `limit` | int | ❌ (query) | 50 |

**Response:**
```json
{
  "ok": true,
  "data": {
    "room_id": "support",
    "messages": [
      {
        "id": "uuid",
        "room_id": "support",
        "user": "Admin",
        "content": "Hello, how can I help?",
        "timestamp": "2026-07-18T12:00:00Z"
      }
    ]
  }
}
```

### `POST /chat/<room_id>` 🟢

Post a message to the chat room. Also broadcasts via WebSocket.

**Request:**
```json
{
  "text": "I need help with...",
  "sender": "user"
}
```

**Response:** `201 Created`
```json
{
  "ok": true,
  "data": {
    "id": "uuid",
    "room_id": "support",
    "user": "user",
    "content": "I need help with...",
    "timestamp": "2026-07-18T12:00:00Z"
  }
}
```

---

## Support Tickets

### `GET /api/support/tickets` 🟢

List all support tickets.

**Query Parameters:**
| Param | Type | Default |
|-------|------|---------|
| `status` | string | (all) |
| `limit` | int | 50 |

**Response:**
```json
{
  "ok": true,
  "data": [
    {
      "id": "uuid",
      "subject": "Invoice not generating",
      "message": "When I click export...",
      "status": "open",
      "created_at": "2026-07-18T12:00:00Z",
      "updated_at": "2026-07-18T12:30:00Z"
    }
  ]
}
```

### `POST /api/support/ticket` 🟢

Create a support ticket.

**Request:**
```json
{
  "subject": "Issue summary",
  "message": "Detailed description"
}
```

At least one of `subject` or `message` is required.

**Response:** `201 Created` with ticket object.

### `PATCH /api/support/ticket/<id>` 🔴

Update ticket status.

**Request:**
```json
{
  "status": "closed"
}
```

Valid statuses: `open`, `in_progress`, `closed`, `resolved`.

---

## Data API (SQLite Read-Only)

These endpoints are only available when sidecar is started with `--db <path>`.

### `GET /api/sales` 🟢

List all sales with line items.

**Response:**
```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "invoice_number": "INV-001",
      "customer_name": "John Doe",
      "total": 150.00,
      "status": "completed",
      "created_at": "2026-07-18T12:00:00Z",
      "items": [
        {
          "product_name": "Burger",
          "quantity": 2,
          "unit_price": 50.00,
          "total": 100.00
        }
      ]
    }
  ]
}
```

### `GET /api/sales/<id>` 🟢

Get a single sale by ID with its line items.

### `GET /api/products` 🟢

List all products.

**Response:**
```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "name": "Cheeseburger",
      "price": 50.00,
      "category": "Food",
      "active": true
    }
  ]
}
```

### `GET /api/settings` 🟢

Get application settings from the database.

**Response:**
```json
{
  "ok": true,
  "data": {
    "store_name": "My Restaurant",
    "currency": "USD",
    "tax_rate": 10.0,
    "language": "en"
  }
}
```

---

## Invoice Rendering

### `GET /invoice/render/<sale_id>` 🟢

Render a printable invoice as HTML.

**Query Parameters:**

| Param | Values | Default |
|-------|--------|---------|
| `type` | `tax`, `commercial`, `proforma`, `credit`, `receipt` 🟢 | `commercial` |
| `design` | `modern`, `classic`, `minimal` 🟢 | `modern` |

**Design presets:**

| Design | Accent Color | Style |
|--------|-------------|-------|
| `modern` | Teal (#0d9488) | Clean, rounded |
| `classic` | Blue (#2563eb) | Traditional, borders |
| `minimal` | Dark (#1e293b) | Compact, monochrome |

**Response:** `text/html` — complete, self-contained HTML document (print-ready A4).

### Customizing Invoice Designs 🟢

Edit `DESIGN_CONFIGS` dict in `projects/formints/sidecar/server.py`:

```python
DESIGN_CONFIGS = {
    "custom": {
        "accent_color": "#your-color",
        "css_extra": ".custom-class { ... }",
        "font_family": "Your Font, sans-serif",
    }
}
```

Then use: `GET /invoice/render/1?design=custom`

### Customizing Invoice Template 🟢

Edit `INVOICE_TEMPLATE` string in `server.py`. Uses Python `.format()` syntax:

| Placeholder | Description |
|-------------|-------------|
| `{invoice_type}` | Invoice type label (upper) |
| `{accent_color}` | Design accent color |
| `{company_name}` | From settings or default |
| `{invoice_number}` | Sale invoice number |
| `{customer_name}` | Sale customer name |
| `{date}` | Formatted date |
| `{items_html}` | `<tr>` rows for each line item |
| `{subtotal}` | Pre-tax total |
| `{tax_amount}` | Tax amount |
| `{total}` | Grand total |

---

## Customer Service

### `GET /customers` 🟢

List all customers.

### `POST /customers` 🟢

Create a customer.

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1234567890"
}
```

### `PATCH /customers/<id>` 🟢

Update customer information.

---

## WebSocket

### `WS /ws/chat/<room>` 🔴

Persistent WebSocket for real-time chat.

See [WebSocket Protocol](sidecar-websocket.md) for full details.

---

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| `200 OK` | Success |
| `201 Created` | Resource created |
| `400 Bad Request` | Missing required field, invalid data |
| `404 Not Found` | Resource not found |
| `500 Server Error` | Internal error (check logs) |

---

→ [Server Docs](README.md) | [WebSocket Protocol](sidecar-websocket.md) | [Back to docs](../README.md)
