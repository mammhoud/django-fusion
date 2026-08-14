# 🐳 Docker — Container Architecture & Setup

> Docker Compose orchestration for all Structa Cloud services — databases, sites, proxy, workers, and tools.

---

## Container Overview

| Container | Service | Port | Network |
|-----------|---------|------|---------|
| `default-postgres` | PostgreSQL 16 | 5432 | `common` |
| `default-redis` | Redis 7 | 6379 | `common` |
| `default-proxy` | Traefik 3 | 80, 443 | `traefik-net` |
| `shared-proxy` | Nginx (static/media) | 80 | `common` |
| `shared-worker` | Dramatiq worker | — | `common` |
| `shared-scheduler` | Celery Beat | — | `common` |
| `ctc-research-website` | Django/Gunicorn | 5070 | `common` |
| `lms-web` | Django/Gunicorn | 5071 | `common` |
| `vresume-web` | Django/Gunicorn | 5072 | `common` |
| `cypercloud` | Django/Gunicorn | 5073 | `common` |
| `coder` | Coder platform | 7080 | `common` |
| `coolify` | Coolify | 8000 | `coolify` |

---

## Docker Networks

```
┌──────────────────────────────────────────────────────┐
│                    traefik-net                       │
│  default-proxy (Traefik)                             │
└────────────┬─────────────────────────────────────────┘
             │ routes to
┌────────────▼──────────────────────────────────────────┐
│                    common                             │
│  postgres | redis | nginx | sites | workers | coder  │
└───────────────────────────────────────────────────────┘
```

| Network | Purpose | Connected Services |
|---------|---------|-------------------|
| `traefik-net` | Public ingress | Proxy only |
| `common` | Internal communication | All backend services |
| `internal` | Secure internal-only | DB management tools |
| `utilities-net` | Monitoring stack | Prometheus, Grafana |
| `ollama-net` | AI inference | Ollama, Open WebUI |
| `coolify` | Coolify platform | Coolify containers |

---

## Compose Files

| File | Services |
|------|----------|
| `applications/compose/docker-compose.applications.yml` | All Django site containers |
| `applications/docker-compose.tasks.yml` | shared-worker + shared-scheduler |
| `applications/databases/docker-compose.yml` | Postgres + Redis |
| `applications/docker-compose.yml` | Coder control plane |
| `applications/proxy/docker-compose.yml` | Traefik proxy |
| `applications/proxy/docker-compose.nginx.yml` | Nginx media server |
| `applications/proxy/docker-compose.nginx.yml` (`docs` service) | Documentation site |

---

## Quick Commands

```bash
make deploy              # Full deploy (DB → media → apps → proxy)
make deploy-databases    # Postgres + Redis only
make deploy-app          # Django site containers
make deploy-tasks        # Worker + scheduler
make deploy-proxy        # Traefik proxy
docker compose -f applications/docker-compose.yml up -d coder  # Coder platform
make status              # Show all container statuses
make logs                # Tail logs from all services
make stop                # Stop all services
```

---

## Shared Dockerfile

All Django sites use a single shared Dockerfile at `projects/compose/Dockerfile`:

```dockerfile
# Build-time: PROJECT_PATH arg selects the site
FROM python:3.11-slim AS app-base
ARG PROJECT_PATH=ctc-research

# Multi-stage: builds webpack bundles in node:24-slim,
# then copies them into the python:3.11-slim app image.
```

Python version is 3.11 — matches `.python-version` for local development.

---

## Docker Ignore

Key patterns in `.dockerignore`:

```
**/node_modules        # Rebuilt in Docker
**/.venv               # Docker uses /opt/venv internally
**/__pycache__         # Bytecode
**/.git                # Not needed in image
**/*.log               # Runtime logs
```

---

## Related

| Resource | Path |
|----------|------|
| Infrastructure overview | [`../README.md`](../README.md) |
| Proxy & SSL | [`../proxy.md`](../proxy.md) |
| Deployment guide | [`../deployment.md`](../deployment.md) |
| Shared worker | [`../shared-worker.md`](../shared-worker.md) |
