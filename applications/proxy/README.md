# 📁 Proxy Infrastructure (`applications/proxy/`)

## What's Here

Traefik reverse proxy with Let's Encrypt SSL termination for all Structa Cloud sites.

```
proxy/
├── docker-compose.yml        # 🔴 Proxy service definition
├── Dockerfile                # 🔴 Proxy image
├── traefik/
│   ├── traefik.yml           # 🔴 Static config (entrypoints, providers)
│   └── dynamic.yml           # 🔴 Dynamic config (routers, services, middleware)
├── certs/                    # 🔵 SSL certificates (self-signed fallback)
├── acme/                     # 🔵 Let's Encrypt ACME store
│   └── acme.json             #    (mode 0600, gitignored)
├── scripts/
│   └── manage-certs.sh       # 🟢 Certificate management
├── .env.example              # 🟢 Environment template
├── Makefile                  # 🟢 Proxy commands
└── LETSENCRYPT.md            #    SSL rollout guide
```

## Customization Tags

| Module | Tag | How to customize |
|--------|-----|-----------------|
| `dynamic.yml` routers | 🟢 `customizable` | Add new site routers |
| `dynamic.yml` services | 🟢 `customizable` | Point services to backends |
| `traefik.yml` | 🔴 `not-customizable` | Entrypoint definitions — change breaks routing |
| `docker-compose.yml` | 🔴 `not-customizable` | Must match Traefik config |
| `.env` | ⚪ `config-only` | Set `CF_DNS_API_TOKEN` for Let's Encrypt |
| `manage-certs.sh` | 🟢 `customizable` | Add new cert management commands |

## Quick Commands

```bash
make up        # Start proxy
make down      # Stop proxy
make status    # Check health
make logs      # View proxy logs
```

## Reference

- [Infrastructure Docs →](../../docs/infrastructure/README.md)
- [Proxy Docs →](../../docs/infrastructure/proxy.md)
