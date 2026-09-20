# Proxy Infrastructure

`application/proxy/` owns Traefik TLS termination and the tools-proxy and assets-proxy Nginx pair
front door. Self-hosted tools (Coder, Blinko, Mailpit) and the tools-proxy / assets-proxy
(Nginx) now live under `application/tools/` — see `application/tools/README.md`.

## Public routes

| Host/path | Service | Container(s) |
|---|---|---|
| `space.structa.cloud/` | Coder control plane | `coder:7080` |
| `docs.structa.cloud/` | Docus | `docus:3000` |
| `notes.structa.cloud/` | PlanInc | `planinc:1111` (dedicated vhost, no path prefix) |
| `tools.structa.cloud/notes/` | Blinko | `blinko:1111` (path-based) |
| `tools.structa.cloud/` | Tools navigation + proxy | `tools-proxy:80` |
| `structa.cloud/`, `www.structa.cloud/` | Precis Main | `precis-main-backend:8074` + `precis-main-frontend:3000` |
| `dev.structa.cloud/` | Precis Dev (development) | `precis-dev-backend:8074` + `precis-dev-frontend:3000` |
| `lms.structa.cloud/` | Precis Main (compatibility) | `precis-main-backend:8074` + `precis-main-frontend:3000` |
| `ctc-research.com/` | CTC Research | `precis-ctc` frontend + backend |
| `crm.structa.cloud/` | Loop-CRM | frontend shell + backend path |

## Precis Main routing contract

The historical `precis-landing` and `lms-fusion` router files are compatibility
identities for the unified Precis product. Their load-balancer targets are:

| Router file | Backend target | Frontend target |
|---|---|---|
| `configs/traefik/dynamic/precis-landing.yml` | `precis-main-backend:8074` | `precis-main-frontend:3000` |
| `configs/traefik/dynamic/precis-dev.yml` | `precis-dev-backend:8074` | `precis-dev-frontend:3000` |

## Shared services

`docker-compose.nginx.yml` (under `application/tools/`) runs the `tools-proxy`
which serves static/media content and proxies tools.structa.cloud subpaths.

PostgreSQL and Redis are managed by `application/databases/`. Every service
including Coder and Blinko connects to the single shared `postgres` container.

## Required environment

Copy `.env.example` to `.env` and set unique values. Database credentials live
in `application/databases/.env`; Blinko and tool secrets are in
`application/tools/.env`. The repo-root `.env` fills gaps.

## Validation and startup

```bash
python3 application/proxy/scripts/validate-traefik-config.py

# Full stack
docker compose -f application/docker-compose.yml config -q
docker compose -f application/docker-compose.yml up -d --build

# Proxy only
docker compose -f application/proxy/docker-compose.yml config -q
docker compose -f application/proxy/docker-compose.yml up -d
```

## Certificate operations

Traefik stores ACME state in `configs/acme.json`, which must remain mode 0600
and is ignored by Git. Use the existing certificate scripts for backup and
inspection. Never commit ACME state, DNS API tokens, or database passwords.

## Remarks & Notes

- The router/service identifiers may still contain historical Precis Landing or
  LMS names; only the target URLs define the active Precis Main containers.
- A running proxy cannot make an absent application stack healthy; deploy
  `projects/structa.cloud/docker-compose.yml` before diagnosing a 503.
- ACME/DNS failures for unrelated configured hosts should be handled as
  separate certificate operations.