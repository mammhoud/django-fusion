# Package Guide (PX-001)

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

This directory owns **TLS termination and host-based routing** for every
`*.structa.cloud` site. It does not own the applications behind it — each site's
own repository does.

## What lives here

| Path | Role |
| --- | --- |
| `docker-compose.yml` | Composes the Traefik stack (and the tools-proxy nginx include) |
| `docker-compose.traefik.yml` | The `default-proxy` service — ports 80/443, mounts, health check |
| `Dockerfile` | `traefik:latest` + `curl` + `apache2-utils`, static config baked in |
| `configs/` | All configuration — see [`configs/README.md`](../configs/README.md) |
| `scripts/` | Operational tooling — see [`scripts/README.md`](../scripts/README.md) |
| `data/` | Runtime state: certs, ACME backups (gitignored) |
| `Makefile` | The supported entrypoint for every operation |
| `LETSENCRYPT.md` | Certificate issuance runbook |

## What lives elsewhere

| Concern | Owner |
| --- | --- |
| The tools-proxy/assets-proxy nginx pair | `application/tools/` |
| PostgreSQL, Redis | `application/databases/` |
| Each `*.structa.cloud` application | its own directory / repo |
| The `planinc` container behind `notes.structa.cloud` | the PlanInc repo |

## Where do I change something?

| I want to change… | Edit | Then |
| --- | --- | --- |
| Which backend a host points at | `configs/traefik/dynamic/<site>.yml` | `make validate && make restart` |
| Add a new site | a new `<site>.yml` | `make validate`, DNS, `make proxy-dns-check` |
| Entrypoints or the ACME resolver | `configs/traefik/dynamic.yml` | `make up` (recreate, not reload) |
| Shared headers / compression | `configs/traefik/dynamic/middlewares.yml` | `make validate && make restart` |
| `.localhost` dev certificate SANs | `Makefile` (`LOCAL_HOSTS`, `LOCAL_CERT_SANS`) | `make proxy-certs-selfsigned` |
| A check or gate | `scripts/*.py` + a `Makefile` target | run it |

## Consumers

- **Operators** use `make help`, `make validate`, `make restart`.
- **Deploy gates** — `make deploy` runs `proxy-validate` first, so a broken config
  cannot be rolled out.
- **The applications** rely on this stack resolving their container by name on the
  shared `common` network.

## Prerequisites

| Requirement | Why |
| --- | --- |
| External networks `traefik-net` and `common` | Declared `external: true`; compose will not create them |
| DNS A records → this host | HTTP-01 validation resolves them |
| No off-host `AAAA` record | Let's Encrypt prefers IPv6 and will fail validation |
| `configs/acme.json` at mode `0600` | ACME storage must exist before first start |

## Related

- [`PX-002`](./01-architecture.md) — architecture
- [`PX-003`](./02-routing.md) — routing
- [`PX-004`](./03-certificates.md) — certificates
- [`PX-005`](./04-operations.md) — operations
