# website — Coder Template

Single-container Django/Wagtail workspace provisioned via Coder. Builds a Docker
image from the landing-fusion backend Dockerfile, mounts the full monorepo, and
runs the Django dev server inside the container with automatic database creation
and migrations.

## What you get

| Component | Container | Port | External access |
|---|---|---|---|
| Django dev server | `coder-{name}` | 8075 | `http://localhost:8075` (via Coder app) |
| code-server IDE | shared instance | — | `https://code.structa.cloud` (external link) |

The workspace name becomes the PostgreSQL database name (lowercased), so each
workspace gets its own isolated database.

## ⚠️ No hardcoded workspace name constraint

Unlike the dev-stack template, this template does **not** depend on a specific
workspace name. Traefik is not involved — the Django dev server is accessed
through Coder's built-in port forwarding, and the IDE link points to the shared
code-server instance at `code.structa.cloud`.

## Prerequisites

All infrastructure must be running before creating a workspace:

| Dependency | Provided by | Notes |
|---|---|---|
| PostgreSQL | `applications/databases/docker-compose.yml` | DB created automatically on startup |
| Redis | `applications/databases/docker-compose.yml` | `default-redis:6379` |
| Coder | `applications/databases/docker-compose.yml` | Template server + agent binary |
| Docker daemon | Host | Image build + container management |
| `common` network | Created externally | Container attaches to it |
| Shared code-server | Separate Traefik route | IDE button target |

Verify infrastructure:

```bash
docker network ls | grep common
docker ps --filter "name=postgres" --filter "name=coder" --filter "name=default-redis"
```

### Docker image

The workspace builds from `projects/landing-fusion/backend/Dockerfile` at
`/home/structa.cloud`. The image is tagged `coder-website:{workspace}`. The
image is rebuilt whenever the workspace is recreated (triggered by
`build_id = data.coder_workspace.me.id`).

## Volume mounts

| Host path | Container path | Purpose |
|---|---|---|
| `/home/structa.cloud` | `/app` | Full monorepo (read-write) |
| `/var/run/docker.sock` | `/var/run/docker.sock` | Docker CLI access |

Both are read-write — the container needs write access for Django migrations,
collectstatic output, and any docker commands the user runs.

## Startup sequence

The container runs a startup script that:

1. Installs `docker.io` (Docker CLI)
2. Downloads and starts the Coder agent binary from `http://172.18.0.11:7080`
3. Waits for PostgreSQL to become available (`pg_isready` loop)
4. Creates the workspace database if it doesn't exist: `CREATE DATABASE {workspace} OWNER structa`
5. Runs Django migrations (`python manage.py migrate --noinput`)
6. Runs `collectstatic`
7. Starts the Django dev server on `0.0.0.0:8075`

The healthcheck has a 90s `start_period` to accommodate image build, apt
install, PostgreSQL readiness wait, and Django migrations.

## Health check

| Container | Probe | Start grace | Retries |
|---|---|---|---|
| workspace | `curl -f localhost:8075/` | 90s | 5 |

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `CODER_AGENT_TOKEN` | (auto) | Injected by Coder |
| `CODER_AGENT_URL` | `http://172.18.0.11:7080` | Coder control plane |
| `DATABASE_URL` | `postgresql://structa:***@postgres:5432/{workspace}` | Auto-derived from workspace name |
| `REDIS_URL` | `redis://default-redis:6379/0` | Default Redis DB |
| `DJANGO_SETTINGS_MODULE` | `settings` | Landing-fusion settings |
| `DJANGO_DEBUG` | `1` | Debug mode ON for dev |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,*,0.0.0.0` | Permissive for dev |
| `WAGTAIL_SITE_NAME` | `{workspace}-dev` | Wagtail site identifier |
| `WAGTAILADMIN_BASE_URL` | `http://localhost:8075` | Admin base URL |

The `@` character in the PostgreSQL password is URL-encoded to `%40` at
Terraform interpolation time via `replace(var.postgres_password, "@", "%40")`.

## Configuration variables

| Variable | Default | Notes |
|---|---|---|
| `project_path` | `/home/structa.cloud` | Host monorepo root |
| `container_mount` | `/app` | Container mount point |
| `django_port` | `8075` | Django dev server port |
| `postgres_host` | `postgres` | PostgreSQL hostname |
| `postgres_port` | `5432` | PostgreSQL port |
| `postgres_user` | `structa` | PostgreSQL user |
| `postgres_password` | `CTCreSearch0x@` | PG password (sensitive) |
| `redis_host` | `default-redis` | Redis hostname |
| `redis_port` | `6379` | Redis port |
| `docker_network` | `common` | Docker network |
| `code_server_url` | `https://code.structa.cloud` | Shared IDE link |

## Database isolation

Each workspace gets its own database named after the workspace (lowercased).
For a workspace named `marketing-site`, the database is `marketing-site`.

The `PGPASSWORD` env var is set for the `psql` CREATE DATABASE command so
password prompts are avoided. The database is owned by the `structa` user.

If the database already exists, the `CREATE DATABASE` command is silently
skipped (`|| true`), making startup idempotent.

## Coder apps

Two apps appear in the workspace UI:

| App | Target | Type |
|---|---|---|
| code-server IDE | `https://code.structa.cloud?folder=/app` | External link |
| Django (8075) | `http://localhost:8075` | Port-forwarded |

## Network topology

```text
┌─────────────────────────────────┐
│         Coder (7080)            │
│  Agent binary + control plane   │
└────────────┬────────────────────┘
             │ http://172.18.0.11:7080
             ▼
┌────────────────────────────────┐
│     workspace container        │
│     coder-{name}               │
│                                │
│  /app  ← /home/structa.cloud   │
│  :8075 (Django runserver)      │
│                                │
│  DATABASE_URL ──────► postgres:5432
│  REDIS_URL ─────────► default-redis:6379
│  /etc/hosts: coder.structa.cloud → 172.18.0.11
└────────────────────────────────┘
```

## Related files

```
applications/
├── templates/website/
│   ├── main.tf          ← this template
│   └── README.md        ← you are here
├── databases/
│   └── docker-compose.yml  ← PostgreSQL + Redis + Coder
└── proxy/traefik/dynamic/
    └── coder.yml           ← Traefik → Coder routing

projects/landing-fusion/backend/
├── Dockerfile              ← Image built by this template
├── settings.py             ← DJANGO_SETTINGS_MODULE target
└── manage.py               ← Migrations + runserver entry
```
