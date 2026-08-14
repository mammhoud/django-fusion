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
| `docker-compose.yml` | Proxy service definition | 🔴 |
| `traefik/traefik.yml` | Static config (entrypoints, providers) | 🔴 |
| `traefik/dynamic.yml` | Dynamic config (routers, services, middleware) | 🔴 |
| `acme/acme.json` | Let's Encrypt cert store (mode 0600) | 🔴 |
| `.env` | Cloudflare credentials, env vars | ⚪ |
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
CF_DNS_API_TOKEN=dns-token-here    # Cloudflare API token for DNS-01 challenge
# OR (legacy)
CF_API_EMAIL=you@example.com
CF_API_KEY=your-api-key
```

## Adding a New Site Router

```yaml
# In traefik/dynamic.yml
http:
  routers:
    new-site:
      rule: "Host(`newsite.structa.cloud`)"
      service: new-site-service
      tls:
        certResolver: letsencrypt

  services:
    new-site-service:
      loadBalancer:
        servers:
          - url: "http://new-site-container:8000"
```

---

→ [Back to Infrastructure docs](README.md)
