# Coder Templates

Terraform templates for [Coder](https://coder.com) workspaces. Templates
provision the monorepo, Docker access, and a Coder agent for authenticated
workspace applications.

## Templates

| Template | What it provisions | Public routing | Workspace constraint |
|---|---|---|---|
| [**workspace**](./workspace/README.md) | AFFiNE + devcontainer | AFFiNE (`space.structa.cloud`) | None (set `workspace_name`) |
| [**devcontainer**](./devcontainer/README.md) | Any repo's devcontainer via Docker-in-Docker | Coder app | None |

### workspace

The development workspace is a single agent-host container that runs the
repository's compose devcontainer inside it (docker-devcontainer pattern): the
devcontainers-cli and git-clone modules clone `repo_url` (default: the Structa
Cloud monorepo) and `coder_devcontainer` auto-starts its `.devcontainer/` — a
compose stack (`docker-compose.yml`) with the full-toolchain `devcontainer`
service (Dockerfile, docker-in-docker), plus AFFiNE. No fixed host ports are
published; the IDE runs inside the devcontainer itself.

The workspace is served under ONE public origin, `space.structa.cloud` (root =
AFFiNE, web + API + WebSocket). Routes resolve through the shared-media nginx
to the devcontainer service container `coder-<workspace_name>-affine`
(envsubst-templated from `WORKSPACE_NAME`; Traefik routes `space.structa.cloud`
via `space.yml`). The former `blinko.structa.cloud` host 301-redirects to the
consolidated origin; the public `affine.pro` and `filegator.structa.cloud`
hosts were removed.

→ [workspace README](./workspace/README.md) ·
[main.tf](./workspace/main.tf)

### devcontainer

Modeled on the official
[`coder/docker-devcontainer`](https://registry.coder.com/templates/coder/docker-devcontainer)
template: a single privileged container runs Docker-in-Docker, clones
`repo_url` (default: the Structa Cloud monorepo), and `coder_devcontainer`
auto-starts its `.devcontainer/` so the IDE opens the devcontainer directly.
Home and the inner Docker daemon persist on dedicated volumes. Unlike
`workspace`, devcontainers run on the workspace's own bridge network — use
`workspace` when the devcontainer needs the shared host infrastructure.

→ [devcontainer README](./devcontainer/README.md) ·
[main.tf](./devcontainer/main.tf)

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

# 3. Push the templates
coder templates push workspace --directory applications/templates/workspace
coder templates push devcontainer --directory applications/templates/devcontainer

# 4. Create workspace (any name works; containers use workspace_name)
#    Open AFFiNE from the Coder workspace page, or visit https://space.structa.cloud
#    (root = AFFiNE; the former blinko host 301-redirects there).
```

## File layout

```text
applications/templates/
├── README.md
├── workspace/
│   ├── main.tf       # agent-host container + AFFiNE devcontainer
│   ├── README.md     # full workspace configuration and validation
│   └── ARCHITECTURE.md
├── devcontainer/
│   ├── main.tf       # privileged docker-devcontainer (Docker-in-Docker)
│   ├── scripts/
│   │   └── init-docker-in-docker.sh
│   └── README.md

.devcontainer/
├── Dockerfile          # devcontainer image (full monorepo toolchain)
└── devcontainer.json   # builds the Dockerfile + Docker daemon — devcontainer source
```
