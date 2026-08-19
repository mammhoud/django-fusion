# 🐳 Docker — Container Architecture & Setup

> Docker Compose orchestration for all Structa Cloud services — databases, sites, proxy, workers, and tools.

---

## Container Overview

| Container | Service | Port | Network |
|-----------|---------|------|---------|
| `postgres` | PostgreSQL 16 | 5432 | `common` |
| `default-redis` | Redis 7 | 6379 | `common` |
| `default-proxy` | Traefik 3 | 80, 443 | `traefik-net` |
| `shared-proxy` | Nginx (static/media) | 80 | `common` |
| `shared-worker` | Dramatiq worker | — | `common` |
| `shared-scheduler` | Celery Beat | — | `common` |
| `coder` | Coder platform | 7080 | `common` |

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
| `projects/docker-compose.tasks.yml` | shared-worker + shared-scheduler |
| `application/databases/docker-compose.yml` | Postgres + Redis |
| `application/docker-compose.yml` | Coder control plane |
| `application/proxy/docker-compose.yml` | Traefik proxy |
| `application/proxy/docker-compose.nginx.yml` | Nginx media server |
| `docker-compose.yml` (repo root) | Coder control plane |
| Per-site compose files | Django site containers (e.g. `projects/precis/precis-ctc/docker-compose.yml`) |

---

## Quick Commands

```bash
make deploy              # Full deploy (DB → media → apps → proxy)
make deploy-databases    # Postgres + Redis only
make deploy-app          # Django site containers
make deploy-tasks        # Worker + scheduler
make deploy-proxy        # Traefik proxy
docker compose -f application/docker-compose.yml up -d coder  # Coder platform
make status              # Show all container statuses
make logs                # Tail logs from all services
make stop                # Stop all services
```

---

## Shared Dockerfile

Site containers build from per-product Dockerfiles (e.g. `projects/precis/precis-ctc/backend/Dockerfile`, `projects/loop-crm/Dockerfile`, `projects/syntara/Dockerfile`), with a multi-stage pattern that builds webpack bundles in a Node image, then copies them into a `python:3.11-slim` app image. The docs site builds from `docs/Dockerfile`.

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
