# Coder Templates

Terraform templates for [Coder](https://coder.com) workspaces. The active
`workspace` template provides a mounted monorepo development environment;
shared applications run independently in the proxy stack.

## Templates

| Template | Provisioned workspace | Shared application routes |
|---|---|---|
| [workspace](./workspace/README.md) | Agent host, mounted devcontainer, VS Code Web, web terminal, authenticated Files app | AFFiNE at `space.structa.cloud/`; FileGator at `space.structa.cloud/files/` and `files.structa.cloud` |

## workspace

The template bind-mounts the local checkout (`host_repo_path`, default
`/home/structa.cloud`) instead of cloning it. The same files are visible on
the host, in the Coder agent host, and in the devcontainer. The agent runs as
root so npm and Git can write to the root-owned checkout.

The `devcontainers-cli` module and `coder_devcontainer` start only
`.devcontainer/docker-compose.yml`. AFFiNE and FileGator are not installed by
or stopped with a workspace; they are permanent services in
`applications/proxy/docker-compose.nginx.yml` using shared PostgreSQL/Redis
and persistent proxy-owned data directories.

The Coder template disables VS Code Desktop and provides VS Code Web. It also
provides a Files app backed by the shared FileGator service. Antigravity is not
included because no runnable image or supported deployment contract was
specified.

## Shared infrastructure

| Component | Defined in |
|---|---|
| PostgreSQL + Redis | `applications/databases/docker-compose.yml` |
| Coder control plane | `applications/docker-compose.yml` |
| AFFiNE, FileGator, shared-media, and Docus | `applications/proxy/docker-compose.nginx.yml` |
| Workspace and Files routing | `applications/proxy/traefik/dynamic/space.yml` |
| Legacy Blinko redirect | `applications/proxy/traefik/dynamic/blinko.yml` |
| Coder routing | `applications/proxy/traefik/dynamic/coder.yml` |
| Docker networks | `common`, `traefik-net`, `warehouse-net` |

## Quick start

```bash
cd applications/databases
docker compose up -d postgres default-redis

cd ../proxy
# Set AFFINE_DB_PASSWORD and REDIS_PASSWORD in .env first.
docker compose --env-file .env -f docker-compose.nginx.yml up -d

docker compose -f docker-compose.traefik.yml up -d

cd ../..
coder templates push \
  -d applications/templates/workspace \
  -m "Mounted monorepo workspace with shared proxy applications" \
  -y workspace
```

## File layout

```text
applications/templates/
├── README.md
└── workspace/
    ├── main.tf
    ├── README.md
    └── ARCHITECTURE.md

.devcontainer/
├── Dockerfile
├── docker-compose.yml       # development container only
└── devcontainer.json

applications/proxy/
├── docker-compose.nginx.yml # shared-media + Docus + AFFiNE + FileGator
├── affine-data/             # ignored persistent AFFiNE files
├── filegator-data/          # ignored persistent FileGator repository
└── nginx/default.conf.template
```
