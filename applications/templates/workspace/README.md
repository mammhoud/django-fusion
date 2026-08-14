# workspace — Coder Template

Provisions one Coder agent-host container that bind-mounts the local Structa
Cloud checkout and starts its compose-based development container. The
workspace includes the full monorepo toolchain, VS Code Web, a web terminal,
and an authenticated Files app that points to the permanent shared FileGator
service. It does not provision AFFiNE, FileGator, or any application database.

## Access model

The shared proxy owns application services and public routing:

- `https://space.structa.cloud/` → permanent AFFiNE
- `https://space.structa.cloud/files/` → shared FileGator
- `https://files.structa.cloud/` → shared FileGator alias
- `https://coder.structa.cloud/` → Coder control plane

`blinko.structa.cloud` remains a legacy redirect to `space.structa.cloud`.
`affine.pro` is intentionally not routed or renewed. DNS records must point to
the proxy host outside this repository; Traefik requests the public
Let's Encrypt certificate for `space.structa.cloud` and `files.structa.cloud`.

The workspace Coder apps are authenticated through Coder. No workspace service
publishes a host port.

## Project source

The project directory is a read-write bind mount, not a clone:

- `host_repo_path` defaults to `/home/structa.cloud`.
- The host checkout is mounted at `/home/coder/structa.cloud`.
- The same checkout is mounted into the devcontainer at
  `/workspaces/structa.cloud`.
- Local edits and workspace edits are the same files, and Git operations work
  from either side.

The agent runs as root because the host checkout is root-owned. This avoids the
`npm install` EACCES failure on the bind mount.

## What the template provisions

The template creates one agent-host container with the Docker socket, a
persistent `/home/coder` volume, and the mounted repository. The
`devcontainers-cli` module and `coder_devcontainer` resource start only the
repository's `.devcontainer/docker-compose.yml`; that compose file now owns
only the development container.

The code-server module provides VS Code Web. VS Code Desktop is disabled in the
agent display. The Files Coder app connects to `proxy-filegator:8080` on the
shared `common` network.

## Prerequisites

The following infrastructure must already be running:

- Coder control plane
- PostgreSQL and Redis for shared applications
- Traefik and shared-media Nginx
- External Docker networks `common`, `traefik-net`, and `warehouse-net`
- Proxy credentials `AFFINE_DB_PASSWORD` and `REDIS_PASSWORD` supplied through
  `applications/proxy/.env` or the deployment environment

AFFiNE data is stored outside the workspace at
`applications/proxy/affine-data/`. FileGator data is stored at
`applications/proxy/filegator-data/repository/`; both paths are ignored by Git.

## Push and create

```bash
coder templates push \
  -d applications/templates/workspace \
  -m "Shared proxy services with mounted monorepo devcontainer" \
  -y workspace
```

Create a workspace from the pushed `workspace` template, then open VS Code Web
or Files from the Coder workspace page. AFFiNE and the public FileGator route
are independent of the workspace lifecycle.

## Validation

```bash
docker compose \
  --env-file applications/proxy/.env \
  -f applications/proxy/docker-compose.nginx.yml config -q

docker compose -f .devcontainer/docker-compose.yml config -q
terraform fmt -check applications/templates/workspace
python3 applications/proxy/scripts/validate-traefik-config.py
```

When validating without a local secrets file, provide redacted test values in
the command environment; never commit them.
