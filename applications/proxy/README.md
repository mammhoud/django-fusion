# Proxy Infrastructure

`applications/proxy/` owns Traefik TLS termination, shared-media Nginx, Docus,
AFFiNE, and FileGator. Application services are independent of Coder
workspaces and use the external `common` and `warehouse-net` networks.

## Public routes

| Host/path | Service |
|---|---|
| `space.structa.cloud/` | AFFiNE web/API/WebSocket (`proxy-affine:3010`) |
| `space.structa.cloud/files/` | FileGator (`proxy-filegator:8080`) |
| `files.structa.cloud/` | FileGator alias |
| `docs.structa.cloud/` | Docus |
| `coder.structa.cloud/` | Coder control plane |
| `code.structa.cloud/` | Secure redirect to `coder.structa.cloud` |
| `blinko.structa.cloud` | Legacy redirect to `space.structa.cloud` |

`affine.pro` has no router or certificate request. The DNS provider must point
`space.structa.cloud`, `files.structa.cloud`, and `code.structa.cloud` at this
proxy host; Traefik requests the public certificates through the
`letsencrypt-http` resolver. `code.structa.cloud` redirects to the authenticated
Coder control plane rather than exposing a workspace code-server container.
External DNS/CNAME records cannot be created from this repository.

## Shared services

`docker-compose.nginx.yml` runs:

- `shared-media`, which serves static/media content and proxies the routes
  above;
- `docus`, the documentation server;
- `affine-migration`, a one-shot successful migration job;
- `proxy-affine`, the persistent AFFiNE server;
- `proxy-filegator`, the persistent FileGator file manager.

AFFiNE connects to `postgres` on `warehouse-net` and `default-redis` on
`common`. AFFiNE files live under `affine-data/`; FileGator's repository and
private configuration live under `filegator-data/`. These paths are ignored by
Git.

The shared-media healthcheck only tests Nginx syntax and `/health/`, so a
backend rollout does not incorrectly mark the proxy unhealthy. AFFiNE,
FileGator, and Docus have separate healthchecks.

## Required environment

Copy `.env.example` to `.env` and set unique values before starting the shared
stack:

```dotenv
AFFINE_DB_PASSWORD=<the password of the shared affine PostgreSQL role>
REDIS_PASSWORD=<the password of default-redis>
AFFINE_SERVER_EXTERNAL_URL=https://space.structa.cloud
```

Do not use repository defaults or commit `.env`. Keep the AFFiNE password
synchronized with the `affine` role created by the database bootstrap.

## Validation and startup

```bash
python3 applications/proxy/scripts/validate-traefik-config.py

docker compose \
  --env-file applications/proxy/.env \
  -f applications/proxy/docker-compose.nginx.yml config -q

docker compose \
  --env-file applications/proxy/.env \
  -f applications/proxy/docker-compose.nginx.yml up -d --build

docker ps --format 'table {{.Names}}\t{{.Status}}'
```

The migration container exiting with code 0 is expected. `shared-media`,
`proxy-affine`, and `proxy-filegator` should report healthy.

## Certificate operations

Traefik stores ACME state in `acme/acme.json`, which must remain mode 0600 and
is ignored by Git. Use the existing certificate scripts for backup and
inspection. Never commit ACME state, DNS API tokens, database passwords, or
FileGator private configuration.
