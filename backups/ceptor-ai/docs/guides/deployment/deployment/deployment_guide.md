# Deployment Guide

Complete guide for deploying the structa.cloud monorepo to production.

## Prerequisites

- Docker Engine 24+
- Docker Compose plugin v2.20+
- Domain DNS pointing to server
- `.env` file populated from `.env.example`

## Quick Deploy

```bash
# 1. Clone and enter repo
git clone <repo-url>
cd structa.cloud

# 2. Set up environment
cp .env.example .env
# Edit .env with production values

# 3. Validate root compose configuration
docker compose -f docker-compose.yml config

# 4. Start all services from the repository root
make compose-up

# 5. Run migrations
docker compose -f docker-compose.yml exec ctc-research python manage.py migrate
docker compose -f docker-compose.yml exec lms-demo python manage.py migrate

# 6. Collect static files
docker compose -f docker-compose.yml exec ctc-research python manage.py collectstatic --noinput
docker compose -f docker-compose.yml exec lms-demo python manage.py collectstatic --noinput
```

## Service Architecture

```
traefik          → Reverse proxy (ports 80/443)
├── ctc-research → Django/Wagtail site (ctc-research.com)
├── lms-demo     → Django/Wagtail site (structa.cloud)
├── vresume      → Django/Wagtail portfolio (vresume.structa.cloud)
└── docs         → Docsify docs site (docs.structa.cloud)

common (internal)
├── postgres     → PostgreSQL database
└── redis        → Redis broker/cache

shared-tasks-worker → Celery shared task worker
shared-tasks-beat   → Celery beat scheduler
```

## Docker Compose Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Main orchestrator — includes all others |
| `compose/docker-compose.traefik.yml` | Traefik reverse proxy |
| `compose/docker-compose.warehouse.yml` | PostgreSQL + Redis |
| `compose/docker-compose.applications.yml` | All Django websites |
| `compose/docker-compose.tasks.yml` | Celery workers |
| `compose/docker-compose.docs.yml` | Docsify docs server |
| `docker-compose.infra.yml` | Infrastructure overlay |

## Environment Variables

Key variables required in `.env`:

```bash
# Database
POSTGRES_DB=structa
POSTGRES_USER=structa
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql://structa:<password>@postgres:5432/structa

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1

# Django
SECRET_KEY=<50-char-random-string>
ALLOWED_HOSTS=ctc-research.com,structa.cloud,docs.structa.cloud
DEBUG=False

# Email (for crafts-ai)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<app-password>

# Traefik SSL
ACME_EMAIL=admin@structa.cloud
```

## SSL Certificates

Traefik auto-provisions Let's Encrypt certificates when:

1. `ACME_EMAIL` is set in `.env`
2. Port 80 is accessible from the internet (for HTTP-01 challenge)
3. DNS A records point to server IP

## Logs

```bash
# All services
docker compose -f docker-compose.yml logs -f

# Specific service
docker compose -f docker-compose.yml logs -f ctc-research
docker compose -f docker-compose.yml logs -f docs

# Traefik access log
docker compose -f docker-compose.yml logs -f traefik
```

## Health Checks

```bash
# Check all container health
docker compose ps

# Manual health check
curl -sf http://localhost/ -H "Host: structa.cloud"
curl -sf http://localhost/ -H "Host: docs.structa.cloud"
```

## Rolling Updates

```bash
# Rebuild and restart a single service
docker compose up -d --build --no-deps ctc-research

# Restart without rebuild
docker compose restart lms-demo
```

## Backup

```bash
# Database backup
docker compose exec postgres pg_dump -U structa structa > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T postgres psql -U structa structa < backup_20260616.sql
```

## Troubleshooting

See [ecosystem/deployment/06-troubleshooting.md](../06-troubleshooting.md) for full troubleshooting guide.

Common issues:
- **502 Bad Gateway**: Application container not healthy — check `docker compose logs <service>`
- **Static files 404**: Run `collectstatic` and check volume mounts
- **Certificate missing**: Ensure port 80 is open and DNS is correct
- **Migration errors**: Check `DATABASE_URL` and run `docker compose exec <site> python manage.py showmigrations`
