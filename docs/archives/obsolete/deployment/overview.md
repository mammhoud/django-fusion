# Deployment Guide

This guide summarizes the stable Docker deployment path. For the full step-by-step flow, see [Docker Deployment Flow](deployment_flow.md).

## Architecture overview

The stack is split into independently composable layers:

| Layer | Compose file | Services |
|---|---|---|
| Warehouse | `applications/databases/docker-compose.yml` | PostgreSQL, Redis, optional Celery worker/beat definitions |
| Application | `applications/compose/docker-compose.applications.yml` | Django ASGI application container |
| Shared tasks | `applications/compose/docker-compose.tasks.yml` | Shared Celery worker and beat |
| Edge proxy | `applications/proxy/docker-compose.traefik.yml` | Traefik with TLS termination |
| Static/media proxy | `applications/proxy/docker-compose.nginx.yml` | Optional Nginx layer |
| Docs | `applications/compose/docker-compose.docs.yml` | Documentation service |

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
docker compose -f docker-compose.yml up -d postgres redis shared-media
docker compose -f docker-compose.yml up -d --build vresume-website
docker compose -f docker-compose.yml up -d shared-tasks-worker shared-tasks-beat
docker compose -f applications/proxy/docker-compose.traefik.yml up -d
```

## Verification gates

Run these before routing production traffic:

```bash
docker compose -f docker-compose.yml config
docker compose -f docker-compose.yml exec vresume-website python manage.py --site "$PROJECT_PATH" check
docker compose -f docker-compose.yml exec vresume-website python manage.py --site "$PROJECT_PATH" migrate --noinput
docker compose -f docker-compose.yml exec vresume-website python manage.py --site "$PROJECT_PATH" collectstatic --noinput
docker compose -f docker-compose.yml exec vresume-website python scripts/verify_runtime.py --site "$PROJECT_PATH" --strict-assets --strict-pages
curl -fL -H 'X-Forwarded-Proto: https' http://localhost:5072/health/
```

## Operational notes

- Use `SERVER_TYPE=gunicorn` for production.
- Use `RUN_SETUP=true` only when you intentionally want the entrypoint to run setup tasks at container start.
- Use the shared task stack only when background jobs are needed.
- Rotate default database and Redis passwords before deployment.
- Keep the Traefik ACME CA server on staging until DNS and routing are confirmed, then switch to the production Let's Encrypt endpoint.

## 2026-05 runtime updates

### Local log mounts

All Django and Celery compose services now mount `compose/logs` to `/app/logs`, so entrypoint logs such as `build_assets.log`, `collectstatic.log`, `load_dumped_data.log`, and `verify_runtime.log` are available from the compose directory on the host.

```bash
mkdir -p logs
docker compose -f docker-compose.yml up -d --build vresume-website
tail -f logs/collectstatic.log
```

### Static collection and runtime setup

`STATIC_ROOT` is set per website at `<site>/assets/staticfiles`, which keeps `ctc-research` and `lms-demo` build outputs isolated.

```bash
SERVER_ENV=production uv run python manage.py --site ctc-research collectstatic --noinput
SERVER_ENV=production uv run python manage.py --site lms-demo collectstatic --noinput
SERVER_ENV=production uv run python scripts/verify_runtime.py --site ctc-research --strict-assets --strict-pages
```

### Celery workers

All background tasks are handled by a single shared worker/scheduler pair. Site-specific context should be passed as task arguments rather than relying on per-site worker containers.

```bash
# Start the shared worker and scheduler
docker compose -f applications/compose/docker-compose.tasks.yml up -d shared-worker shared-scheduler

# Or use the Makefile target
make deploy-tasks
```

**Important:** The shared worker container defaults `DJANGO_SITE` to `ctc-research` for bootstrapping Django settings. Tasks that need to act on behalf of another site must accept the site as an argument and switch context inside the task (e.g., by calling `configs.site.configure_site_environment(site)` or by using a site-aware task decorator). Do not rely on the global `DJANGO_SITE` environment variable for per-site behavior in a shared worker.

**Note:** The shared worker listens on all queues (`shared`, `email`, `default`, `ctc-research`, `lms-demo`, `vresume`). If you add new site-specific queues, update the `--queues` list in `applications/compose/docker-compose.tasks.yml`.

### Delegate workflow for operators

Use this checklist when delegating deploy verification across people or automation agents:

1. **Build delegate:** run `docker compose -f docker-compose.yml build vresume-website` and confirm no dependency drift.
2. **Runtime delegate:** run `python manage.py --site <site> check`, `migrate`, `collectstatic`, and `scripts/verify_runtime.py` for each site.
3. **Tasks delegate:** start the relevant Celery worker/beat pair and inspect `compose/logs` for import or broker errors.
4. **Auth delegate:** submit HTMX login/register/password forms and verify `HX-Trigger` notification payloads and email backend output.
5. **Cleanup delegate:** follow `docs/reports/unused_files_plan.md` before removing duplicate legacy files.
