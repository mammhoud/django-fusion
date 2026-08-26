---
title: Precis Main proxy and admin routing
description: Current Traefik and Compose contract for structa.cloud and lms.structa.cloud.
navigation:
  title: Precis Main proxy routing
  icon: i-lucide-route
object:
  type: "runbook"
  id: "docs.infrastructure.precis-main-proxy-admin"
attributes:
  source_path: "dev/infrastructure/precis-main-proxy-admin.md"
  canonical_route: "/docs/en/dev/infrastructure/precis-main-proxy-admin"
  source_of_truth: "repository-markdown"
  owner: "precis-main"
  status: "maintained"
tags:
  - precis-main
  - traefik
  - admin
  - deployment
  - lms
links:
  - label: "Precis documentation"
    to: "/precis"
    icon: "i-lucide-graduation-cap"
  - label: "Proxy guide"
    to: "/dev/infrastructure/proxy"
    icon: "i-lucide-network"
---

# Precis Main proxy and admin routing

<!-- AI-generated: review needed -->

This is the current deployment contract for the unified Precis product. The
canonical application is `projects/precis/precis-main/`; the historical
`precis-lms` and `precis-landing` names are compatibility aliases, not separate
runtime stacks.

## Runtime topology

```text
structa.cloud / lms.structa.cloud
        │
        ▼
Traefik default-proxy
        ├─ public/backend paths → precis-main-backend:8074
        ├─ public/catch-all     → precis-main-frontend:3000
        └─ /static/, /media/    → shared-proxy where the site router declares it

precis-main-backend
        ├─ PostgreSQL: db_precis_landing
        └─ Redis/task services through the shared Compose networks
```

The application services join the external `common` and `traefik-net` networks.
The source of truth is:

- Compose: `projects/precis/precis-main/docker-compose.yml`
- Structa router: `application/proxy/configs/traefik/dynamic/precis-landing.yml`
- LMS router: `application/proxy/configs/traefik/dynamic/lms-fusion.yml`
- Django URLs: `projects/precis/precis-main/backend/urls.py`

## Traefik service targets

| Router file | Host | Backend target | Frontend target | Backend health check |
|---|---|---|---|---|
| `precis-landing.yml` | `structa.cloud`, `www.structa.cloud` | `http://precis-main-backend:8074` | `http://precis-main-frontend:3000` | `/apis/pages/` |
| `lms-fusion.yml` | `lms.structa.cloud` | `http://precis-main-backend:8074` | `http://precis-main-frontend:3000` | `/apis/pages/` |

The logical Traefik router/service identifiers retain their historical
Precis Landing/LMS labels for compatibility, but their load-balancer URLs must
remain pointed at the `precis-main-*` containers. Do not restore the removed
`precis-landing-*` or `precis-lms-*` container URLs.

## Backend path ownership

Backend routers have priority over the frontend catch-all for API, auth,
learning, document, fragment, and administration paths. The public admin
contract is:

| URL | Owner | Expected unauthenticated response |
|---|---|---|
| `/admin` | Django redirect | `302` to `/admin/` |
| `/admin/` | Wagtail | `302` to `/admin/login/?next=/admin/` |
| `/django-admin` | Django redirect | `302` to `/django-admin/` |
| `/django-admin/` | Django admin | `302` to `/django-admin/login/?next=/django-admin/` |

`precis-main` keeps `APPEND_SLASH=False` because headless authentication POSTs
must not be redirected by `CommonMiddleware`. The exact no-slash redirects are
therefore declared explicitly in `backend/urls.py`.

The production Compose environment allows both public domains through
`DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `CORS_ALLOWED_ORIGINS`.

## Deploy and validate

Run from the repository root. The root `.env` is passed explicitly so the
Compose interpolation and container environment use the same deployment
configuration.

```bash
# Read-only syntax validation
docker compose --env-file .env \
  -f projects/precis/precis-main/docker-compose.yml config -q
python3 application/proxy/scripts/validate-traefik-config.py

docker compose --env-file application/proxy/.env \
  -f application/proxy/docker-compose.yml config -q

# Build and start the unified stack
docker compose --env-file .env \
  -f projects/precis/precis-main/docker-compose.yml up -d --build

# Confirm service health
docker compose --env-file .env \
  -f projects/precis/precis-main/docker-compose.yml ps
```

Verify the public routes after the backend and frontend health checks pass:

```bash
curl -k -sS -o /dev/null -D - https://structa.cloud/admin
curl -k -sS -L -o /dev/null \
  -w 'Wagtail: %{http_code} %{url_effective}\n' \
  https://structa.cloud/admin

curl -k -sS -L -o /dev/null \
  -w 'Django admin: %{http_code} %{url_effective}\n' \
  https://structa.cloud/django-admin

curl -k -sS -L -o /dev/null \
  -w 'LMS Wagtail: %{http_code} %{url_effective}\n' \
  https://lms.structa.cloud/admin
```

Expected final pages are the Wagtail login page for `/admin` and the Django
admin login page for `/django-admin`; authentication is intentionally not
performed by this smoke check.

## Troubleshooting

- **503 from Traefik:** check `docker compose ps`, then inspect
  `docker logs default-proxy` for target DNS/health-check failures. Confirm the
  `precis-main-backend` and `precis-main-frontend` names resolve on
  `traefik-net`.
- **404 on `/admin` without a slash:** the backend image is stale or the exact
  redirect routes from `backend/urls.py` were not included. Rebuild the backend
  image and recreate the service.
- **Django `DisallowedHost`:** confirm `lms.structa.cloud` is present in the
  production Compose host allowlist and recreate the backend container.
- **Frontend assets missing:** follow the static/media routing guide and verify
  `shared-proxy` separately; do not point the frontend catch-all at the Django
  backend.

## Rollback

Keep the database and named media/static volumes. If a deployment is unhealthy,
restore the previous Compose/configuration revision, run the read-only validation
commands, and recreate only the affected application services. Do not use
`docker compose down --volumes` as a routine rollback.

## Remarks & Notes

- This guide was added after the migration from legacy Precis Landing/LMS
  container names to the unified Precis Main services and was verified against
  the live `structa.cloud` and `lms.structa.cloud` admin routes on 19 August
  2026.
- The proxy may still emit unrelated ACME/DNS warnings for other configured
  hosts; investigate those independently from Precis route health.
- `make check` currently reports Treebeard future-compatibility warnings in the
  Precis backend; they are warnings, not a failed deployment gate.
