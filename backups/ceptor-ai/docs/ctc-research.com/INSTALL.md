# Alliance — Installation Guide

This guide covers setting up a full local development environment using Docker Compose.

---

## Prerequisites

| Requirement | Minimum Version |
|---|---|
| Docker | 24.x |
| Docker Compose | 2.x (plugin) |
| Git | 2.x |
| `uv` (Python package manager) | 0.4+ |

> **Note:** Python does not need to be installed on the host — everything runs inside containers. `uv` is only required if you plan to run management commands outside Docker.

---

## 1. Clone the Repository

```bash
git clone <your-repo-url> alliancecore
cd allianceprojects/core
```

---

## 2. Configure Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env   # or use the existing .env as a base
```

### Required Variables

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DATABASE_URL=postgres://alliancecore:alliancecore@db:5432/alliancecore
POSTGRES_DB=alliancecore
POSTGRES_USER=alliancecore
POSTGRES_PASSWORD=alliancecore

# Redis
REDIS_URL=redis://redis:6379/0

# Wagtail
WAGTAIL_SITE_NAME=Alliance

# Environment
DJANGO_ENV=local
```

### Optional Variables

```bash
# Email (development — console backend)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Sentry (production only)
SENTRY_DSN=

# AWS S3 Storage (production only)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Temporal (background workflows)
TEMPORAL_ADDRESS=temporal:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=alliancecore-tasks

# Stripe (payments)
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
```

---

## 3. Set Up `django-fusion` (Source Clone)

Alliance uses `django-fusion` installed from a local source clone as configured in `pyproject.toml`:

```toml
[tool.uv.sources]
django-fusion = { path = "/libs/django-fusion", editable = true }
```

Clone `django-fusion` into the expected path:

```bash
# On your host machine (mounted into containers)
sudo mkdir -p /libs
cd /libs
git clone https://github.com/<org>/django-fusion.git
```

> If you prefer a different path, update the `path` in `pyproject.toml` and the matching Docker volume mount in `compose/`.

---

## 4. Build and Start Services

```bash
# Build all images
docker compose build

# Start all services in the background
docker compose up -d
```

### Service Overview

| Service | Purpose | Port |
|---|---|---|
| `web` | Django (Gunicorn/Uvicorn) | 8000 |
| `db` | PostgreSQL | 5432 |
| `redis` | Cache + message broker | 6379 |
| `nginx` | Static files + reverse proxy | 80 |
| `worker` | Django RQ worker | — |
| `temporal` | Temporal server | 7233 |
| `temporal-ui` | Temporal web UI | 8080 |
| `temporal-worker` | Temporal activity worker | — |

---

## 5. First-Run Setup

### Apply Migrations

```bash
docker compose exec web python com migrate
```

### Load Initial Data (Optional)

```bash
docker compose exec web python com loaddata dump-data.json
```

### Create Superuser

```bash
docker compose exec web python com createsuperuser
```

### Compile Translations

```bash
docker compose exec web django-admin compilemessages
```

### Build Frontend Assets

```bash
# Run inside the container (or locally if Node.js is installed)
docker compose exec web npm install
docker compose exec web npm run build
```

---

## 6. Access the Application

| Interface | URL |
|---|---|
| Main site | http://localhost |
| Django admin | http://localhost/admin |
| Wagtail admin | http://localhost/cms |
| API (Ninja) | http://localhost/api/docs |
| Temporal UI | http://localhost:8080 |
| Django Debug Toolbar | Available in development |

---

## 7. Development Workflow

### Run the Development Server (without Docker)

```bash
# Install dependencies via uv
uv sync

# Start Django
python com runserver
```

### Frontend Hot Reload

```bash
npm run dev
# Webpack dev server at http://localhost:3000, proxies to Django at :8000
```

### Run Temporal Worker

```bash
python com run_temporal_worker
```

### Run Tests

```bash
# Inside Docker
docker compose exec web pytest

# Locally
uv run pytest
```

---

## 8. Common Commands Reference

```bash
# Shorthand manage.py wrapper
python com <command>

# Examples
python com migrate
python com shell
python com shell_plus          # django-extensions
python com makemigrations
python com collectstatic
python com createsuperuser
python com run_temporal_worker
python com sync_alliancecore   # Alliance sync command
```

---

## 9. Stopping and Cleanup

```bash
# Stop services
docker compose down

# Stop and remove volumes (wipes database)
docker compose down -v

# Remove all built images
docker compose down --rmi all
```

---

## Troubleshooting

### `django-fusion` not found
Ensure `/libs/django-fusion` exists and is accessible inside the container via the volume mount. Check `compose/` service definitions for the bind mount declaration.

### Database connection refused
Verify `DATABASE_URL` matches the `db` service credentials in `.env`. Services sometimes need a few seconds to be ready; retry after `docker compose up -d`.

### Static files not loading
Run `python com collectstatic --noinput` then reload Nginx: `docker compose restart nginx`.

### Migrations failing
If you get integrity errors on a fresh install, try `docker compose down -v` to wipe the volume and start fresh.

---

## Further Reading

- [Product Overview](./PRODUCT.md)
- [Settings Reference](./config/settings.md)
- [MCP Integration](./integrations/mcp.md)
- [Temporal Workflows](./architecture/temporal-workflows.md)
