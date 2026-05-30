# Deployment Guide

This guide summarizes the stable Docker deployment path. For the full step-by-step flow, see [Docker Deployment Flow](deployment_flow.md).

## Architecture overview

The stack is split into independently composable layers:

| Layer | Compose file | Services |
|---|---|---|
| Warehouse | `compose/docker-compose.warehouse.yml` | PostgreSQL, Redis, optional Celery worker/beat definitions |
| Application | `compose/docker-compose.yml` | Django ASGI application container |
| Shared tasks | `compose/docker-compose.tasks.yml` | Shared Celery worker and beat |
| Edge proxy | `compose/docker-compose.traefik.yml` | Traefik with TLS termination |
| Static/media proxy | `compose/docker-compose.nginx.yml` | Optional Nginx layer |
| Docs | `compose/docker-compose.docs.yml` | Documentation service |

## Required environment

Create a root `.env` and keep these values aligned:

```env
PROJECT_PATH=lms-demo
DJANGO_SITE=lms-demo
DJANGO_SETTINGS_MODULE=settings
SERVER_ENV=production
DEBUG=False
DB_TYPE=postgres
DB_HOST=vresume-postgres
DB_NAME=vresume
DB_USER=vresume
DB_PASSWORD=change-me
REDIS_PASSWORD=change-me-too
REDIS_URL=redis://:change-me-too@vresume-redis:6379/0
CELERY_BROKER_URL=redis://:change-me-too@vresume-redis:6379/1
DJANGO_HOST=structa.cloud
ACME_EMAIL=admin@structa.cloud
```

Use `PROJECT_PATH=ctc-research` and `DJANGO_SITE=ctc-research` when deploying the CTC Research site.

## Production deployment

```bash
docker network create traefik-net || true
docker compose -f compose/docker-compose.warehouse.yml up -d vresume-postgres vresume-redis
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.yml up -d --build vresume-website
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.tasks.yml up -d shared-tasks-worker shared-tasks-beat
docker compose -f compose/docker-compose.traefik.yml up -d
```

## Verification gates

Run these before routing production traffic:

```bash
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.yml config
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.yml exec vresume-website python manage.py --site "$PROJECT_PATH" check
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.yml exec vresume-website python manage.py --site "$PROJECT_PATH" migrate --noinput
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.yml exec vresume-website python manage.py --site "$PROJECT_PATH" collectstatic --noinput
docker compose -f compose/docker-compose.warehouse.yml -f compose/docker-compose.yml exec vresume-website python scripts/verify_runtime.py --site "$PROJECT_PATH" --strict-assets --strict-pages
curl -fL -H 'X-Forwarded-Proto: https' http://localhost:5072/health/
```

## Operational notes

- Use `SERVER_TYPE=gunicorn` for production.
- Use `RUN_SETUP=true` only when you intentionally want the entrypoint to run setup tasks at container start.
- Use the shared task stack only when background jobs are needed.
- Rotate default database and Redis passwords before deployment.
- Keep the Traefik ACME CA server on staging until DNS and routing are confirmed, then switch to the production Let's Encrypt endpoint.
