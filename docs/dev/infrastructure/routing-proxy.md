# Proxy & Routing

> **Related Names:** `Traefik`, `SSL`, `Let's Encrypt`, `Cloudflare`, `DNS-01`, `ACME`, `certificate`, `media`, `nginx`, `shared-proxy`
> **Tags:** #proxy #ssl #letsencrypt #routing #infrastructure

The default proxy (`default-proxy`) serves SSL on port 443.

- Global config: `application/proxy/configs/traefik/dynamic.yml`
- Per-site routers: `application/proxy/configs/traefik/dynamic/*.yml`
- Let's Encrypt store: `application/proxy/configs/acme.json`

## Let's Encrypt

Certs are obtained via Let's Encrypt DNS-01 (Cloudflare).

Required env vars in `application/proxy/.env`:

```
CF_DNS_API_TOKEN=<token>
```

Or alternatively:

```
CF_API_EMAIL=<email>
CF_API_KEY=<key>
```

## Rollout stages

1. **Stage 1**: LE staging CA for `vresume.structa.cloud`.
2. **Stage 2**: LE production CA for precis-ctc, structa-cloud, media, dashboard.
3. **Stage 3**: Delete `application/proxy/configs/traefik/dynamic/certs.yml`.

## Shared media

Nginx media server (`shared-proxy`) serves static/media files for all sites.

Media subdomains:

- `media.structa.cloud` (LMS site)
- `media.ctc-research.com` (CTC Research)
- `media.vresume.structa.cloud` (VResume)

## Commands

```bash
# Deploy proxy
cd application/proxy && make deploy

# Check certificate status
make cert-check

# Backup ACME store
cp application/proxy/configs/acme.json \
  application/proxy/data/backups/acme_$(date +%Y%m%d_%H%M%S).json
```
