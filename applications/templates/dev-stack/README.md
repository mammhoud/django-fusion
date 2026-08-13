# dev-stack — Coder Template

Multi-service development workspace provisioned via Coder. Spins up a web-based
VS Code IDE (code-server) with full Node.js/npm tooling plus a Blinko AI
note-taking instance, both wired into the existing Traefik reverse proxy.

## What you get

| Service | Container | Port | External URL |
|---|---|---|---|
| code-server IDE | `coder-dev-code-server` | 8086 | `https://code.structa.cloud` |
| Blinko (notes) | `coder-dev-blinko` | 1111 | `https://blinko.structa.cloud` |

Both containers run on the `common` Docker network alongside PostgreSQL, Redis,
and the Coder control plane.

## ⚠️ Workspace name constraint

The Traefik dynamic configs in `applications/proxy/traefik/dynamic/` hardcode
the container names `coder-dev-code-server` and `coder-dev-blinko`. **The Coder
workspace MUST be named `dev`.** Any other name will produce container names
that Traefik cannot resolve, and external routing will break.

Relevant Traefik configs:
- `applications/proxy/traefik/dynamic/code-server.yml` → upstream `http://coder-dev-code-server:8086`
- `applications/proxy/traefik/dynamic/blinko.yml` → upstream `http://coder-dev-blinko:1111`

This constraint is enforced at plan time by a `lifecycle { precondition }`
block on the code-server container. Attempting to provision with any other
workspace name will produce a clear error and halt before any resources are
created.

## Prerequisites

All of these must be running before you create a workspace from this template:

| Dependency | Provided by | Notes |
|---|---|---|
| PostgreSQL | `applications/databases/docker-compose.yml` | `blinko` DB created via `INITDB_MULTIPLE_DATABASES` |
| Redis | `applications/databases/docker-compose.yml` | Default broker |
| Coder | `applications/databases/docker-compose.yml` | Template server (`coder.structa.cloud`) |
| Traefik | `applications/proxy/docker-compose.yml` | Reverse proxy with dynamic configs |
| `common` network | Created externally | All containers attach to it |

Verify infrastructure is up:

```bash
docker network ls | grep common
docker ps --filter "name=postgres" --filter "name=coder"
```

## Volume mounts

| Host path | Container path | Purpose |
|---|---|---|
| `/home/structa.cloud` | `/home/coder/project` | Full monorepo (read-write) |
| `/var/run/docker.sock` | `/var/run/docker.sock` | Docker CLI access |
| `/home/structa.cloud/.blinko-data-dev` | `/app/.blinko` | Blinko persistent data |

The Blinko data directory is scoped per-workspace to avoid collisions.

## Startup sequence (code-server)

The code-server container runs a startup script that:

1. Installs `docker.io` and `curl`
2. Installs Node.js LTS + latest npm via NodeSource
3. Downloads the Coder agent binary from `http://172.18.0.11:7080`
4. Starts the Coder agent in the background
5. Launches code-server on `0.0.0.0:8086` with password auth

This takes roughly 30–60 seconds. The healthcheck has a 60s `start_period`
to accommodate the full install sequence.

## Health checks

| Container | Probe | Start grace |
|---|---|---|
| code-server | `wget --spider localhost:8086/` | 60s |
| Blinko | `wget --spider localhost:1111/` | 30s |

Use `docker ps` to monitor health status:

```bash
docker ps --filter "name=coder-dev" --format "table {{.Names}}\t{{.Status}}"
```

## Environment variables

### code-server

| Variable | Default | Notes |
|---|---|---|
| `CODER_AGENT_TOKEN` | (auto) | Injected by Coder |
| `CODER_AGENT_URL` | `http://172.18.0.11:7080` | Coder control plane |
| `PASSWORD` | `CTCreSearch0x@` | code-server login |

### Blinko

| Variable | Default | Notes |
|---|---|---|
| `NODE_ENV` | `production` | NextJS runtime mode |
| `NEXTAUTH_SECRET` | `CTCreSearch0x@` | Session encryption key |
| `NEXTAUTH_URL` | `https://blinko.structa.cloud` | Canonical URL |
| `NEXT_PUBLIC_BASE_URL` | `https://blinko.structa.cloud` | Public base URL |
| `DATABASE_URL` | `postgresql://structa:***@postgres:5432/blinko` | PostgreSQL connection |

The `@` character in the PostgreSQL password is URL-encoded to `%40` at
interpolation time via Terraform's `replace(var.postgres_password, "@", "%40")`.
The host and port are interpolated from `var.postgres_host` and
`var.postgres_port`.

## Network topology

```text
                    ┌────────────────────────────┐
                    │         Traefik             │
                    │  (traefik-net + common)     │
                    └──────┬──────────┬──────────┘
                           │          │
              code.structa.cloud   blinko.structa.cloud
                           │          │
              ┌────────────▼──┐  ┌───▼───────────┐
              │ code-server   │  │    Blinko      │
              │  :8086        │  │    :1111       │
              │               │  │                 │
              │ /etc/hosts:   │  │ DATABASE_URL ───┼──► postgres:5432
              │ blinko.local  │  │                 │    (blinko db)
              └───────────────┘  └─────────────────┘
                      │
              /home/coder/project
              (bind mount to /home/structa.cloud)
```

## Configuration variables

All defaults can be overridden when creating the workspace:

| Variable | Default | Notes |
|---|---|---|
| `code_server_version` | `4.131.0` | code-server image tag |
| `code_server_port` | `8086` | IDE listen port |
| `code_server_password` | `CTCreSearch0x@` | IDE login (sensitive) |
| `blinko_port` | `1111` | Blinko listen port |
| `workspace_mount` | `/home/structa.cloud` | Host monorepo root |
| `container_mount` | `/home/coder/project` | Container mount point |
| `docker_network` | `common` | Docker network to join |
| `postgres_host` | `postgres` | PostgreSQL host for Blinko |
| `postgres_port` | `5432` | PostgreSQL port |
| `postgres_password` | `CTCreSearch0x@` | PG password (sensitive) |
| `coder_host_ip` | `172.18.0.11` | Coder container IP |

## Related files

```
applications/
├── templates/dev-stack/
│   ├── main.tf          ← this template
│   └── README.md        ← you are here
├── proxy/traefik/dynamic/
│   ├── code-server.yml  ← Traefik → code-server routing
│   ├── blinko.yml       ← Traefik → Blinko routing
│   └── certs.yml        ← TLS certificates
└── databases/
    └── docker-compose.yml  ← PostgreSQL + Redis + Coder
```
