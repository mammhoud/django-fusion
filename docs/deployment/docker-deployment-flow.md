# Docker Deployment Flow

This guide defines the stable deployment flow for the current repository layout.

## Compose file roles

| File | Role | Typical command |
|---|---|---|
| `applications/databases/docker-compose.yml` | PostgreSQL and Redis, plus optional Celery worker/beat definitions. | `docker compose -f applications/databases/docker-compose.yml up -d vresume-postgres vresume-redis` |
| `applications/compose/docker-compose.yml` | Django application container for the selected site. | `docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.yml up -d --build vresume-website` |
| `applications/compose/docker-compose.tasks.yml` | Shared Celery worker/beat for cross-site background jobs. | `docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.tasks.yml up -d shared-tasks-worker shared-tasks-beat` |
| `applications/proxy/docker-compose.traefik.yml` | Traefik edge proxy and TLS termination. | `docker compose -f applications/proxy/docker-compose.traefik.yml up -d` |
| `applications/proxy/docker-compose.nginx.yml` | Optional Nginx static/media reverse proxy when Traefik is not serving assets directly. | `docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.yml -f applications/proxy/docker-compose.nginx.yml up -d` |
| `applications/compose/docker-compose.docs.yml` | Documentation service. | `docker compose -f applications/compose/docker-compose.docs.yml up -d` |

## Recommended production sequence

1. **Create the external network once**:

   ```bash
   docker network create traefik-net || true
   ```

2. **Prepare `.env` at the repository root**:

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
   ACME_CA_SERVER=https://acme-v02.api.letsencrypt.org/directory
   ```

3. **Start the warehouse layer first**:

   ```bash
   docker compose -f applications/databases/docker-compose.yml up -d vresume-postgres vresume-redis
   ```

4. **Build and start the selected Django site**:

   ```bash
   docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.yml up -d --build vresume-website
   ```

5. **Run one-time setup and runtime verification**:

   ```bash
   docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.yml exec vresume-website python manage.py --site "$PROJECT_PATH" check
   docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.yml exec vresume-website python manage.py --site "$PROJECT_PATH" migrate --noinput
   docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.yml exec vresume-website python manage.py --site "$PROJECT_PATH" collectstatic --noinput
   docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.yml exec vresume-website python scripts/verify_runtime.py --site "$PROJECT_PATH" --strict-assets --strict-pages
   ```

6. **Start background jobs if the site uses queued work**:

   ```bash
   docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.tasks.yml up -d shared-tasks-worker shared-tasks-beat
   ```

7. **Start the edge proxy**:

   ```bash
   docker compose -f applications/proxy/docker-compose.traefik.yml up -d
   ```

8. **Watch health and logs**:

   ```bash
   docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.yml ps
   docker compose -f applications/databases/docker-compose.yml -f applications/compose/docker-compose.yml logs -f --tail=200 vresume-website
   curl -fL -H 'X-Forwarded-Proto: https' http://localhost:5072/health/
   ```

## Stability rules

- Keep `PROJECT_PATH`, `DJANGO_SITE`, `DJANGO_WEBSITE`, and `WEBSITE` aligned to the same site directory unless intentionally testing aliases.
- Use `SERVER_TYPE=gunicorn` for production and `SERVER_TYPE=uvicorn RELOAD=true` only for development.
- Keep PostgreSQL and Redis passwords outside committed files; `.env` should override the safe examples above.
- Run `docker compose ... config` before a deployment window to catch YAML, variable, and service graph errors.
- Run Django `check`, migrations, static collection, and `scripts/verify_runtime.py` before routing production traffic.
