# POS — Backend Environment Setup

> **Edition:** Full | **Component:** Django Portal + sidecar

---

## Overview

The Full Edition includes a Django backend (the "portal") that provides:
- **Django Admin** — Manage POS data via web interface
- **django-fusion Viewsets** — CRUD views for menu items, categories
- **Node API** — Heartbeat and registration endpoints for POS nodes
- **Cloud CRM** — CRM master server (port 8766)

The Django portal runs alongside the Sanic sidecar, both reading from the same SQLite database.

---

## Environment Variables

All configuration is loaded from `sidecar/settings.py`, which reads from environment variables and `.env` files.

### Required Variables

```bash
# Django settings
DJANGO_SETTINGS_MODULE=settings
DJANGO_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=restaurant.db
```

### Recommended Variables

```bash
# Debug mode (disable in production!)
DJANGO_DEBUG=True

# Allowed hosts
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Portal site name
WEBSITE=full-portal
```

### Optional Variables

```bash
# Superuser auto-creation (for first setup)
DJANGO_SUPERUSER_EMAIL=admin@pos.local
DJANGO_SUPERUSER_PASSWORD=changeme
DJANGO_SUPERUSER_USERNAME=admin

# Cloud CRM URL (for sync)
CLOUD_CRM_URL=http://localhost:8766
CLOUD_CRM_API_KEY=your-api-key

# Sync settings
SYNC_ENABLED=true
SYNC_INTERVAL=60           # Seconds between sync cycles
SYNC_RETRY_MAX=3           # Max retry attempts
SYNC_RETRY_DELAY=10        # Seconds between retries
```

---

## Django Settings (`sidecar/settings.py`)

Key settings sections:

```python
# Database — uses the same SQLite as the Rust backend
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DATABASE_URL', 'restaurant.db'),
    }
}

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shared',        # Shared models, viewsets, templates
    'portal',        # Portal views
    'posapp',        # POS Django models (mirror)
]

# django-fusion viewsets (from shared/)
# MenuItem, Category CRUD via portal_viewsets.py
```

---

## Database Setup

### First Run

```bash
cd sidecar

# Install dependencies
pip install -r requirements.txt

# Run migrations (creates Django tables in SQLite)
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Seed menu data
python3 manage.py seed_menu
```

### Django Tables

The Django side adds these tables to the shared SQLite database:

| Table | Purpose |
|-------|---------|
| `auth_user` | Django admin users |
| `shared_menuitem` | Menu items (managed via portal) |
| `shared_category` | Menu categories |
| `posapp_product` | POS product mirror (Full only) |
| `posapp_sale` | POS sale mirror (Full only) |

**Important:** Django tables coexist with the Rust schema tables. Both read/write the same `restaurant.db` file.

---

## Running the Portal

### Development

```bash
# Terminal 1: Sanic sidecar (API)
python3 sidecar/server.py --db ../restaurant.db --port 8765 &

# Terminal 2: Django portal (admin)
cd sidecar
python3 manage.py runserver 0.0.0.0:8080
```

### Access Points

| URL | Service |
|-----|---------|
| `http://localhost:8080/admin/` | Django Admin |
| `http://localhost:8080/portal/` | Portal dashboard |
| `http://localhost:8080/portal/menu/` | Menu management |
| `http://localhost:8765/health` | Sidecar health check |

---

## Cloud CRM Setup (Full Edition)

### Start the Cloud CRM Server

Run from `pos-full/`:

```bash
cd cloud
pip install -r requirements.txt
python3 server.py --port 8766
```

### Configure Sync

Set in `.env`:
```bash
CLOUD_CRM_URL=http://localhost:8766
CLOUD_CRM_API_KEY=your-api-key
SYNC_ENABLED=true
```

The sync client (`sync_client.py`) will push:
- Products → Cloud CRM
- Sales → Cloud CRM
- Customers → Cloud CRM contacts

---

## PyInstaller Build

The sidecar is bundled as a standalone binary for distribution:

```bash
# Build for current platform
make build-sidecar

# Build for specific target
make build-sidecar-x86_64-unknown-linux-gnu
```

The build uses `sidecar/build.py` (PyInstaller) which packages:
- Sanic server
- Django portal
- All Python dependencies
- Templates and static files

---

## Related Docs

- [`README.md`](../../sidecar/README.md) — Sidecar overview
- [`ARCHITECTURE.md`](../../sidecar/ARCHITECTURE.md) — Sidecar architecture
- [`server/README.md`](../server/README.md) — API reference
- [Django Documentation](https://docs.djangoproject.com/)
