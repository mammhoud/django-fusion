# POS Full

> Complete enterprise POS — sidecar + Django ORM + WebSocket chat + data sync.

This is the **full edition** of POS. Everything included: React frontend,
Tauri/Rust backend, Python/Sanic sidecar, Django ORM models, WebSocket chat,
cross-device data sync, JSON fixtures, and complete documentation.

## What's Included

Everything from extended, plus:

- **Django ORM models** (`sidecar/posapp/models.py`) — 30 models mirroring the Rust schema
- **JSON seed fixtures** (`sidecar/posapp/fixtures/seed_data.json`)
- **WebSocket real-time chat** with message history
- **Data sync API** for multi-device synchronization
- **Support ticket system** via sidecar
- **Complete documentation** including server API, backend env, and data flow

## Quick Start

```bash
pnpm install && cd src-tauri && cargo fetch && cd ..
cd sidecar && pip install -r requirements.txt && cd ..

# Terminal 1: Start full sidecar (Django + WebSocket)
python3 sidecar/server.py

# Terminal 2: Start frontend
pnpm dev
```

## Sidecar API

The sidecar runs on `http://127.0.0.1:8765` by default with Django ORM backing.

```bash
# Health check
curl http://127.0.0.1:8765/api/health

# Full data sync
curl http://127.0.0.1:8765/api/data/sales

# WebSocket chat with persistence
ws://127.0.0.1:8765/ws/chat

# Django admin (if configured)
# http://127.0.0.1:8765/admin/
```

Full API reference: [`docs/server/README.md`](docs/server/README.md)
Backend setup: [`docs/back-env/README.md`](docs/back-env/README.md)

## Database

```bash
# Rust/SQLite seed (29 tables)
cargo run --manifest-path src-tauri/Cargo.toml --bin seed

# Django fixtures (30 models)
cd sidecar && python3 -c "
import django; import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posapp.apps')
django.setup()
from django.core.management import call_command
call_command('loaddata', 'posapp/fixtures/seed_data.json')
"
```

## Directory Structure

```
pos-full/
├── src/                    # React 19 + TypeScript + Tailwind
│   ├── api/                # Full API: sidecar, chat, data, tickets
│   ├── pages/              # 22 pages including Invoice, SupportChat
│   └── utils/              # invoicePdf.ts, data utilities
├── src-tauri/              # Tauri/Rust backend
│   ├── src/operations/     # 25 CRUD modules including sidecar.rs
│   └── templates/          # invoice.html, support_email.html
├── sidecar/
│   ├── server.py           # Sanic REST + WebSocket (35+ endpoints)
│   └── posapp/
│       ├── models.py       # 30 Django ORM models (mirrors Rust schema)
│       ├── apps.py         # Django app config
│       └── fixtures/
│           └── seed_data.json  # Matching seed data
├── scripts/dev/            # 12 build/dev utilities
└── docs/                   # Full documentation (17 files)
```

## Build

```bash
pnpm build:desktop     # Production desktop app
pnpm build:sidecar     # Build sidecar binary (PyInstaller)
pnpm build:all         # Build all platforms
```

## Environment

```bash
SUPERUSER_EMAIL=admin@pos.local
SUPERUSER_PASSWORD=changeme
SUPERUSER_NAME=Admin
DATABASE_URL=restaurant.db
SIDECAR_HOST=127.0.0.1
SIDECAR_PORT=8765
DJANGO_SETTINGS_MODULE=posapp.apps
```
