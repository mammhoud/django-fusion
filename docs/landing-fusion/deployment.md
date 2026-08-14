# Landing Fusion — Deployment

> Docker Compose deployment with Traefik proxy, Let's Encrypt SSL, and Nginx media.

---

## Production Architecture

```
Browser → Traefik Proxy (:443, SSL)
    ├── structa.cloud → landing-fusion-frontend (Astro, :3000)
    ├── /apis/* → landing-fusion-backend (Django, :8074)
    ├── /accounts/* → landing-fusion-backend
    ├── /learning/* → landing-fusion-backend
    └── /static/* → shared-proxy (Nginx)
```

---

## Docker Compose

```yaml
# projects/landing-fusion/docker-compose.yml
services:
  backend:
    build: ../..  # Monorepo root
    context: projects/landing-fusion/backend
    port: 8074
    env:
      DJANGO_ALLOWED_HOSTS: structa.cloud,www.structa.cloud
      CSRF_TRUSTED_ORIGINS: https://structa.cloud
      CORS_ALLOWED_ORIGINS: https://structa.cloud

  frontend:
    build:
      context: projects/landing-fusion/frontend
    port: 3000
```

---

## Deploy Commands

```bash
# Build images
docker compose -f projects/landing-fusion/docker-compose.yml build

# Start services
docker compose -f projects/landing-fusion/docker-compose.yml up -d

# View logs
docker compose -f projects/landing-fusion/docker-compose.yml logs -f

# Restart
docker compose -f projects/landing-fusion/docker-compose.yml restart

# Stop
docker compose -f projects/landing-fusion/docker-compose.yml down
```

---

## Traefik Routing

The Traefik dynamic config routes by Host and PathPrefix:

```yaml
# applications/proxy/traefik/dynamic/landing-fusion.yml
http:
  routers:
    landing-fusion-www:
      rule: "Host(`structa.cloud`) || Host(`www.structa.cloud`)"
      service: landing-fusion-frontend

    landing-fusion-api:
      rule: "Host(`structa.cloud`) && (PathPrefix(`/apis/`) || PathPrefix(`/accounts/`) || PathPrefix(`/learning/`))"
      service: landing-fusion-backend
```

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins |
| `FUSION_RENDER_FIRST` | `1` to enable fusion-render-first mode |

---

## Health Checks

```bash
# Backend health
curl https://structa.cloud/apis/health/

# Frontend
curl https://structa.cloud/

# Languages API
curl https://structa.cloud/apis/content/languages/
```

---

## Related

- [`../README.md`](../README.md) — project overview
- [`backend-api.md`](backend-api.md) — backend API docs
- [`frontend.md`](frontend.md) — frontend docs
