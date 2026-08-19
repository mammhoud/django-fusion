# 🚀 Docker Deployment Pipeline

> How to build, deploy, and manage Docker containers across all Structa Cloud projects.

---

## Architecture

```
root Makefile (make deploy)
    │
    ├── make deploy-databases    → application/databases/
    │   ├── postgres:5432 (per-site DBs)
    │   └── redis:6379 (shared broker)
    │
    ├── make deploy-media        → shared-proxy (Nginx :80)
    │   ├── Static files: /var/www/sites/<site>/static/
    │   └── Media files:  /var/www/sites/<site>/media/
    │
    ├── make deploy-app          → application/compose/
    │   ├── precis-ctc:5070
    │   ├── lms:5071
    │   ├── portfolio:5072
    │   └── cypercloud:5073
    │
    ├── make deploy-tasks        → shared-worker + shared-scheduler
    │   ├── Dramatiq worker
    │   └── Celery beat scheduler
    │
    └── make deploy-proxy        → Traefik :443
        ├── Let's Encrypt DNS-01 (Cloudflare)
        └── Per-site routers + TLS
```

---

## Per-Project Docker Compose

| Project | Compose File | Container | Port |
|---------|-------------|-----------|------|
| CTC Research | `projects/precis-ctc/docker-compose.yml` | `precis-ctc-website` | 5070 |
| LMS | `projects/lms/docker-compose.yml` | `lms-web` | 5071 |
| Portfolio | `projects/portfolio/docker-compose.yml` | `vresume-web` | 5072 |
| Syntara | `projects/syntara/docker-compose.yml` | `cypercloud-web` | 5073 |

All built from `projects/compose/Dockerfile` (Python 3.11-slim, uv-installed deps, Gunicorn).

---

## Quick Deploy Commands

```bash
# Full stack (DB → media → apps → proxy)
make deploy

# Individual components
make deploy-databases     # Postgres + Redis
make deploy-media         # Nginx static/media server
make deploy-app           # All Django apps
make deploy-proxy         # Traefik reverse proxy
make deploy-tasks         # Background workers
make deploy-cypercloud    # Syntara (build + migrate)

# Status & logs
make status               # All container statuses
make logs                 # Tail all logs
make status-tasks         # Worker + scheduler status
make probe-health         # HTTP health checks per site
```

---

## Deployment Order

```
postgres-first (default):
  databases → coder → media → apps → tasks → docs → proxy

legacy:
  proxy → apps → media → tasks → docs → databases
```

Override: `make deploy DEPLOY_ORDER=legacy`

---

## Preflight Validation

Before any deploy, the preflight chain runs:

```bash
make deploy-preflight     # Validates compose files + deploy order
make deploy-ci            # CI-only gate (no actual deploy)
```

### Networks (auto-created)

| Network | Purpose |
|---------|---------|
| `common` | Django apps ↔ workers inter-container comms |
| `traefik-net` | Proxy ↔ backend routing |
| `internal` | DB ↔ app private channel |
| `utilities-net` | Monitoring stack |
| `warehouse-net` | POS sync services |
| `ollama-net` | AI model inference |

---

## Adding a New Project to Docker

1. Create `projects/<name>/docker-compose.yml`
2. Add to `application/compose/docker-compose.applications.yml` includes
3. Add Traefik router in `application/proxy/configs/traefik/dynamic/`
4. Add health check: `Host: 127.0.0.1` → `<port>/health/`
5. `make deploy-app` picks it up automatically

---

## Related

| Topic | Path |
|-------|------|
| Infrastructure | [`../infrastructure/`](../infrastructure/) |
| Backend env | [`../back-env/`](../back-env/) |
| CI/CD pipelines | [`ci-cd.md`](ci-cd.md) |
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
