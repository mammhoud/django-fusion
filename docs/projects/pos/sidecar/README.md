# 🖥️ Sidecar — Server Architecture

> The POS sidecar is a Python server that extends the Rust/Tauri desktop app with REST APIs, WebSocket, Django ORM, and cloud sync capabilities.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Tauri Desktop App                  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Vue 3 Frontend (TypeScript)                  │  │
│  └───────────────────┬───────────────────────────┘  │
│                      │ invoke()                      │
│  ┌───────────────────▼───────────────────────────┐  │
│  │  Rust Backend (Diesel ORM + SQLite)           │  │
│  │  • 25 CRUD modules                            │  │
│  │  • Auth, products, orders, inventory          │  │
│  └───────────────────┬───────────────────────────┘  │
│                      │ sidecar spawn                 │
└──────────────────────┼──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│               Python Sidecar Server                  │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Sanic HTTP Server (:8765)                   │    │
│  │  • 35+ REST endpoints                        │    │
│  │  • WebSocket real-time                       │    │
│  │  • Invoice PDF generation                    │    │
│  │  • Email sending                             │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Django ORM (posapp/models.py)               │    │
│  │  • 30 mirror models (Full edition)           │    │
│  │  • Django Admin for data management          │    │
│  │  • Fixtures for seed data                    │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Cloud Sync (Solo edition)                   │    │
│  │  • sync_client.py → Cloud CRM                │    │
│  │  • sync_routes.py → sync API                 │    │
│  │  • webhook_sender.py → push events           │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Cloud Integration (Full edition)            │    │
│  │  • cloud/api.py → CRM REST API               │    │
│  │  • cloud/sync_proxy.py → accept Solo pushes  │    │
│  │  • cloud/webhook_receiver.py → events        │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Shared Portal (all editions)                │    │
│  │  • shared/portal_viewsets.py → Django views  │    │
│  │  • shared/portal_urls.py → URL routing       │    │
│  │  • portal/admin.py → Django Admin            │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

---

## Sidecar by Edition

| Edition | Sidecar | Port | Key Features |
|---------|---------|------|-------------|
| **Minimal** | None | — | No Python sidecar — pure Rust backend |
| **Solo** | `pos-solo/sidecar/` | 8765 | Sanic REST API + Cloud CRM sync client |
| **Full** | `pos-full/sidecar/` | 8765 | Sanic REST + Django ORM + WebSocket + Cloud CRM proxy |

---

## Sidecar Files

| File | Edition | Purpose |
|------|---------|---------|
| `server.py` | Solo, Full | Sanic HTTP + WebSocket server (entry point) |
| `settings.py` | Solo, Full | Django settings for ORM |
| `urls.py` | Solo, Full | URL routing |
| `manage.py` | Solo, Full | Django management commands |
| `build.py` | Solo, Full | PyInstaller build script |
| `posapp/models.py` | Solo, Full | Django ORM mirror models |
| `sync_client.py` | Solo | Push POS data to Cloud CRM |
| `sync_routes.py` | Solo | Sync API blueprint |
| `webhook_sender.py` | Solo | Outgoing webhooks |
| `cloud/api.py` | Full | Cloud CRM REST API |
| `cloud/sync_proxy.py` | Full | Accepts pushes from Solo editions |
| `cloud/webhook_receiver.py` | Full | Incoming webhook handler |
| `portal/admin.py` | All | Django Admin registration |
| `shared/portal_viewsets.py` | All | Shared Django REST viewsets |
| `shared/node_base.py` | All | Base node sync models |

---

## How the Sidecar Starts

The Rust backend auto-spawns the sidecar process:

```rust
// src-tauri/src/sidecar.rs (conceptual)
use tauri::api::process::Command;

pub fn start_sidecar(db_path: &str) {
    Command::new_sidecar("pos-sidecar")
        .expect("failed to create sidecar command")
        .args(["--db", db_path, "--port", "8765"])
        .spawn()
        .expect("failed to spawn sidecar");
}
```

No manual launch needed — the sidecar starts when the desktop app starts.

---

## Sanic Server Specs

| Property | Value |
|----------|-------|
| Framework | Sanic 23+ |
| Port | 8765 (configurable via `--port`) |
| Protocol | HTTP/1.1 + WebSocket |
| CORS | Enabled for localhost |
| Endpoints | 35+ (CRUD for all entities) |
| PDF | Invoice generation via ReportLab |
| Email | SMTP via aiosmtplib |

### API Standard

```python
# Standard response format
{
    "ok": true,
    "data": {...},
    "error": null
}

# Standard error format
{
    "ok": false,
    "data": null,
    "error": "Product not found"
}
```

---

## Django ORM Integration (Full Edition)

The Full edition sidecar includes Django ORM models that mirror the Rust/SQLite schema:

```python
# posapp/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'products'  # Mirror the SQLite table
```

This enables:
- Django Admin for data management
- Django ORM queries for complex reports
- Fixtures for seed data (`posapp/fixtures/seed_data.json`)
- Migration management via Django

---

## Related

| Topic | Path |
|-------|------|
| Sidecar API reference | [`sidecar-api.md`](sidecar-api.md) |
| WebSocket | [`sidecar-websocket.md`](sidecar-websocket.md) |
| Django ORM guide | [`django-orm.md`](django-orm.md) |
| Django Ninja plan | [`django-ninja-plan.md`](django-ninja-plan.md) |
| Network architecture | [`network-architecture.md`](network-architecture.md) |
