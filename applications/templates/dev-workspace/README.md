# dev-workspace — Coder Template

Multi-service development workspace provisioned through Coder. It provides an
authenticated code-server IDE, a workspace-scoped FileGator, and an internal
AppFlowy Cloud stack backed by the shared PostgreSQL and Redis services.

## Access model

The workspace no longer publishes fixed host ports for code-server or
AppFlowy, and these public subdomains are intentionally removed:

- `code.structa.cloud` / `ws.structa.cloud`
- `blinko.structa.cloud`

Use the authenticated Coder apps instead. FileGator retains its existing
`filegator.structa.cloud` route for file management, but its container port is
also internal-only. This eliminates the previous Docker error:

```text
Bind for 0.0.0.0:1111 failed: port is already allocated
```

| Coder app | Container | Internal endpoint |
|---|---|---|
| code-server IDE | `coder-dev-code-server` | `http://localhost:8086` |
| FileGator | `coder-dev-filegator` | `http://filegator.local:8080` |
| AppFlowy Workspace | `coder-dev-appflowy-web` | `http://coder-dev-appflowy-web:80` |

## Workspace name constraint

The public FileGator proxy targets `coder-dev-filegator`, so the Coder
workspace **must be named `dev`**. The IDE and AppFlowy services are internal
Coder apps and do not require public DNS names. The Terraform precondition
allows `default` for Coder template validation.

## AppFlowy Cloud

The former Blinko resource is retired. The template provisions the official
AppFlowy Cloud service shape using these internal containers:

- `appflowy-gotrue` — authentication
- `appflowy-cloud` — Rust API
- `appflowy-web` — web client exposed as a Coder app
- `appflowy-minio` — private S3-compatible object storage

AppFlowy Cloud uses the existing `postgres` service on `warehouse-net` and the
existing authenticated `default-redis` service on `common`. The AppFlowy
containers do not publish host ports and are not attached to a public Traefik
router. Persistent object data is stored at:

```text
/home/structa.cloud/.appflowy-data-dev/minio
```

Override the AppFlowy database URLs and secrets in Coder variables before using
this outside local development. The default values are development-only.

The official AppFlowy deployment is a multi-service stack; this template keeps
its dependencies in the workspace while reusing Structa's shared database and
Redis infrastructure. The container image/version variables are configurable
so the workspace can be pinned to a tested AppFlowy release.

## Prerequisites

| Dependency | Provided by | Notes |
|---|---|---|
| PostgreSQL | `applications/databases/docker-compose.yml` | Shared `postgres`; creates `appflowy` on a new volume |
| Redis | `applications/databases/docker-compose.yml` | Shared `default-redis`, password protected |
| Coder | `applications/docker-compose.yml` | Template server |
| Traefik + nginx | `applications/proxy/docker-compose.yml` | FileGator route only for this template |
| `common` and `warehouse-net` | Infrastructure deployment | Must already exist as external Docker networks |

Verify the prerequisites without creating or changing services:

```bash
docker network inspect common warehouse-net
docker ps --filter "name=postgres" --filter "name=default-redis" \
  --filter "name=coder" --filter "name=shared-media"
```

For a new PostgreSQL volume, the database bootstrap creates the `appflowy`
database and role from `INITDB_MULTIPLE_DATABASES`. Existing volumes do not
rerun initialization automatically; create the database and role using the
normal database maintenance procedure before provisioning the workspace.

## First run

```bash
# Push the template
coder templates push dev-workspace \
  --directory applications/templates/dev-workspace

# Create the workspace with the required name
# Coder UI → dev-workspace → workspace name: dev

# Inspect the workspace containers
docker ps --filter "name=coder-dev" \
  --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

The `Ports` column should be empty for the workspace containers. Coder's
authenticated app proxy handles access; there should be no `0.0.0.0:1111`
(or 8086) binding from this template.

## FileGator data

FileGator runs as `www-data` (uid 33). Prepare its repository directory before
creating a workspace or after wiping it:

```bash
mkdir -p /home/structa.cloud/.filegator-data-dev/repository
chown -R 33:33 /home/structa.cloud/.filegator-data-dev
```

The workspace FileGator repository is separate from the host-level public
media repository. Its configuration and credentials remain mounted from
`applications/proxy/filegator/`.

## Networks

```text
                         ┌──────────────────────────┐
                         │ Coder authenticated apps │
                         └─────────────┬────────────┘
                                       │
                    common ───────────┼────────── warehouse-net
                       │               │                    │
                 code-server      AppFlowy API       postgres
                 FileGator        GoTrue/MinIO        appflowy DB
                 AppFlowy web
```

- `common`: Coder workspace services, Redis, and shared-media.
- `warehouse-net`: AppFlowy API/GoTrue to the shared PostgreSQL service.
- No AppFlowy or code-server host port is published.
- No Blinko or code-server public Traefik/Nginx route remains.

## Terraform variables

| Variable | Default | Purpose |
|---|---|---|
| `code_server_version` | `4.132.0` | IDE image tag |
| `code_server_port` | `8086` | Internal IDE listen port |
| `code_server_password` | development value | IDE password, sensitive |
| `appflowy_cloud_version` | `latest` | AppFlowy API image tag |
| `appflowy_web_version` | `latest` | AppFlowy web image tag |
| `appflowy_gotrue_version` | `latest` | Authentication image tag |
| `appflowy_database_url` | development URL | AppFlowy API PostgreSQL URL |
| `appflowy_gotrue_database_url` | development URL | GoTrue PostgreSQL URL |
| `appflowy_jwt_secret` | development value | JWT signing secret, sensitive |
| `appflowy_redis_uri` | authenticated shared Redis URI | Redis broker URI, sensitive |
| `appflowy_admin_email` | `admin@structa.cloud` | Initial administrator |
| `appflowy_admin_password` | development value | Initial administrator, sensitive |
| `appflowy_s3_access_key` | `appflowy` | MinIO access key, sensitive |
| `appflowy_s3_secret_key` | development value | MinIO secret, sensitive |
| `workspace_mount` | `/home/structa.cloud` | Host monorepo path |
| `container_mount` | `/home/coder/project` | IDE project path |
| `docker_network` | `common` | Workspace network |
| `database_network` | `warehouse-net` | PostgreSQL network |
| `coder_host_ip` | `172.18.0.16` | Coder agent callback address |

## Related files

```text
applications/
├── templates/dev-workspace/main.tf       # Coder + internal AppFlowy stack
├── proxy/nginx/default.conf               # Docus/media/FileGator routes only
├── proxy/traefik/dynamic/filegator.yml   # retained FileGator public route
├── databases/docker-compose.yml           # PostgreSQL + Redis
└── docker-compose.yml                     # Coder control plane
```

The old `blinko.yml` and `code-server.yml` dynamic routes are intentionally
removed. Do not recreate public aliases for those services; use Coder apps.
