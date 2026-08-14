# Coder Templates

Terraform templates for [Coder](https://coder.com) workspaces. Templates
provision the monorepo, Docker access, and a Coder agent for authenticated
workspace applications.

## Templates

| Template | What it provisions | Public routing | Workspace constraint |
|---|---|---|---|
| [**workspace**](./workspace/README.md) | Mounted monorepo + devcontainer + AFFiNE + VS Code Web | AFFiNE (`space.structa.cloud`) | None (set `workspace_name`) |

### workspace

The single development workspace template: one agent-host container that
**bind-mounts the host's local checkout** (`host_repo_path`, default
`/home/structa.cloud`, → `/home/coder/structa.cloud`) instead of cloning it, so
edits made locally or in the workspace are the same files and git commit/push
work from both sides. The `devcontainers-cli` module + `coder_devcontainer`
auto-start the repository's `.devcontainer/` (compose stack with the
full-toolchain `devcontainer` service plus AFFiNE), the `code-server` module
provides the **VS Code Web** browser editor on the same folder, and
`display_apps` disables the VS Code Desktop button. No host ports are
published; the agent runs as root so the root-owned checkout stays writable.

The workspace is served under ONE public origin, `space.structa.cloud` (root =
AFFiNE, web + API + WebSocket). Routes resolve through the shared-media nginx
to the devcontainer service container `coder-<workspace_name>-affine`
(envsubst-templated from `WORKSPACE_NAME`; Traefik routes `space.structa.cloud`
via `space.yml`). The former `blinko.structa.cloud` host 301-redirects to the
consolidated origin; the public `affine.pro` and `filegator.structa.cloud`
hosts were removed.

→ [workspace README](./workspace/README.md) ·
[main.tf](./workspace/main.tf)

## Shared infrastructure

| Component | Defined in |
|---|---|
| PostgreSQL + Redis | `applications/databases/docker-compose.yml` |
| Coder control plane | `applications/docker-compose.yml` |
| Traefik + shared-media nginx | `applications/proxy/docker-compose.yml` |
| Workspace origin route | `applications/proxy/traefik/dynamic/space.yml` |
| AFFiNE route | `applications/proxy/traefik/dynamic/affine.yml` |
| Legacy AppFlowy host redirect | `applications/proxy/traefik/dynamic/space.yml` |
| Legacy Blinko host redirect | `applications/proxy/traefik/dynamic/blinko.yml` |
| Docker networks (`common`, `warehouse-net`) | Infrastructure deployment |

The database and Redis services must be running before creating a `workspace`.
A new PostgreSQL volume creates the `affine` database and role; existing
volumes need the normal database maintenance step to add them.

## Quick start

```bash
# 1. Start shared database infrastructure
cd applications/databases
docker compose up -d postgres default-redis

# 2. Start Coder
cd ..
docker compose -f docker-compose.yml up -d coder

# 3. Push the template
coder templates push workspace --directory applications/templates/workspace

# 4. Create workspace (any name works; containers use workspace_name)
#    Open AFFiNE from the Coder workspace page, or visit https://space.structa.cloud
#    (root = AFFiNE; the former blinko host 301-redirects there).
```

## File layout

```text
applications/templates/
├── README.md
└── workspace/
    ├── main.tf       # mounted monorepo + AFFiNE devcontainer + VS Code Web
    ├── README.md     # full workspace configuration and validation
    └── ARCHITECTURE.md

.devcontainer/
├── Dockerfile          # devcontainer image (full monorepo toolchain)
└── devcontainer.json   # builds the Dockerfile + Docker daemon — devcontainer source
```
