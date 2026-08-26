---
title: Deploy
description: Production deployment for Django sites — Docker, Traefik, Let's Encrypt SSL, health checks, DB backups, troubleshooting.
navigation:
  title: Deploy
  icon: i-lucide-rocket
object:
  type: "guide"
  id: "guide.deploy"
attributes:
  source_path: "guides/05-deploy.md"
  canonical_route: "/docs/en/guides/05-deploy"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - deploy
  - production
  - docker
  - ssl
  - traefik
  - proxy
links:
  - label: "Dev"
    to: "/guides/04-dev"
    icon: "i-lucide-code"
  - label: "Customize"
    to: "/guides/06-customize"
    icon: "i-lucide-palette"
  - label: "Infrastructure"
    to: "/dev/infrastructure"
    icon: "i-lucide-server"
---

# 🚀 Deploy — Deployment Guide

> **Related:** `infrastructure/deployment.md`, `infrastructure/proxy.md`, `infrastructure/routing-proxy.md`, `back-env/`
> **Tags:** #deployment #production #docker #ssl #proxy

How to deploy Structa Cloud Django sites and infrastructure to production.

---

## Architecture

```
Internet
  │
  ▼
┌──────────────────────────────────────────────┐
│          Traefik Proxy (443/80)              │
│          SSL: Let's Encrypt (Cloudflare DNS) │
└──────┬──────────┬──────────┬─────────────────┘
       │          │          │
       ▼          ▼          ▼
  precis-ctc  lms   VResume
  (Django)      (Django)   (Django)
       │          │          │
       └──────────┼──────────┘
                  │
          ┌───────┴───────┐
          ▼               ▼
      PostgreSQL        Redis
      (5432)            (6379)
```

---

## Infrastructure Services

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| `default-proxy` | Traefik | 80, 443 | SSL termination, routing |
| `shared-proxy` | Nginx | 80 | Static/media files |
| `postgres` | PostgreSQL 15 | 5432 | Primary database |
| `default-redis` | Redis 7 | 6379 | Cache, sessions, Celery |

---

## SSL / Let's Encrypt

### Rollout Stages

1. **Stage 1:** Enable LE **staging** CA for `vresume.structa.cloud`
2. **Stage 2:** Flip to **production** CA, enable for all sites
3. **Stage 3:** Delete self-signed cert fallback

> ⚠️ **Warning:** The ACME store at `application/proxy/configs/acme.json` must have `0600` permissions and is gitignored. Never commit it.

### Required Env Vars

```bash
# application/proxy/.env
CF_DNS_API_TOKEN=your-cloudflare-api-token
# OR
CF_API_EMAIL=your@email.com
CF_API_KEY=your-global-api-key
```

> 💡 **Tip:** DNS-01 challenge means no open ports needed — Let's Encrypt validates via Cloudflare DNS TXT records.

---

## Deploy Commands

### Full Deploy

```bash
# From project root
make deploy              # Full stack deploy
```

### Individual Services

```bash
# Databases
cd application/databases
make deploy

# Proxy
cd application/proxy
make deploy

# Specific site
cd projects
make docker-up WEBSITE=precis-ctc
```

### Health Checks

```bash
# Proxy
curl -k https://localhost/health

# Database
docker exec postgres pg_isready

# Redis
docker exec default-redis redis-cli ping

# Django site
docker exec precis-ctc-website python manage.py check
```

---

## Database Management

### Backup

```bash
# PostgreSQL dump
docker exec postgres pg_dump -U structa_user ctc_research_db > backup_ctc.sql

# All databases
cd application/databases
make backup
```

### Restore

```bash
docker exec -i postgres psql -U structa_user ctc_research_db < backup_ctc.sql
```

### Migrations

```bash
cd projects
make migrate WEBSITE=precis-ctc
```

---

## Troubleshooting

### 502 Bad Gateway

```bash
# Check if Django is running
docker ps | grep precis-ctc
docker logs precis-ctc-website --tail 50

# Check Django
docker exec precis-ctc-website python manage.py check
```

### SSL Certificate Error

```bash
# Check Traefik logs
docker logs default-proxy | grep -i "acme\|challenge\|certificate"

# Check cert expiry
echo | openssl s_client -connect ctc-research.com:443 -servername ctc-research.com 2>/dev/null | openssl x509 -noout -dates
```

### Static Files Not Loading

```bash
# Check shared-proxy
docker ps | grep shared-proxy
docker logs shared-proxy

# Recollect
docker exec precis-ctc-website python manage.py collectstatic --noinput
```

### Database Connection Refused

```bash
docker exec postgres pg_isready
docker logs postgres | tail -50
docker exec postgres psql -U structa_user -d ctc_research_db -c "SELECT 1"
```

---

## ## Remarks & Notes

- **Order matters:** Deploy databases → proxy → sites → workers. `make deploy` enforces this.
- **ACME store** (`application/proxy/configs/acme.json`) is gitignored and must be `0600`.
- **DNS-01 challenge** requires Cloudflare API token — no open ports needed for validation.
- **Staging → Production** SSL rollout prevents rate limits on new domains.
- **Health checks** (`make probe-health`) hit each site's `/health` endpoint via the common network.

---

→ [Back to Guides](README.md) | [Infrastructure Docs](/docs/en/dev/infrastructure) | [Backend Environments](/docs/en/dev/back-env)

<!-- AI-generated: review needed -->