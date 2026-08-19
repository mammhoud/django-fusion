# Proxy Infrastructure

`application/proxy/` owns Traefik TLS termination, shared-proxy Nginx, Docus,
and AFFiNE. AFFiNE is independent of Coder workspaces and uses the external
`common` and `warehouse-net` networks.

## Public routes

| Host/path | Service |
|---|---|
| `space.structa.cloud/` | AFFiNE web/API/WebSocket (`proxy-affine:3010`) |
| `docs.structa.cloud/` | Docus |
| `coder.structa.cloud/` | Coder control plane |
| `code.structa.cloud/` | Secure redirect to Coder |
| `blinko.structa.cloud` | Legacy redirect to `space.structa.cloud` |
| `crm.structa.cloud/` | Loop-CRM (frontend shell + backend path fallback) |
| `lms.structa.cloud/` | Precis LMS (`precis-lms` frontend + backend) |
| `ctc-research.com/` | CTC Research (`precis-ctc` frontend + backend) |
| `structa.cloud/`, `www.structa.cloud/` | Landing-Fusion (frontend + backend path fallback) |

`affine.pro` and FileGator hosts have no router or certificate request. The DNS
provider must point active public hosts at this proxy; Traefik requests public
certificates through the `letsencrypt-http` resolver. External DNS records
cannot be created from this repository.

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
  -f application/proxy/docker-compose.nginx.yml config -q

docker compose \
  --env-file application/proxy/.env \
  -f application/proxy/docker-compose.nginx.yml up -d --build

docker ps --format 'table {{.Names}}\t{{.Status}}'
```

The migration container exiting with code 0 is expected. `shared-proxy`,
`proxy-affine`, and `docus` should report healthy.

## Certificate operations

Traefik stores ACME state in `configs/acme.json`, which must remain mode 0600
and is ignored by Git. Use the existing certificate scripts for backup and
inspection. Never commit ACME state, DNS API tokens, database passwords, or
AFFiNE private configuration.
