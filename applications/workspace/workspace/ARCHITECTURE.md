# workspace — Architecture

The `workspace` Coder template provisions one agent-host container and runs the
mounted repository's development container. AFFiNE is a shared proxy service,
not a workspace resource.

## Request flow

```text
browser
  │ https://space.structa.cloud/ → AFFiNE
  ▼
Traefik (:80/:443, Let's Encrypt)
  ▼
shared-proxy Nginx
  └─ / → proxy-affine:3010
```

The Coder workspace page separately exposes VS Code Web and the web terminal.
`coder.structa.cloud` routes to the Coder control plane, while
`code.structa.cloud` redirects to it. No workspace application port is
published on the host.

## Ownership boundaries

| Component | Owner | Persistence |
|---|---|---|
| Agent host and devcontainer | Coder template | Coder home volume and mounted checkout |
| AFFiNE server and migration | `applications/proxy/docker-compose.nginx.yml` | `applications/proxy/affine-data/` + shared `affine` database |
| PostgreSQL and Redis | `applications/databases/` | database volumes |
| Public TLS and routing | `applications/proxy/` | Traefik ACME storage |

Deleting or rebuilding a Coder workspace does not stop, recreate, or delete
AFFiNE.

## Workspace source and lifecycle

Terraform mounts `host_repo_path` (default `/home/structa.cloud`) at
`/home/coder/structa.cloud`. The devcontainer compose then mounts that folder
at `/workspaces/structa.cloud`. There is no clone. The Coder agent runs as root
to keep the root-owned bind mount writable for npm, Git, and build tools.

The `devcontainers-cli` module always installs the devcontainer CLI, so the
devcontainer is discovered automatically. Auto-start is opt-in via the
`devcontainer` parameter (default false); when disabled, the devcontainer can
be started manually from the Coder dashboard.

The devcontainer compose owns only:

- `devcontainer`, built from `.devcontainer/Dockerfile`;
- the external `common` network.

AFFiNE is deliberately absent from `.devcontainer/` and Terraform resources.
It is reached through the shared `space.structa.cloud` origin.

## Shared AFFiNE topology

`proxy-affine` and `proxy-affine-migration` attach to `common` and
`warehouse-net`. They use the shared `postgres` and `default-redis` services;
the credentials are required environment variables, not repository defaults.
The migration is a one-shot job and an exited-zero migration container is
expected. `proxy-affine` has an HTTP healthcheck on port 3010.

`shared-proxy` has an independent healthcheck: it validates Nginx syntax and
its local `/health/` endpoint. It does not become unhealthy merely because
Docus or AFFiNE is restarting.

## Routing and certificates

Traefik routes `space.structa.cloud` to `shared-proxy` and uses the
`letsencrypt-http` resolver for the public HTTPS router. Local `.localhost`
aliases do not request ACME certificates.

The public DNS provider must contain a record resolving the space host to the
proxy host. This repository configures the reverse proxy and certificate
request; it cannot create external DNS records or validate Cloudflare access
without credentials.

Legacy `blinko.structa.cloud` redirects to `space.structa.cloud`. The old
`affine.pro` and FileGator routes are absent by design.

## Validation

```bash
docker compose --env-file applications/proxy/.env \
  -f applications/proxy/docker-compose.nginx.yml config -q
docker compose -f .devcontainer/docker-compose.yml config -q
python3 applications/proxy/scripts/validate-traefik-config.py
terraform fmt -check applications/workspaces/workspace
```
