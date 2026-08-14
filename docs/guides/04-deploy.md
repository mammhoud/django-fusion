# 04 — Deployment Guide

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
   ctc-research  lms   VResume
   (Django)      (Django)   (Django)
       │          │          │
       └──────────┼──────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
     PostgreSQL          Redis
     (5432)              (6379)
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

> ⚠️ **Warning:** The ACME store at `applications/proxy/acme/acme.json` must have `0600` permissions and is gitignored. Never commit it.

### Required Env Vars

```bash
# applications/proxy/.env
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
cd applications/databases
make deploy

# Proxy
cd applications/proxy
make deploy

# Specific site
cd projects
make docker-up WEBSITE=ctc-research
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
docker exec ctc-research-website python manage.py check
```

---

## Database Management

### Backup

```bash
# PostgreSQL dump
docker exec postgres pg_dump -U structa_user ctc_research_db > backup_ctc.sql

# All databases
cd applications/databases
make backup
```

### Restore

```bash
docker exec -i postgres psql -U structa_user ctc_research_db < backup_ctc.sql
```

### Migrations

```bash
cd projects
make migrate WEBSITE=ctc-research
```

---

## Troubleshooting

### 502 Bad Gateway

```bash
# Check if Django is running
docker ps | grep ctc-research
docker logs ctc-research-website --tail 50

# Check Django
docker exec ctc-research-website python manage.py check
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
docker exec ctc-research-website python manage.py collectstatic --noinput
```

### Database Connection Refused

```bash
docker exec postgres pg_isready
docker logs postgres | tail -50
docker exec postgres psql -U structa_user -d ctc_research_db -c "SELECT 1"
```

---

→ [Back to Guides](README.md) | [Infrastructure Docs](../infrastructure/) | [Backend Env](../back-env/)
