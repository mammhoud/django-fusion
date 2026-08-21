---
title: Precis — Configuration
description: Precis Main configuration — core environment variables, the public host contract, local checks, and Compose validation.
navigation:
  title: Configuration
  icon: i-lucide-settings
object:
  type: "guide"
  id: "docs.precis.configuration"
attributes:
  source_path: "precis/configuration.md"
  canonical_route: "/docs/en/precis/configuration"
  source_of_truth: "repository-markdown"
  owner: "precis-main"
  status: "maintained"
tags:
  - structa-cloud
  - precis
  - precis-main
  - configuration
  - environment
  - deployment
links:
  - label: "Precis home"
    to: "/docs/en/precis"
    icon: "i-lucide-graduation-cap"
---

# ⚙️ Precis — Configuration

> **Canonical project:** `projects/precis/precis-main/`
> **Runtime:** Django 5.2 + Wagtail 7.4 + django-fusion with an Astro frontend.

Precis Main is configured by `projects/precis/precis-main/docker-compose.yml`
for deployment and by `backend/settings.py` for local defaults. The former
standalone LMS/landing configuration is a compatibility alias, not a second
runtime configuration.

## Core environment variables

| Variable | Purpose |
|---|---|
| `DJANGO_SETTINGS_MODULE` | Django settings module; production uses `settings` |
| `PRECIS_MAIN_DJANGO_SECRET_KEY` / `DJANGO_SECRET_KEY` | Shared Django signing key |
| `DJANGO_DEBUG` | Production debug switch; Compose sets `0` |
| `DJANGO_ALLOWED_HOSTS` | Includes `structa.cloud`, `www.structa.cloud`, and `lms.structa.cloud` |
| `CSRF_TRUSTED_ORIGINS` | HTTPS origins allowed to submit Django forms |
| `CORS_ALLOWED_ORIGINS` | Browser origins allowed to call credentialed APIs |
| `DJANGO_DB_NAME` | Defaults from `DB_NAME_LANDING` (`db_precis_landing`) |
| `DJANGO_DB_USER` / `DJANGO_DB_PASSWORD` | PostgreSQL credentials |
| `DJANGO_DB_HOST` / `DJANGO_DB_PORT` | PostgreSQL service and port |
| `FUSION_RENDER_FIRST` | `1` enables Fusion render-first mode; `0` keeps the data-API default |
| `WAGTAILADMIN_BASE_URL` | Canonical Wagtail admin origin, normally `https://structa.cloud` |
| `EMAIL_BACKEND` and `EMAIL_*` | Transactional email provider settings; values belong in the secret store |

Use names from `.env.example` or the Compose file. Never commit secret values
or copy a full production `.env` into documentation.

## Public host contract

Both public hosts are accepted by the backend:

- `structa.cloud` / `www.structa.cloud` — primary public/catalog host
- `lms.structa.cloud` — compatibility LMS host routed to the same containers

The proxy routes both hosts to `precis-main-backend:8074` for backend-owned
paths and `precis-main-frontend:3000` for the Astro catch-all. See the
[Precis Main proxy/admin runbook](../dev/infrastructure/precis-main-proxy-admin.md).

## Local checks

```bash
cd projects/precis/precis-main/backend
make check
make test

# Apply local SQLite migrations when needed
make migrate
```

For the deployed stack, validate the resolved Compose configuration without
printing environment values:

```bash
docker compose --env-file .env \
  -f projects/precis/precis-main/docker-compose.yml config -q
```

## Remarks & Notes

- `APPEND_SLASH=False` is intentional for headless authentication POST safety;
  `/admin` and `/django-admin` have explicit redirects in `backend/urls.py`.
- A shared `DJANGO_SECRET_KEY` is required across backend, scheduler, and worker
  processes whenever those processes sign or validate session/token data.
- Do not point the Precis Main database at CTC or another product database;
  site isolation is part of the deployment contract.
