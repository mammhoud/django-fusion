# Coder Templates

Terraform templates for [Coder](https://coder.com) workspaces. The active
`workspace` template provides a mounted monorepo development environment;
AFFiNE runs independently in the shared proxy stack.

## Templates

| Template | Provisioned workspace | Shared application route |
|---|---|---|
| [workspace](./workspace/README.md) | Agent host, mounted devcontainer, VS Code Web, and web terminal | AFFiNE at `space.structa.cloud/` |

## workspace

The template bind-mounts the local checkout (`host_repo_path`, default
`/home/structa.cloud`) instead of cloning it. The same files are visible on
the host, in the Coder agent host, and in the devcontainer. The agent runs as
root so npm and Git can write to the root-owned checkout.

The `devcontainers-cli` module and `coder_devcontainer` start only
`.devcontainer/docker-compose.yml`. AFFiNE is not installed by or stopped with
a workspace; it is a permanent service in
`applications/proxy/docker-compose.nginx.yml` using shared PostgreSQL/Redis
and proxy-owned persistent data.

The Coder template disables VS Code Desktop and provides VS Code Web.
Antigravity is not included because no runnable image or supported deployment
contract was specified.

## Shared infrastructure

| Component | Defined in |
|---|---|
| PostgreSQL + Redis | `applications/databases/docker-compose.yml` |
| Coder control plane | `applications/docker-compose.yml` |
| AFFiNE, shared-proxy, and Docus | `applications/proxy/docker-compose.nginx.yml` |
| AFFiNE routing | `applications/proxy/traefik/dynamic/space.yml` |
| Code/Coder routing | `applications/proxy/traefik/dynamic/code.yml` and `coder.yml` |
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
  -m "AFFiNE shared proxy with mounted monorepo devcontainer" \
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
├── docker-compose.nginx.yml # shared-proxy + Docus + AFFiNE
├── affine-data/             # ignored persistent AFFiNE files
└── nginx/default.conf.template
```
