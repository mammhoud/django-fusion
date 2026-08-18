# 🔴 Proxy — `applications/proxy/`

Traefik reverse proxy with Let's Encrypt SSL, serving all Structa Cloud sites.

> **Customization level**: ⚪ Config Only — change via env vars + YAML config files.

## Architecture

```
Internet → Traefik (port 443, SSL)
              ├── structa.cloud           → Django app container
              ├── ctc-research.com        → Django app container
              ├── lms.com            → Django app container
              ├── vresume.structa.cloud   → Django app container
              ├── media.*                 → Nginx shared-proxy
              ├── dashboard.structa.cloud → Monitoring dashboard
              └── docs.structa.cloud      → Documentation site
```

## Key Files

| File | Purpose | Level |
|------|---------|-------|
| `docker-compose.traefik.yml` | Proxy service definition | 🔴 |
| `configs/traefik/dynamic.yml` | Static config (entrypoints, providers, ACME resolver) | 🔴 |
| `configs/traefik/dynamic/*.yml` | Dynamic config (routers, services, middleware) | 🔴 |
| `configs/acme.json` | Let's Encrypt cert store (mode 0600) | 🔴 |
| `.env` | Let's Encrypt email, env vars | ⚪ |
| `.env.example` | Template for `.env` | ⚪ |

## SSL Rollout Stages

| Stage | What | Status |
|-------|------|--------|
| 1 | Enable LE staging for vresume | 🟡 |
| 2 | Production CA + all sites | 🟡 |
| 3 | Delete self-signed cert fallback | 🟡 |

## Quick Commands

```bash
cd applications/proxy

make up              # Start proxy
make down            # Stop proxy
make logs            # View Traefik logs
make status          # Health check
make reload          # Reload config without downtime
```

## Environment Variables

```env
LETSENCRYPT_EMAIL=admin@structa.cloud    # Let's Encrypt account email (HTTP-01)
```

## Adding a New Site Router

```yaml
# In configs/traefik/dynamic/<site>.yml
http:
  routers:
    new-site:
      rule: "Host(`newsite.structa.cloud`)"
      service: new-site-service
      tls:
        certResolver: letsencrypt-http

  services:
    new-site-service:
      loadBalancer:
        servers:
          - url: "http://new-site-container:8000"
```

---

→ [Back to Infrastructure docs](README.md)
