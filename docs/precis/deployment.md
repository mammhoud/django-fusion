---
title: Precis — Deployment
description: Precis Main deployment — Docker Compose services, build and deploy commands, proxy routing, admin smoke checks, logs and rollback.
navigation:
  title: Deployment
  icon: i-lucide-rocket
object:
  type: "guide"
  id: "docs.precis.deployment"
attributes:
  source_path: "precis/deployment.md"
  canonical_route: "/docs/en/precis/deployment"
  source_of_truth: "repository-markdown"
  owner: "precis-main"
  status: "maintained"
tags:
  - structa-cloud
  - precis
  - precis-main
  - deployment
  - docker
  - traefik
  - proxy
links:
  - label: "Precis home"
    to: "/precis"
    icon: "i-lucide-graduation-cap"
---

# 🚀 Precis — Deployment

> **Canonical project:** `projects/precis/precis-main/`
> **Compatibility aliases:** `WEBSITE=precis-lms`, `WEBSITE=precis-landing`,
> `WEBSITE=lms`, and `WEBSITE=structa` resolve to the unified Precis Main
> product where supported.

Precis Main serves the public marketing/catalog shell and LMS from one Django +
Wagtail backend and one Astro frontend. There is no separate production
`precis-lms` container stack.

## Docker Compose services

Source: `projects/precis/precis-main/docker-compose.yml`.

| Service | Container | Internal port | Purpose |
|---|---|---:|---|
| `backend` | `precis-main-backend` | `8074` | Django, Wagtail, APIs, auth, learning, admin |
| `frontend` | `precis-main-frontend` | `3000` | Astro public shell |
| `scheduler` | `precis-main-scheduler` | — | django-fusion task scheduler |

The application services use the external `common` and `traefik-net` networks.
PostgreSQL and Redis are shared infrastructure; site-specific database and
secret values come from the root `.env` or deployment secret store.

## Build and deploy

Run from the repository root:

```bash
# Validate interpolation and YAML without changing containers
docker compose --env-file .env \
  -f projects/precis/precis-main/docker-compose.yml config -q

# Build and start backend, frontend, and scheduler
docker compose --env-file .env \
  -f projects/precis/precis-main/docker-compose.yml up -d --build

# Inspect health and startup state
docker compose --env-file .env \
  -f projects/precis/precis-main/docker-compose.yml ps
```

The backend startup command applies migrations, collects static files, seeds
idempotent pages/learning data, and starts Gunicorn. Do not use the startup seed
command as a substitute for a reviewed production fixture reload.

Project-local delegation remains available:

```bash
cd projects/precis/precis-main
make backend-check
make backend-test
make build
```

## Proxy routing

Traefik dynamic configuration is owned by `application/proxy/`:

| Host | Router file | Backend | Frontend |
|---|---|---|---|
| `structa.cloud`, `www.structa.cloud` | `dynamic/precis-landing.yml` | `precis-main-backend:8074` | `precis-main-frontend:3000` |
| `lms.structa.cloud` | `dynamic/lms-fusion.yml` | `precis-main-backend:8074` | `precis-main-frontend:3000` |

Validate the proxy before or after a deployment:

```bash
python3 application/proxy/scripts/validate-traefik-config.py
docker compose --env-file application/proxy/.env \
  -f application/proxy/docker-compose.yml config -q
```

The routers send backend-owned `/api`, `/apis`, `/accounts`, `/learning`,
`/fragment`, `/documents`, and admin paths to Django. The frontend catch-all
handles public Astro pages. Site-specific `/static`, `/media`, and `/sites`
routes must follow the dynamic file rather than being duplicated in the Astro
container.

## Admin smoke checks

Wagtail and Django admin intentionally have separate paths:

```bash
# Wagtail CMS
curl -k -sS -L -o /dev/null \
  -w 'Wagtail: %{http_code} %{url_effective}\n' \
  https://structa.cloud/admin

# Django system admin
curl -k -sS -L -o /dev/null \
  -w 'Django admin: %{http_code} %{url_effective}\n' \
  https://structa.cloud/django-admin

# LMS compatibility host
curl -k -sS -L -o /dev/null \
  -w 'LMS Wagtail: %{http_code} %{url_effective}\n' \
  https://lms.structa.cloud/admin
```

Expected behavior is a no-slash `302` to the slash route and a final `200`
login page. `backend/urls.py` declares these exact redirects because
`APPEND_SLASH=False` is required for safe headless authentication POSTs.

## Logs and rollback

```bash
docker logs --since 10m precis-main-backend
docker logs --since 10m precis-main-frontend
docker logs --since 10m default-proxy
```

For an unhealthy rollout, preserve the PostgreSQL and named static/media
volumes, restore the previous application/proxy revision, re-run config
validation, and recreate only the affected services. Do not run
`docker compose down --volumes` for a normal rollback.

## Related

- [Precis product index](README.md)
- [Precis Main proxy and admin runbook](../dev/infrastructure/precis-main-proxy-admin.md)
- [Configuration](configuration.md)
- [Courses](courses.md)
- [Precis Landing compatibility deployment](precis-landing/deployment.md)

## Remarks & Notes

<!-- AI-generated: review needed -->

- The legacy `precis-lms` and `precis-landing` names remain in router identities
  and dispatcher aliases for compatibility; the load-balancer URLs must point
  to `precis-main-*` containers.
- A successful container health check does not prove DNS, ACME, SMTP, or media
  availability; verify those boundaries separately.
- Never place secret values, admin credentials, or full environment files in
  this document.
