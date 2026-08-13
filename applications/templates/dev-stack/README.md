# dev-stack — Coder Template

Multi-service development workspace provisioned via Coder. Spins up a web-based
VS Code IDE (code-server) with full Node.js/npm tooling plus a workspace-scoped
FileGator file manager, both wired through the shared reverse-proxy stack
(Traefik → nginx).

## What you get

| Service | Container | Port | External URL |
|---|---|---|---|
| code-server IDE | `coder-dev-code-server` | 8086 | `https://code.structa.cloud` |
| FileGator (files) | `coder-dev-filegator` | 1111 (host) / 8080 (container) | `https://filegator.structa.cloud` |

Both containers run on the `common` Docker network alongside PostgreSQL, Redis,
and the Coder control plane.

## ⚠️ Workspace name constraint

The proxy configs in `applications/proxy/` hardcode the container names
`coder-dev-code-server` and `coder-dev-filegator`. **The Coder workspace MUST
be named `dev`.** Any other name will produce container names the proxy cannot
resolve, and external routing will break.

Relevant proxy configs:
- Traefik: `applications/proxy/traefik/dynamic/code-server.yml` and
  `filegator.yml` → both route their hosts to the shared-media nginx
- nginx: `applications/proxy/nginx/default.conf` → proxying to
  `http://coder-dev-code-server:8086` and `http://coder-dev-filegator:8080`

Routing chain for both services:

```text
code.structa.cloud / filegator.structa.cloud
        │ (TLS + host routing)
      Traefik
        │
      shared-media (nginx)
        │
  coder-dev-code-server:8086   coder-dev-filegator:8080
```

This constraint is enforced at plan time by a `lifecycle { precondition }`
block on the code-server container. Attempting to provision with any other
workspace name will produce a clear error and halt before any resources are
created.

## Prerequisites

All of these must be running before you create a workspace from this template:

