# Proxy Infrastructure

`application/proxy/` owns Traefik TLS termination, shared-proxy Nginx, Docus,
and AFFiNE. AFFiNE is independent of Coder workspaces and uses the external
`common` and `warehouse-net` networks.

## Public routes

| Host/path | Service |
|---|---|
| `space.structa.cloud/` | Coder control plane (workspace origin) |
| `docs.structa.cloud/` | Docus |
| `tools.structa.cloud/space/` | AFFiNE (`proxy-affine:3010`, path-based) |
| `crm.structa.cloud/` | Loop-CRM (frontend shell + backend path fallback) |
| `lms.structa.cloud/` | Precis Main compatibility host (`precis-main-frontend` + `precis-main-backend`) |
| `ctc-research.com/` | CTC Research (`precis-ctc` frontend + backend) |
| `structa.cloud/`, `www.structa.cloud/` | Precis Main public host (`precis-main-frontend` + `precis-main-backend`) |

`coder.structa.cloud` and `code.structa.cloud` are retired aliases; the
workspace control plane is served at `space.structa.cloud`. `affine.pro` and
FileGator hosts have no router or certificate request. The DNS
provider must point active public hosts at this proxy; Traefik requests public
certificates through the `letsencrypt-http` resolver. External DNS records
cannot be created from this repository.

## Precis Main routing contract

The historical `precis-landing` and `lms-fusion` router files are compatibility
identities for the unified Precis product. Their load-balancer targets are:

| Router file | Backend target | Frontend target | Backend health check |
|---|---|---|---|
| `configs/traefik/dynamic/precis-landing.yml` | `http://precis-main-backend:8074` | `http://precis-main-frontend:3000` | `/apis/pages/` |
| `configs/traefik/dynamic/lms-fusion.yml` | `http://precis-main-backend:8074` | `http://precis-main-frontend:3000` | `/apis/pages/` |

The admin paths are backend-owned on both public hosts:

- `/admin` → `/admin/` → Wagtail login
- `/django-admin` → `/django-admin/` → Django admin login

Validate the proxy and deploy the application from the repository root:

```bash
python3 application/proxy/scripts/validate-traefik-config.py
docker compose --env-file application/proxy/.env \
  -f application/proxy/docker-compose.yml config -q
docker compose --env-file .env \
  -f projects/precis/precis-main/docker-compose.yml up -d --build
```

See [`../../docs/dev/infrastructure/precis-main-proxy-admin.md`](../../docs/dev/infrastructure/precis-main-proxy-admin.md)
for the full request lifecycle, health checks, smoke tests, and rollback notes.

## Shared services

`docker-compose.nginx.yml` runs:

- `shared-proxy`, which serves static/media content and proxies the routes
  above;
- `docus`, the documentation server;
- `affine-migration`, a one-shot successful migration job;
- `proxy-affine`, the persistent AFFiNE server.

AFFiNE connects to `postgres` on `warehouse-net` and `default-redis` on
`common`. AFFiNE files live under `affine-data/`, which is ignored by Git.

The shared-proxy healthcheck tests Nginx syntax and `/health/`, so a backend
rollout does not incorrectly mark the proxy unhealthy. AFFiNE and Docus have
separate healthchecks.

## Required environment

Copy `.env.example` to `.env` and set unique values before starting the shared
stack:

```dotenv
# PostgreSQL URI value: percent-encode reserved characters such as @ -> %40.
AFFINE_DB_PASSWORD=<URL-encoded password of the shared affine PostgreSQL role>
REDIS_PASSWORD=<the password of default-redis>
AFFINE_SERVER_EXTERNAL_URL=https://space.structa.cloud
```

Do not use repository defaults or commit `.env`. Keep the decoded AFFiNE
password synchronized with the `affine` role created by the database bootstrap;
only the URI-encoded form belongs in `AFFINE_DB_PASSWORD`.

## Validation and startup

```bash
python3 application/proxy/scripts/validate-traefik-config.py

docker compose \
  --env-file application/proxy/.env \
  -f application/tools/docker-compose.nginx.yml config -q

docker compose \
  --env-file application/proxy/.env \
  -f application/tools/docker-compose.nginx.yml up -d --build

docker ps --format 'table {{.Names}}\t{{.Status}}'
```

The migration container exiting with code 0 is expected. `shared-proxy`,
`proxy-affine`, and `docus` should report healthy.

## Certificate operations

Traefik stores ACME state in `configs/acme.json`, which must remain mode 0600
and is ignored by Git. Use the existing certificate scripts for backup and
inspection. Never commit ACME state, DNS API tokens, database passwords, or
AFFiNE private configuration.

## Remarks & Notes

- The router/service identifiers may still contain historical Precis Landing or
  LMS names; only the target URLs define the active Precis Main containers.
- A running proxy cannot make an absent application stack healthy; deploy
  `projects/precis/precis-main/docker-compose.yml` before diagnosing a 503 as a
  routing defect.
- ACME/DNS failures for unrelated configured hosts should be handled as
  separate certificate operations.
