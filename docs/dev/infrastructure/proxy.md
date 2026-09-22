# 🔴 Proxy — `application/proxy/`

Traefik reverse proxy with Let's Encrypt SSL, serving all Structa Cloud sites.

> **Customization level**: ⚪ Config Only — change via env vars + YAML config files.

## Architecture

```
Internet → Traefik (port 443, SSL)
              ├── structa.cloud           → Precis Main frontend/backend
              ├── lms.structa.cloud       → Precis Main frontend/backend
              ├── ctc-research.com        → CTC Research frontend/backend
              ├── crm.structa.cloud       → Loop-CRM frontend/backend
              ├── space.structa.cloud     → Coder control plane (coder:7080)
              ├── tools.structa.cloud     → Nginx shared-proxy (adminer, mailpit, Open WebUI, Grafana, Docus, AFFiNE /space/)
              ├── media.*                 → Nginx shared-proxy
              └── docs.structa.cloud      → Documentation site
```

The workspace product is branded **space**: `space.structa.cloud` routes to the
Coder control plane (`coder:7080`). AFFiNE is served path-based at
`tools.structa.cloud/space/` (`proxy-affine:3010`). The retired
`coder.structa.cloud` / `code.structa.cloud` aliases are gone.

## Key Files

| File | Purpose | Level |
|------|---------|-------|
| `docker-compose.traefik.yml` | Proxy service definition | 🔴 |
| `configs/traefik/dynamic.yml` | Static config (entrypoints, providers, ACME resolver) | 🔴 |
| `configs/traefik/dynamic/*.yml` | Dynamic config (routers, services, middleware) | 🔴 |
| `configs/acme.json` | Let's Encrypt cert store (mode 0600) | 🔴 |
| `.env` | Let's Encrypt email, env vars | ⚪ |
| `.env.example` | Template for `.env` | ⚪ |
| `dynamic/precis-landing.yml` | `structa.cloud` → Precis Main routers | 🔴 |
| `dynamic/lms-fusion.yml` | `lms.structa.cloud` → Precis Main routers | 🔴 |
| `dynamic/space.yml` | `space.structa.cloud` → Coder control plane (`coder:7080`) | 🔴 |
| `dynamic/tools.yml` | `tools.structa.cloud` → shared-proxy Nginx (tools + AFFiNE `/space/`) | 🔴 |

## SSL Rollout Stages

| Stage | What | Status |
|-------|------|--------|
| 1 | Enable LE staging for vresume | 🟡 |
| 2 | Production CA + all sites | 🟡 |
| 3 | Delete self-signed cert fallback | 🟡 |

## Quick Commands

```bash
cd application/proxy

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

## Precis Main compatibility routing

`structa.cloud` and `lms.structa.cloud` are served by the unified
`projects/structa.cloud/` stack. Both dynamic files target
`precis-main-backend:8074` and `precis-main-frontend:3000`; they do not target
legacy `precis-landing-*` or `precis-lms-*` containers.

For the admin contract and deployment smoke tests, see
[`precis-main-proxy-admin.md`](precis-main-proxy-admin.md).

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

## Remarks & Notes

- Keep router priorities above the frontend catch-all for backend-owned paths.
- Validate dynamic YAML with `python3 application/proxy/scripts/validate-traefik-config.py`
  before reloading Traefik.
- A 503 can mean the target container is absent or unhealthy; verify Compose
  service health and Docker network DNS before changing route rules.

---

→ [Back to Infrastructure docs](README.md)
