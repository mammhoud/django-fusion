# Coder Templates
# workspace — Coder Template

Provisions one Coder agent-host container that bind-mounts the local Structa
Cloud checkout and starts its compose-based development container. The workspace
includes the full monorepo toolchain, VS Code Web, and a web
terminal. It does not provision Blinko, FileGator, or any application database.

## Access model

The shared proxy owns public routing:

- `https://space.structa.cloud/` → Coder control plane (workspace origin)
- `https://tools.structa.cloud/notes/` → Blinko (path-based)

`coder.structa.cloud`, `code.structa.cloud`, and `blinko.structa.cloud` are
retired aliases. FileGator routes are intentionally absent.
DNS records must point public hosts to the proxy outside this repository;
Traefik requests the Let's Encrypt certificates.

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
agent display. A `filebrowser` module adds a web-based File Browser over the
same mounted workspace folder, ordered after VS Code Web in the dashboard apps.

## Prerequisites

The following infrastructure must already be running:

- Coder control plane
- PostgreSQL and Redis for the platform's shared services
- Blinko's dedicated `blinko-db` PostgreSQL service
- Traefik and tools-proxy + assets-proxy Nginx
- External Docker networks `common`, `traefik-net`, and `warehouse-net`
- Proxy credentials `BLINKO_DB_PASSWORD` supplied through
  `application/proxy/.env` or the deployment environment

Blinko data is stored outside the workspace at
`application/tools/blinko/blinko-data/`, which is ignored by Git.

## Push and create

```bash
coder templates push \
  -d application/workspaces/workspace \-m "Shared proxy with mounted monorepo devcontainer"
 \
  -y workspace
```

Create a workspace from the pushed `workspace` template, then open VS Code Web
from the Coder workspace page. Enable the `devcontainer` parameter to
auto-start the development container; otherwise start it manually from the
dashboard. Blinko is independent of the workspace lifecycle.

## Validation

```bash
docker compose \
  --env-file application/tools/blinko/.env \
  -f application/tools/docker-compose.yml config -q

docker compose -f .devcontainer/docker-compose.yml config -q
terraform fmt -check application/workspaces/workspace
python3 application/proxy/scripts/validate-traefik-config.py
```

When validating without a local secrets file, provide redacted test values in
the command environment; never commit them.

Terraform templates for [Coder](https://coder.com) workspaces. There is a
single active `workspace` template that provides a mounted monorepo development
environment **and** installs the base toolchain on start (git + make + Node.js +
Nx + the Freebuff client). Blinko runs independently in the shared tools stack.

## Templates

| Template | Provisioned workspace | Shared application route |
|---|---|---|
| [workspace](./workspace/README.md) | Agent host + base toolchain (git/make/Node/Nx), optional devcontainer, VS Code Web, File Browser, web terminal | Blinko at `tools.structa.cloud/notes/` |

## workspace

The template bind-mounts the local checkout (`host_repo_path`, default
`/home/structa.cloud`) instead of cloning it. The same files are visible on
the host, in the Coder agent host, and in the devcontainer. The agent runs as
root so npm and Git can write to the root-owned checkout.

On every workspace start, an idempotent `coder_script` installs the base
toolchain (`git`, `make`, Node.js, and `npm install -g freebuff`) directly in
the agent-host container — so the toolchain is available even before (or
without) the devcontainer. This absorbs the former `toolchain` template.

The `devcontainers-cli` module always installs the devcontainer CLI, and
`coder_devcontainer` auto-starts `.devcontainer/docker-compose.yml` only when
the `devcontainer` parameter is enabled (off by default); it can otherwise be
started manually from the dashboard. Blinko is not installed by or stopped with
a workspace; it is a permanent service in
`application/tools/docker-compose.yml` using its dedicated PostgreSQL service
and proxy-owned persistent data.

The Coder template disables VS Code Desktop and provides VS Code Web plus a
web-based File Browser (both serve the mounted workspace folder). Antigravity
is not included because no runnable image or supported deployment contract was
specified.

## Shared infrastructure

| Component | Defined in |
|---|---|
| PostgreSQL + Redis | `application/databases/docker-compose.yml` |
| Coder control plane | `application/docker-compose.yml` |
| Blinko + tools-proxy | `application/tools/docker-compose.yml` |
| Docus | `docs/docker-compose.yml` |
| Blinko routing | `application/proxy/configs/traefik/dynamic/tools.yml` |
| Code/Coder routing | `application/proxy/configs/traefik/dynamic/code.yml` and `coder.yml` |
| Docker networks | `common`, `traefik-net`, `warehouse-net` |

## Quick start

```bash
cd application/databases
docker compose up -d postgres default-redis

cd ../tools
# Set BLINKO_DB_PASSWORD in blinko/.env first.
docker compose --env-file blinko/.env -f docker-compose.yml up -d

cd ../proxy
docker compose -f docker-compose.traefik.yml up -d

cd ../..
coder templates push \
  -d application/workspaces/workspace \
  -m "Shared proxy with mounted monorepo devcontainer + toolchain" \
  -y workspace
```

## File layout

```text
application/workspace/
├── README.md
└── workspace/
    ├── main.tf
    ├── README.md
    └── ARCHITECTURE.md

.devcontainer/
├── Dockerfile
├── docker-compose.yml       # development container only
└── devcontainer.json

application/tools/
├── docker-compose.yml       # tools-proxy + Docus + Blinko
├── blinko/                  # Blinko service + data
└── nginx/default.conf.template
```
