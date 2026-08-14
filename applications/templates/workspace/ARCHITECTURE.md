# workspace — Architecture

The `workspace` Coder template provisions ONE agent-host container that runs
the repository's compose devcontainer inside it. The devcontainer provides the
full monorepo toolchain (browser editor VS Code Web via the code-server
module, plus VS Code desktop attach) and bundles the AFFiNE workspace service,
exposed at `space.structa.cloud`. This document describes the container
topology, naming contract, and routing chain.

## Request flow

```text
browser
  │  https://space.structa.cloud  (root = AFFiNE)
  ▼
Traefik (default-proxy, :80/:443, Let's Encrypt)
  │  dynamic router: space.yml → shared-media:80
  ▼
shared-media nginx (nginx/default.conf.template, envsubst)
  │  server_name space.localhost space.structa.cloud
  │    / → coder-<workspace_name>-affine:3010 (WebSocket upgrade)
  ▼
devcontainer service container on the `common` Docker network
  • coder-<workspace_name>-affine   (AFFiNE: web + API + WS, one origin)
```

Legacy `blinko.structa.cloud` still routes to shared-media (Traefik
`blinko.yml`) but nginx responds with a 301 to the consolidated origin, so old
bookmarks keep working while the cert stays valid. The public `affine.pro` and
`filegator.structa.cloud` hosts were removed entirely.

No workspace container publishes a host port; the editor is **VS Code Web**
(code-server `coder_app` in the agent-host container, `display_apps` sets
`vscode = false` to drop the VS Code Desktop button) plus the web terminal.

## Project source (cloned, not mounted)

The project directory is a **fresh `git clone`** by the `git-clone` module at
workspace start — **not** a bind mount of a local directory. The clone lives
in the agent-host container's persistent home volume at
`/home/coder/<repo>` (from `repo_url`) and survives restarts. Terraform mounts
no host path for the project: the only mounts are the named home volume and
the Docker socket. The devcontainer CLI bind-mounts that same cloned folder
into the devcontainer, and code-server opens it directly — one copy of the
source shared by the browser editor, the devcontainer, and AFFiNE's
`.affine-data-*` directory.

## Template container (agent host)

`main.tf` provisions a single `coder-<workspace-id>-workspace` container from
the prebuilt `codercom/enterprise-node:ubuntu` image (docker CLI + compose
plugin + git + curl + node — the same image the `devcontainer` template uses;
no build step in the template). It:

- mounts the host Docker socket (`/var/run/docker.sock`) and a persistent
  home volume (`/home/coder`),
- downloads and runs the Coder agent (over plain HTTP from `coder_host_ip`
  because the HTTPS access URL serves a broken cert),
- attaches to `common` so the Coder app can reach the AFFiNE service by name.

The container name embeds the workspace ID so concurrent workspaces never
collide (unlike the devcontainer service containers, which are pinned for the
proxy). No code-server / FileGator / AFFiNE image or container is defined in
the template — AFFiNE lives in the devcontainer compose.

## Devcontainer (docker-devcontainer pattern)

On start the template installs the devcontainer CLI (devcontainers-cli
module), clones the repository from the `repo_url` parameter (git-clone
module, default: the Structa Cloud monorepo), installs the browser editor
(code-server module, folder = the same clone), then auto-starts the
repository's devcontainer via `coder_devcontainer`:

```text
start ──► devcontainers-cli module ──► git-clone module
   │                                       │
   └──────────► coder_devcontainer ────────┘
                   workspace_folder = /home/coder/<repo>
                   → docker compose -f .devcontainer/docker-compose.yml up
```

The devcontainer is **compose-based**:

- `.devcontainer/docker-compose.yml` — `devcontainer` (full toolchain, built
  from `.devcontainer/Dockerfile`, docker-in-docker feature applied) and
  `affine` (`ghcr.io/toeverything/affine`) with a one-shot `affine_migration`
  job.
- `.devcontainer/devcontainer.json` — `dockerComposeFile: docker-compose.yml`,
  `service: devcontainer`, `remoteUser: node`.

The agent-host container mounts the host Docker socket, so the devcontainer
CLI creates the stack on the shared host daemon where the proxy and Coder app
can reach it — no privileged Docker-in-Docker needed.

## Container topology

