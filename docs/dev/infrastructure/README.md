# 🚀 Infrastructure — Overview

> Proxy, databases, deployment, workers, Docker, and networking for the Structa Cloud monorepo.

---

## Architecture

```
Internet
  │
  ▼
Traefik Proxy (default-proxy)
  │  SSL via Let's Encrypt (Cloudflare DNS-01)
  │
  ├── ctc-research.com ──────→ precis-ctc-website:5070
  ├── structa.cloud ─────────→ lms-web:5071
  ├── vresume.structa.cloud ─→ vresume-web:5072
  ├── media.structa.cloud ───→ shared-proxy:80
  │
  └── Internal services (on common network):
       ├── postgres:5432
       ├── redis:6379
       ├── shared-worker (Dramatiq)
       ├── shared-scheduler (Celery Beat)
       └── coder:7080
```

---

## Components

| Component | Container | Port | Documentation |
|-----------|-----------|------|---------------|
| **Traefik Proxy** | `default-proxy` | 80, 443 | [`proxy.md`](proxy.md) |
| **Nginx Media** | `shared-proxy` | 80 | — |
| **PostgreSQL** | `default-postgres` | 5432 | [`../databases/`](../databases/) |
| **Redis** | `default-redis` | 6379 | — |
| **Dramatiq Worker** | `shared-worker` | — | [`shared-worker.md`](shared-worker.md) |
| **Celery Beat** | `shared-scheduler` | — | [`shared-worker.md`](shared-worker.md) |
| **Coder** | `coder` | 7080 | *(see coder.com docs)* |

---

## Deployment Order

```
1. Databases (PostgreSQL + Redis)
2. Coder (depends on Postgres)
3. Media Server (Nginx)
4. Django Sites + Worker Stack
5. Documentation Site
6. Proxy (Traefik — last so services register)
```

```bash
make deploy              # Full deploy in dependency order
make deploy-databases    # Just databases
make deploy-app          # Just Django sites
make deploy-tasks        # Just workers
```

---

## Health Checks

```bash
make probe-health        # HTTP probe against all site /health/ endpoints
make status-tasks        # Worker + scheduler status
make status              # Full deployment status
```

---

## Related

| Resource | Path |
|----------|------|
| Proxy & SSL | [`proxy.md`](proxy.md) |
| Deployment | [`deployment.md`](deployment.md) |
| Docker setup | [`docker/`](docker/) |
| Shared worker | [`shared-worker.md`](shared-worker.md) |
| Databases | [`../databases/`](../databases/) |
