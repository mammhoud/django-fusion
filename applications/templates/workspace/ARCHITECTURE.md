# workspace — Architecture

The `workspace` Coder template provisions one agent-host container and runs the
mounted repository's development container. Shared application services are
not workspace resources.

## Request flow

```text
browser
  │ https://space.structa.cloud/       → AFFiNE
  │ https://space.structa.cloud/files/ → FileGator
  ▼
Traefik (:80/:443, Let's Encrypt)
  ▼
shared-media Nginx
  ├─ /             → proxy-affine:3010
  ├─ /files/       → proxy-filegator:8080
  └─ files.structa.cloud → proxy-filegator:8080
```

The Coder workspace page separately exposes VS Code Web and Files as
authenticated Coder apps. `coder.structa.cloud` routes to the Coder control
plane. No workspace application port is published on the host.

## Ownership boundaries

| Component | Owner | Persistence |
|---|---|---|
| Agent host and devcontainer | Coder template | Coder home volume and mounted checkout |
| AFFiNE server and migration | `applications/proxy/docker-compose.nginx.yml` | `applications/proxy/affine-data/` + shared `affine` database |
| FileGator | `applications/proxy/docker-compose.nginx.yml` | `applications/proxy/filegator-data/repository/` |
| PostgreSQL and Redis | `applications/databases/` | database volumes |
| Public TLS and routing | `applications/proxy/` | Traefik ACME storage |

Deleting or rebuilding a Coder workspace does not stop, recreate, or delete
AFFiNE or FileGator.

## Workspace source and lifecycle

Terraform mounts `host_repo_path` (default `/home/structa.cloud`) at
`/home/coder/structa.cloud`. The devcontainer compose then mounts that folder
at `/workspaces/structa.cloud`. There is no clone. The Coder agent runs as root
to keep the root-owned bind mount writable for npm, Git, and build tools.

The devcontainer compose owns only:

- `devcontainer`, built from `.devcontainer/Dockerfile`;
- the external `common` network.

AFFiNE and FileGator are deliberately absent from `.devcontainer/` and from
Terraform resources. The template's Files app points to the shared
`proxy-filegator` service, while AFFiNE is reached through its public shared
origin.

## Shared service topology

`proxy-affine` and `proxy-affine-migration` attach to `common` and
`warehouse-net`. They use the shared `postgres` and `default-redis` services;
the credentials are required environment variables, not repository defaults.
The migration is a one-shot job and an exited-zero migration container is
expected. `proxy-affine` has an HTTP healthcheck on port 3010.

`proxy-filegator` attaches to `common`, stores its repository under the proxy
application directory, and has an HTTP healthcheck on port 8080.

`shared-media` has an independent healthcheck: it validates Nginx syntax and
its local `/health/` endpoint. It does not become unhealthy merely because
Docus or an application backend is restarting.

## Routing and certificates

Traefik routes `space.structa.cloud` and `files.structa.cloud` to
`shared-media` and uses the `letsencrypt-http` resolver for the public HTTPS
routers. Local `.localhost` aliases do not request ACME certificates.

The public DNS provider must contain records resolving these names to the
proxy host. This repository configures the reverse proxy and certificate
requests; it cannot create external DNS records or validate Cloudflare access
without credentials.

Legacy `blinko.structa.cloud` redirects to `space.structa.cloud`. The old
`affine.pro` route is absent by design.

## Validation

```bash
docker compose --env-file applications/proxy/.env \
  -f applications/proxy/docker-compose.nginx.yml config -q
docker compose -f .devcontainer/docker-compose.yml config -q
python3 applications/proxy/scripts/validate-traefik-config.py
terraform fmt -check applications/templates/workspace
```
