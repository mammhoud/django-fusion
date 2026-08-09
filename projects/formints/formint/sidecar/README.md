# 📁 Formint POS Sidecar (`sidecar/`)

## What's Here

**Full Django** backend for the Formint POS desktop app. Django owns domain
rules, persistence, permissions, audit, Channels WebSocket streams, and the
`django-fusion` fragment/dual-mode render contract. The former **Robyn**
server (`server.py`, `routes/`, Robyn middleware, Jinja2 `templates/`) was
**removed** — the same surface is now served by Django (daphne / runserver)
plus **django-bolt** (`manage.py runbolt`) for the high-performance `/bolt/*`
API.

```
sidecar/
├── configs/                  # Django settings (configs/__init__.py), URLs, dashboard, wsgi
├── asgi.py                   # 🟢 ASGI entry — HTTP (Django) + WebSocket (Channels)
├── manage.py                 # 🟢 Django management CLI (migrate, runserver, --ensure-superuser)
├── manage_bolt.py            # django-bolt management bridge (ensure_default_api_key)
├── bolt_api.py               # 🟢 BoltAPI core REST endpoints — served natively by runbolt
├── consumers.py              # Channels WebSocket consumers (ws/nodes, ws/entities, ws/config)
├── views_django.py           # Django-native REST surface (replaces Robyn routes)
├── htmx_views.py             # HTMX fragment endpoints (django-fusion)
├── fusion_views.py           # /fusion/* contract endpoints
├── api_keys_views.py         # API-key management (ensure_default_api_key)
├── ws_client.py              # Cloud WebSocket sync client (persistent, backoff)
├── signals.py                # Django signal definitions (config_changed, …)
├── sync_signals.py           # Signal receivers: flag rows for cloud sync
├── signal_handlers.py        # Signal receivers: audit trail + outbound webhooks
├── ws_sync_signals.py        # Signal receivers: real-time push to cloud WS
├── models/                   # Django ORM models (managed=True, pos_full)
│   ├── node.py               # Node, Heartbeat, NodeEvent
│   ├── config.py             # DeviceConfig, MasterDevice, CloudLink
│   ├── sync.py               # SyncLog
│   ├── audit.py              # SignalEvent
│   └── …                     # pos, extra, inventory, ops, crm, loyalty, token, approval
├── formint/                  # Merged backend app (Ninja API, fusion contract, Unfold admin)
├── services/                 # sync engine (ProductSyncEngine)
├── django_templates/         # Django template tree (Django-only)
├── fragments/                # django-fusion fragment components
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── tests/                    # Pytest suite (225+ tests, green in one pass)
├── Makefile                  # Sidecar commands
├── pyproject.toml            # Python project metadata (formint-pos-sidecar)
└── formint-backend.spec      # PyInstaller spec → formint-backend binary (Tauri)
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  Full Django sidecar                                                │
│                                                                     │
│  make dev / daphne  →  asgi:application (:8767, frontend proxy)     │
│    ├─ HTTP      → Django URLconf (configs/urls.py)                  │
│    │    ├─ /api/v1/*  — Django Ninja (formint app)                  │
│    │    ├─ /fusion/*  — django-fusion render-mode contract          │
│    │    ├─ /htmx/*    — HTMX fragment endpoints                     │
│    │    ├─ /nodes, /stats, /sync/status … — Django-native surface   │
│    │    └─ /admin/    — Unfold-themed admin                         │
│    └─ WebSocket → Channels ProtocolTypeRouter → consumers.py        │
│         /ws/nodes · /ws/entities · /ws/config                       │
│                                                                     │
│  make server       →  manage.py runbolt (:8766)                     │
│    └─ /bolt/*      — django-bolt Rust-backed API (BOLT_API)         │
│                                                                     │
│  Django ORM (restaurant.db) — full_ / pos_crm_ / pos_sync_ tables   │
└──────────────────────────────────────────────────────────────────────┘

                         │ Channels WebSockets
                         ▼
  /ws/nodes    — Node event stream (register, heartbeat, …)
  /ws/entities — Entity CRUD events (Redux/RTK cache refresh)
  /ws/config   — Config change stream (config, approval, sync)
```

The **cloud sync client** (`ws_client.py`) keeps a persistent WebSocket to the
POS Cloud master, pushes local entity events, and fans cloud events back to
local `/ws/entities` listeners — all pure Django (no Robyn).

## Quick Start

```bash
make install        # .venv + editable package + migrate
make dev            # Django dev server on :8767
make server         # django-bolt runbolt (Django + /bolt/*) on :8766
make test           # Django formint suite + sidecar pytest suite
make check          # Django system checks
```

Or manually:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
python manage.py migrate
python manage.py runserver 127.0.0.1:8767        # Django road
python manage.py runbolt --host 0.0.0.0 --port 8766   # django-bolt road
DJANGO_SETTINGS_MODULE='' python3 -m pytest tests/ -k "not rust_db"
```

## Key Features

| Feature | Description |
|---------|-------------|
| 🔄 **Product Sync** | Master→Child product/config push + Child→Master sales/reports with approval |
| ✅ **Moderated Approvals** | `SyncApproval` model with approve/reject workflow |
| 🔌 **Django Signals** | `config_changed`, `config_synced`, `device_status_changed` → audit + webhooks + cloud push |
| 🌐 **WebSocket Streams** | Channels: `/ws/nodes`, `/ws/entities`, `/ws/config` with filters |
| ⚡ **django-bolt API** | `/bolt/*` served natively by `runbolt` (Rust router, auth, path params) |
| 🔑 **Token Auth** | DeviceToken system with SHA-256 hashing, roles, expiry, capabilities |
| 🧩 **django-fusion** | Fragment components, dual-mode render contract, PageHandler pipeline |

## Package Structure

| Path | Purpose | Tag |
|------|---------|:---:|
| `configs/` + `asgi.py` | Django settings, URLconf, ASGI (HTTP + WS) | 🟢 customizable |
| `bolt_api.py` | django-bolt REST endpoints (runbolt road) | 🟢 customizable |
| `consumers.py` | Channels WebSocket consumers | 🟢 customizable |
| `views_django.py` + `fusion_views.py` | Django-native REST + fusion surface | 🟢 customizable |
| `models/*.py` | Django ORM models (pos_full) | 🔵 template |
| `signals.py` + `*_signals.py` | Signal defs + receivers (sync, webhooks, WS push) | 🟢 customizable |
| `ws_client.py` | Cloud WebSocket sync client | 🔵 template |
| `tests/` | Pytest suite — unified conftest DB bootstrap, green in one pass | 🟢 customizable |

## Related Docs

- [Architecture](../../docs/FORMINT_ARCHITECTURE.md)
- [POS Editions Overview](../README.md)
- [editions.md — Pro row](../../docs/architecture/editions.md)
