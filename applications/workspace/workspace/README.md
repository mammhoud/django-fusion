# workspace — Coder Template

Provisions one Coder agent-host container that bind-mounts the local Structa
Cloud checkout and starts its compose-based development container. The
workspace includes the full monorepo toolchain, VS Code Web, and a web
terminal. It does not provision AFFiNE, FileGator, or any application database.

## Access model

The shared proxy owns AFFiNE and public routing:

- `https://space.structa.cloud/` → permanent AFFiNE
- `https://coder.structa.cloud/` → Coder control plane
- `https://code.structa.cloud/` → secure redirect to Coder

`blinko.structa.cloud` remains a legacy redirect to `space.structa.cloud`.
`affine.pro` and FileGator routes are intentionally absent. DNS records must
point public hosts to the proxy outside this repository; Traefik requests the
Let's Encrypt certificates.

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
`devcontainers-cli` module always installs the devcontainer CLI, so the
repository's `.devcontainer` is discovered and can be started manually from the
dashboard. The `coder_devcontainer` resource only auto-starts it when the
`devcontainer` parameter is enabled (off by default).

The code-server module provides VS Code Web. VS Code Desktop is disabled in the
agent display.

## Prerequisites

The following infrastructure must already be running:

- Coder control plane
- PostgreSQL and Redis for shared AFFiNE
- Traefik and shared-proxy Nginx
- External Docker networks `common`, `traefik-net`, and `warehouse-net`
- Proxy credentials `AFFINE_DB_PASSWORD` and `REDIS_PASSWORD` supplied through
  `applications/proxy/.env` or the deployment environment

AFFiNE data is stored outside the workspace at
`applications/proxy/affine-data/`, which is ignored by Git.

## Push and create

```bash
coder templates push \
  -d applications/workspaces/workspace \
  -m "AFFiNE shared proxy with mounted monorepo devcontainer" \
  -y workspace
```

Create a workspace from the pushed `workspace` template, then open VS Code Web
from the Coder workspace page. Enable the `devcontainer` parameter to
auto-start the development container; otherwise start it manually from the
dashboard. AFFiNE is independent of the workspace lifecycle.

## Validation

```bash
docker compose \
  --env-file applications/proxy/.env \
  -f applications/proxy/docker-compose.nginx.yml config -q

docker compose -f .devcontainer/docker-compose.yml config -q
terraform fmt -check applications/workspaces/workspace
python3 applications/proxy/scripts/validate-traefik-config.py
```

When validating without a local secrets file, provide redacted test values in
the command environment; never commit them.
