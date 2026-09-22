# `configs/traefik/dynamic`

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

The live router table. Every file here is watched by Traefik and applied without
a restart. One file per site keeps ownership obvious and means a bad router can
be reverted by reverting a single file.

## Routing table

| File | Host(s) | Backend |
| --- | --- | --- |
| `catchall.yml` | `HostRegexp(.+)` at `priority: 1` | `noop@internal` — HTTP→HTTPS redirect, silent HTTPS noop |
| `notes.yml` | `notes.structa.cloud`, `notes.localhost` | `planinc:1111` (dedicated vhost, no path prefix) |
| `space.yml` | `space.structa.cloud`, `space.localhost` | `coder:7080` |
| `tools.yml` | `tools.structa.cloud`, `tools.localhost` | `tools-proxy:80` (nginx path splits, incl. `/notes/` → `blinko:1111`) |
| `xyops.yml` | `ops.structa.cloud`, `ops.localhost` | xyops |
| `docs.yml` | `docs.structa.cloud` | `docus:3000` |
| `precis-landing.yml` | `structa.cloud`, `www.structa.cloud` | `precis-main-frontend:3000` + `precis-main-backend:8074` |
| `lms-fusion.yml` | `lms.structa.cloud`, `precis-lms.localhost` | `precis-main-frontend:3000` + `precis-main-backend:8074` |
| `crm.yml` | `crm.structa.cloud` | loop-crm frontend shell + backend path |
| `ctc-research.yml` | `ctc-research.com`, `www.`, `arch.` | `precis-ctc` frontend + backend |
| `media-servers.yml` | `media.structa.cloud`, `media.ctc-research.com`, `media.vresume.structa.cloud` | static/media hosts |
| `precis-dev.yml.disabled` | `dev.structa.cloud` | parked — no DNS record exists, so the routers are disabled |
| `middlewares.yml` | — | shared middleware definitions (no router) |
| `certs.yml` | — | TLS stores and the default certificate (no router) |

## Contents

- `catchall.yml` - safe default for unmatched hosts
- `certs.yml` - TLS certificates and default store
- `crm.yml`, `ctc-research.yml`, `docs.yml`, `lms-fusion.yml`, `media-servers.yml`, `notes.yml`, `precis-landing.yml`, `space.yml`, `tools.yml`, `xyops.yml` - per-site routers
- `middlewares.yml` - shared middlewares
- `precis-dev.yml.disabled` - disabled site

## Public API

Middlewares defined in `middlewares.yml` and referenced by the routers:

- `redirect-to-https` — permanent scheme redirect
- `security-headers` — HSTS (2 years, preload), `nosniff`, `SAMEORIGIN`, referrer policy, permissions policy
- `compress`
- `csrf-headers` — forwards `X-Forwarded-Proto`
- `rate-limit` — 100/s average, 50 burst
- `basic-auth` — `admin` / `admin` (development gate)
- `redirect-www-to-root`

## Usage

```bash
# Add or edit a router, then validate and apply
make validate
make restart
```

## Conventions

- **Priority:** site routers use `150`; the catch-all deliberately uses `1` so it
  only ever matches what nothing else claimed.
- **Naming:** `<site>-http` / `<site>-https` for production, `<site>-local-http` /
  `<site>-local-https` for the `.localhost` twins.
- **Container names are resolved on the shared `common` network.** A backend that
  is not attached to `common` will 502 even though the router config is correct.
- Keep a site's `.localhost` host in the proxy Makefile's `LOCAL_CERT_SANS` list,
  or it will fall back to the default certificate and warn in the browser.