| Dependency | Provided by | Notes |
|---|---|---|
| PostgreSQL | `applications/databases/docker-compose.yml` | Shared app databases (not needed by this template's services) |
| Redis | `applications/databases/docker-compose.yml` | Default broker |
| Coder | `applications/databases/docker-compose.yml` | Template server (`coder.structa.cloud`) |
| Traefik + nginx | `applications/proxy/docker-compose.yml` | Edge proxy + shared-media frontend |
| FileGator hardened config | `applications/proxy/filegator/` | `configuration.php` + `users.json`, bind-mounted read-only |
| `common` network | Created externally | All containers attach to it |

Verify infrastructure is up:

```bash
docker network ls | grep common
docker ps --filter "name=postgres" --filter "name=coder" --filter "name=shared-media"
```

## Migration from the Blinko-era workspace (2026-08)

If a `dev` workspace was created before this template replaced Blinko with
FileGator, **destroy it before re-provisioning**. The old workspace still runs
the `coder-dev-blinko` container, which holds host port `1111` — the new
FileGator container publishes `1111:8080` and will fail to bind while Blinko
is alive:

```bash
# In Coder: delete the `dev` workspace, then create it again from this template.
# Or, to clear just the stale container without a full rebuild:
docker rm -f coder-dev-blinko
```

## First run (FileGator repository ownership)

FileGator runs as `www-data` (uid 33). Docker auto-creates missing bind-mount
host paths as `root:root`, which would make the workspace FileGator unable to
write uploads. Before creating a workspace (or after wiping the data dir):

```bash
mkdir -p /home/structa.cloud/.filegator-data-dev/repository
chown -R 33:33 /home/structa.cloud/.filegator-data-dev
```

> The workspace FileGator mounts `users.json` **read-only**, so credentials are
> shared with the host-level instance and password changes made in the FileGator
> UI will **not** persist. Rotate the password in
> `applications/proxy/filegator/users.json` instead (see the
> [FileGator README](../proxy/filegator/README.md)).

## Volume mounts

| Host path | Container path | Purpose |
|---|---|---|
| `/home/structa.cloud` | `/home/coder/project` | Full monorepo (read-write) |
| `/var/run/docker.sock` | `/var/run/docker.sock` | Docker CLI access |
| `/home/structa.cloud/.filegator-data-dev/repository` | `/var/www/filegator/repository` | FileGator uploads (per-workspace) |
| `/home/structa.cloud/applications/proxy/filegator/configuration.php` | `/var/www/filegator/configuration.php` | Hardened FileGator config (read-only) |
| `/home/structa.cloud/applications/proxy/filegator/users.json` | `/var/www/filegator/private/users.json` | Version-controlled admin credentials (read-only) |

The FileGator data directory is scoped per-workspace to avoid collisions.

## Startup sequence (code-server)

The code-server container runs a startup script that:

1. Installs `docker.io` and `curl`
2. Installs Node.js LTS + latest npm via NodeSource
3. Installs the latest `pnpm` CLI globally (repo-standard package manager
   used by the landing-fusion frontend and all formints editions — run
   `pnpm` from the shell once the workspace is up)
4. Installs the additional shell CLIs `tsx`, `yarn`, `astro`, `nodemon`,
   and `bun` globally (see the shell-tools table below)
5. Downloads the Coder agent binary from `http://172.18.0.11:7080`
6. Starts the Coder agent in the background
7. Launches code-server on `0.0.0.0:8086` with password auth

This takes roughly 60–120 seconds on a cold registry pull (the global npm
CLI installs add time on first provision). The healthcheck has a 120s
`start_period` to accommodate the full install sequence; `docker logs
coder-dev-code-server` prints an `OK`/`MISSING` line per shell CLI so you can
confirm exactly which tools landed.

## Health checks

| Container | Probe | Start grace |
|---|---|---|
| code-server | `wget --spider localhost:8086/` | 60s |
| FileGator | `curl -fsS localhost:8080/` | 20s |

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

Shell tools installed globally in the workspace container: `node`, `npm`,
`docker`, `curl` plus the npm-installed CLIs below. `pnpm` matches the repo's
package manager (see `pnpm-lock.yaml` in landing-fusion/formints projects).

| CLI | Purpose |
|---|---|
| `pnpm` | Repo-standard package manager (landing-fusion, formints) |
| `tsx` | Run TypeScript files directly at the shell |
| `yarn` | Classic yarn CLI for `yarn.lock` projects |
| `astro` | Astro CLI for the landing-fusion / precis frontends |
| `nodemon` | Auto-restart Node scripts on file changes |
| `bun` | Bun runtime + package manager (`bun.lock` projects) |

All of them are on `PATH` as plain shell commands once the workspace is up.

### FileGator

FileGator is configured entirely through its PHP config (no env vars). The
template reuses the hardened, version-controlled config from
`applications/proxy/filegator/`:

- `configuration.php` — randomized `csrf_key`, `cookie_secure=true`,
  100 MB uploads, UTC timezone
- `users.json` — the same admin credentials as the host-level FileGator
  (`https://media.structa.cloud/filegator/`); see the
  [FileGator README](../proxy/filegator/README.md) for rotating the password

> The workspace FileGator repository (`/home/structa.cloud/.filegator-data-dev/`)
> is **separate** from the host-level shared repository
> (`projects/assets/media/filegator/`) — per-workspace uploads never mix with
> the public media tree.

## Network topology

```text
                    ┌──────────────────────────────┐
                    │           Traefik             │
                    │  (traefik-net + common)       │
                    └───────┬────────────┬──────────┘
                            │            │
              code.structa.cloud   filegator.structa.cloud
                            │            │
                    ┌───────▼──────┐  ┌──▼──────────────┐
                    │ shared-media │  │ shared-media    │
                    │ (nginx)      │  │ (nginx)         │
                    └───────┬──────┘  └──┬──────────────┘
                            │            │
              ┌─────────────▼──┐  ┌──────▼────────────┐
              │ code-server    │  │ FileGator          │
              │  :8086         │  │  :8080             │
              │                │  │                    │
              │ /etc/hosts:    │  │ repository ───────► .filegator-data-dev/
              │ filegator.local│  │                    │
              └────────────────┘  └────────────────────┘
                      │
              /home/coder/project
              (bind mount to /home/structa.cloud)
```

## Configuration variables

All defaults can be overridden when creating the workspace:

| Variable | Default | Notes |
|---|---|---|
| `code_server_version` | `4.132.0` | code-server image tag |
| `code_server_port` | `8086` | IDE listen port |
| `code_server_password` | `CTCreSearch0x@` | IDE login (sensitive) |
| `filegator_port` | `1111` | FileGator published host port (container listens on 8080) |
| `workspace_mount` | `/home/structa.cloud` | Host monorepo root |
| `container_mount` | `/home/coder/project` | Container mount point |
| `docker_network` | `common` | Docker network to join |
| `coder_host_ip` | `172.18.0.11` | Coder container IP |

## Related files

```
applications/
├── templates/dev-stack/
│   ├── main.tf          ← this template
│   └── README.md        ← you are here
├── proxy/
│   ├── docker-compose.yml        ← Traefik + shared-media nginx
│   ├── nginx/default.conf        ← nginx → code-server / FileGator routing
│   ├── filegator/                ← hardened FileGator config + credentials
│   └── traefik/dynamic/
│       ├── code-server.yml       ← Traefik host routing (→ shared-media)
│       ├── filegator.yml         ← Traefik host routing (→ shared-media)
│       └── certs.yml             ← TLS certificates
└── databases/
    └── docker-compose.yml  ← PostgreSQL + Redis + Coder
```
