# workspace — Coder Template

Provisions ONE Coder workspace container (agent host) that runs the repository's
compose devcontainer inside it. The devcontainer (`.devcontainer/`) provides the
full monorepo toolchain — the browser editor (VS Code Web, a code-server
`coder_app`) and VS Code desktop both attach to it — and includes an AFFiNE
workspace service connected to the shared PostgreSQL and Redis services over
the same `common` / `warehouse-net` networks used by the rest of the platform.
No separate code-server or FileGator *service* is bundled; the editor app runs
in the workspace container.

## Access model

The only public route is `space.structa.cloud`, served by the shared-media
nginx:

- `space.structa.cloud/` → AFFiNE (web client + API + WebSocket on port 3010)

Legacy `blinko.structa.cloud` 301-redirects to `space.structa.cloud`. The
public `affine.pro` and `filegator.structa.cloud` hosts were removed entirely.
The editor is **VS Code Web** (browser): the `code-server` module installs
code-server in the agent-host container and registers it as a Coder app
(`display_apps` disables the VS Code Desktop button — `vscode = false`). The
web terminal and SSH/port-forwarding helpers remain. No host port is published
by the template; Coder app proxying and the shared-media nginx handle all
access.

| Coder app | Runs in | Endpoint |
|---|---|---|
| AFFiNE Workspace | devcontainer service `coder-workspace-affine` | `http://coder-workspace-affine:3010` |
| VS Code Web (code-server) | agent-host container | `http://localhost:13337` (via Coder app) |

## Project source (cloned, not mounted)

The project directory is a **fresh `git clone`** performed by the `git-clone`
module at workspace start — **not** a bind mount of a local directory. The
clone lives in the agent-host container's persistent home volume at
`/home/coder/structa.cloud` (from `repo_url`), which survives restarts. There
are no host-path mounts in the Terraform for the project source; the only
mounts are the named home volume, the Docker socket, and (inside the
devcontainer) the same cloned folder bind-mounted by the devcontainer CLI, so
the browser editor, the devcontainer, and AFFiNE's data all share one copy of
the source. Set `repo_url` to your fork when the repo is private so the clone
uses your authenticated GitHub identity.

## Workspace name constraint

The devcontainer compose pins the AFFiNE service container name to
`coder-<workspace_name>-affine`; the shared-media nginx resolves the same
prefix from its `WORKSPACE_NAME` env var via an envsubst template
(`applications/proxy/nginx/default.conf.template`). Both default to
`workspace` — keep them in sync when overriding.

## Devcontainer (docker-devcontainer pattern)

The template follows the
[docker-devcontainer reference template](https://registry.coder.com/templates/coder/docker-devcontainer):
on start it installs the devcontainer CLI, clones the repository from
`repo_url` (default: the Structa Cloud monorepo) into the persistent home
volume, and auto-starts the repository's compose devcontainer through
`coder_devcontainer`. The `code-server` module opens that same folder in the
browser editor. The agent-host container mounts the host Docker socket, so the
devcontainer stack (including the AFFiNE containers) is created on the shared
host daemon where the proxy can reach it — no privileged Docker-in-Docker
needed.

The devcontainer itself is compose-based:

- `.devcontainer/docker-compose.yml` — `devcontainer` (toolchain, built from
  `.devcontainer/Dockerfile`) + `affine` with a one-shot `affine_migration`
  job. Services attach to the external `common` (proxy + Redis reachability)
  and `warehouse-net` (AFFiNE → shared `postgres`) networks.
- `.devcontainer/devcontainer.json` — `dockerComposeFile: docker-compose.yml`,
  `service: devcontainer`, docker-in-docker feature, remote user `node`.

AFFiNE uses the shared `postgres` service (`affine` database created by the
databases bootstrap) and the shared authenticated `default-redis` service.
Persistent data lives under the cloned repo: `.affine-data-<workspace_name>/`
(`storage` + `config`).

Set `repo_url` when creating the workspace to point at any repository that
contains a `devcontainer.json` + `docker-compose.yml`.

## Prerequisites

| Dependency | Provided by | Notes |
|---|---|---|
| PostgreSQL | `applications/databases/docker-compose.yml` | Shared `postgres`; creates `affine` on a new volume |
| Redis | `applications/databases/docker-compose.yml` | Shared `default-redis`, password protected |
| Coder | `applications/docker-compose.yml` | Template server |
| Traefik + nginx | `applications/proxy/docker-compose.yml` | `space.structa.cloud` routing for this template |
| `common` and `warehouse-net` | Infrastructure deployment | Must already exist as external Docker networks |

Verify the prerequisites without creating or changing services:

```bash
docker network inspect common warehouse-net
docker ps --filter "name=postgres" --filter "name=default-redis" \
  --filter "name=coder" --filter "name=shared-media"
```

For a new PostgreSQL volume, the database bootstrap creates the `affine`
database and role from `INITDB_MULTIPLE_DATABASES`. Existing volumes do not
rerun initialization automatically; create the database and role using the
normal database maintenance procedure before provisioning the workspace.

## First run

```bash
# Push the template
coder templates push workspace \
  --directory applications/templates/workspace

# Create the workspace (any name works; containers use workspace_name)

# Inspect the workspace containers
docker ps --filter "name=coder-workspace" \
  --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

The `Ports` column should be empty for the workspace containers. Coder's
authenticated app proxy and the shared-media nginx handle access.

## Networks

```text
                         ┌──────────────────────────┐
                         │ Coder authenticated apps │
                         └─────────────┬────────────┘
                                       │
                    common ───────────┼────────── warehouse-net
                       │               │                    │
            devcontainer (toolchain)   │            postgres
            AFFiNE                AFFiNE             affine DB
```

- `common`: devcontainer services, Redis, shared-media, and the agent-host
  container.
- `warehouse-net`: AFFiNE to the shared PostgreSQL service.
- No AFFiNE host port is published.
- Public access is `space.structa.cloud` (root = AFFiNE) through the
  shared-media nginx.

## Terraform variables

| Variable | Default | Purpose |
|---|---|---|
| `docker_network` | `common` | Shared network for the agent-host container + devcontainer services |
| `database_network` | `warehouse-net` | External network attached to the shared PostgreSQL service |
| `coder_host_ip` | `172.18.0.16` | Coder server address for the agent binary download |
| `workspace_name` | `workspace` | Container name suffix; must match nginx `WORKSPACE_NAME` |

AFFiNE versions/passwords are configured in the devcontainer compose
(`.devcontainer/docker-compose.yml`, env-overridable) rather than as template
variables.

## Related files

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the routing chain and naming
contract.

```text
applications/
├── templates/workspace/main.tf          # single agent-host container + coder_devcontainer
├── ../.devcontainer/docker-compose.yml  # devcontainer stack: toolchain + AFFiNE
├── ../.devcontainer/devcontainer.json   # compose-based devcontainer config
├── ../.devcontainer/Dockerfile          # devcontainer toolchain image
├── proxy/nginx/default.conf.template    # space.structa.cloud (root = AFFiNE) + legacy redirects (envsubst)
├── proxy/traefik/dynamic/space.yml      # space.structa.cloud → shared-media (main route)
├── proxy/traefik/dynamic/blinko.yml     # legacy blinko host → root redirect
├── databases/docker-compose.yml         # PostgreSQL + Redis (affine DB)
└── docker-compose.yml                   # Coder control plane
```