| Container | Image | Port | Networks | Public path |
|---|---|---|---|---|
| `coder-<workspace-id>-workspace` | `codercom/enterprise-node:ubuntu` (prebuilt) | — (code-server :13337 via Coder app) | `common` | none (agent host) |
| `coder-<workspace_name>-affine-migration` | `ghcr.io/toeverything/affine` | — (one-shot) | `common`, `warehouse-net` | none |
| `coder-<workspace_name>-affine` | `ghcr.io/toeverything/affine` | 3010 | `common`, `warehouse-net` | `space.structa.cloud/` |

`warehouse-net` is the external network shared with PostgreSQL; the AFFiNE
containers attach to it for database access. Everything else uses `common`, the
shared network that also hosts Redis and shared-media.

## AFFiNE provisioning

AFFiNE's official self-host deployment is a single image
(`ghcr.io/toeverything/affine`) plus a one-shot migration job; the devcontainer
compose mirrors the official compose:

- `affine_migration` runs `node ./scripts/self-host-predeploy.js` once: it
  creates `config/private.key` and applies Prisma migrations against the
  `affine` database.
- `affine` starts the server (`node ./dist/main.js`) on port 3010 and depends
  on the migration job completing. The web client, REST/GraphQL API, and
  WebSocket channel are all served from that single origin.

Both containers share the same env wiring (`DATABASE_URL` → shared `postgres`,
`REDIS_SERVER_*` → shared `default-redis`) and the same persistent volumes
under the cloned repo `.affine-data-<workspace_name>/`:

- `storage` → `/root/.affine/storage`
- `config` → `/root/.affine/config` (private.key lives here — back it up)

## Naming contract

Container names are **not** derived from the Coder workspace name. They derive
from two synchronized values:

1. `workspace_name` — a Coder template variable (default `workspace`) used by
   the devcontainer compose (`container_name` pins
   `coder-${WORKSPACE_NAME:-workspace}-affine`) and the Coder app URL.
2. `WORKSPACE_NAME` — the shared-media nginx envsubst variable (set in
   `docker-compose.nginx.yml`), which resolves the same upstream name.

Keep the two in sync. The Coder workspace itself can be named anything
(e.g. `space`); it does not affect routing.

## Public routing (space.structa.cloud)

The shared-media nginx `server_name space.localhost space.structa.cloud` block
proxies the root (including `/api`, `/_next`, `/assets`, `/ws`) to
`coder-${WORKSPACE_NAME}-affine:3010` with WebSocket upgrade headers and
`client_max_body_size 128m`. Traefik `space.yml` routes the public host here
with Let's Encrypt.

Because AFFiNE is the root app of the origin, no subpath routing or response
rewriting is needed — unlike the AppFlowy/Blinko stacks it replaced.

## Legacy redirects

| Host | Redirect target |
|---|---|
| `blinko.localhost` | `http://space.localhost/` |
| `blinko.structa.cloud` | `https://space.structa.cloud/` |
| `affine.localhost` | `http://space.localhost/` (dev-only) |

Once DNS/certs are no longer needed, delete `blinko.yml` and the redirect
server blocks in the nginx template.

## Data persistence

- AFFiNE: `.affine-data-<workspace_name>/` under the cloned repo (`storage` +
  `config`, the latter holding `private.key`).
- AFFiNE's database and Redis are shared infrastructure (`postgres` on
  `warehouse-net`, `default-redis` on `common`).

## Key files

```text
applications/templates/workspace/
├── main.tf                 # Coder template: single agent-host container + devcontainer wiring
├── README.md               # usage + variable reference
└── ARCHITECTURE.md         # this document
.devcontainer/
├── docker-compose.yml      # devcontainer stack: toolchain + AFFiNE
├── devcontainer.json       # compose-based devcontainer config (service: devcontainer)
└── Dockerfile              # devcontainer toolchain image
applications/proxy/
├── nginx/default.conf.template   # envsubst template (WORKSPACE_NAME)
├── docker-compose.nginx.yml      # shared-media + docus; WORKSPACE_NAME env
└── traefik/dynamic/
    ├── space.yml                 # space.structa.cloud → shared-media (main route)
    └── blinko.yml                # legacy blinko host → root redirect
```

## Validation

```bash
# nginx template renders + syntax (envsubst runs in the image entrypoint)
docker run --rm -e WORKSPACE_NAME=workspace \
  -v "$PWD/applications/proxy/nginx/default.conf.template:/etc/nginx/templates/default.conf.template:ro" \
  nginx:alpine nginx -t

docker compose -f applications/proxy/docker-compose.nginx.yml config -q
docker compose -f .devcontainer/docker-compose.yml config -q
python3 applications/proxy/scripts/validate-traefik-config.py
terraform fmt -check -diff && terraform validate   # in applications/templates/workspace
```
