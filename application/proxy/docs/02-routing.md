# Routing (PX-003)

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

One file per site under `configs/traefik/dynamic/`. No file knows about another;
anything shared lives in `middlewares.yml`.

## The host table

| Host | Backend | File |
| --- | --- | --- |
| `notes.structa.cloud` | `planinc:1111` (dedicated vhost, no path prefix) | `notes.yml` |
| `space.structa.cloud` | `coder:7080` | `space.yml` |
| `tools.structa.cloud` | `tools-proxy:80` (nginx path splits, incl. `/notes/` → `blinko:1111`) | `tools.yml` |
| `ops.structa.cloud` | xyops | `xyops.yml` |
| `docs.structa.cloud` | `docus:3000` | `docs.yml` |
| `structa.cloud`, `www.structa.cloud` | `precis-main-frontend:3000` + `precis-main-backend:8074` | `precis-landing.yml` |
| `lms.structa.cloud` | Precis Main (compatibility identity) | `lms-fusion.yml` |
| `crm.structa.cloud` | loop-crm frontend shell + backend path | `crm.yml` |
| `ctc-research.com`, `www.`, `arch.` | `precis-ctc` frontend + backend | `ctc-research.yml` |
| `media.structa.cloud`, `media.ctc-research.com`, `media.vresume.structa.cloud` | static/media hosts | `media-servers.yml` |
| *unmatched* | `noop@internal` | `catchall.yml` |
| `dev.structa.cloud` — **parked** | `precis-dev-*` | `precis-dev.yml.disabled` |

`www.crm.structa.cloud` is not in DNS and is not routed.

## Priorities

| Priority | Used by | Rationale |
| --- | --- | --- |
| `1` | `catchall.yml` | Matches `HostRegexp(.+)` so it must lose to everything |
| `150` | every site router | Wins over the catch-all; ties between sites cannot occur because rules are host-specific |

If a request reaches the catch-all on HTTPS it receives a silent `noop@internal`
response — by design, so unknown hosts do not leak an error page.

## Naming

| Router | Convention |
| --- | --- |
| Production | `<site>-http`, `<site>-https` |
| Local twins | `<site>-local-http`, `<site>-local-https` |

Local twins exist so `notes.localhost`, `space.localhost`, `tools.localhost` and
`ops.localhost` work without touching DNS. `precis-lms.localhost` is the legacy
name kept for compatibility.

## Middlewares

Defined once in `middlewares.yml`, referenced by name:

`redirect-to-https`, `security-headers`, `compress`, `csrf-headers`,
`rate-limit`, `basic-auth`, `redirect-www-to-root`.

A typical site router composes `redirect-to-https` on the `web` entrypoint and
`compress` + `security-headers` on `web-secure`.

## Adding a site

1. Confirm the backend joins the **`common`** network — otherwise it will 502.
2. Add the DNS record (A → this host; **no off-host AAAA**).
3. Create `configs/traefik/dynamic/<site>.yml` modelled on `notes.yml`:
   HTTP→HTTPS redirect, HTTPS router with `certResolver: letsencrypt-http`,
   `compress` + `security-headers`, `priority: 150`, health check.
4. Add the `.localhost` twin if useful, and add that host to the Makefile's
   `LOCAL_CERT_SANS` — otherwise it gets the default certificate and warns.
5. `make validate` (fails on a dangling service or middleware reference).
6. `make proxy-dns-check` **before** expecting a certificate.
7. `make restart`, then `make proxy-site-check` to confirm status **and** that the
   host serves a real certificate covering its own name.
8. Add a row to the README route table and to this table.

## Related

- [`PX-004`](./03-certificates.md) — certificates and the DNS gate
- [`PX-006`](./05-validation-and-health-checks.md) — the checks in detail
