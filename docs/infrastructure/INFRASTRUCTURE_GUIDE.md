# Infrastructure Guide

Reference for the Docker Compose stack, networking, databases, and service topology.

---

## Compose Stack Architecture

The workspace uses a **layered Docker Compose** pattern. Shared infrastructure is defined once
and included by per-site compose files. This avoids duplication while allowing each site to be
managed independently.

```
compose/
├── docker-compose.warehouse.yml   ← shared DB (structa-db) + cache (structa-cache)
├── docker-compose.traefik.yml     ← shared reverse proxy (structa-proxy / Traefik)
├── docker-compose.yml             ← shared YAML anchors + network definitions
├── docker-compose.nginx.yml       ← optional Nginx variant
├── docker-compose.caddy.yml       ← optional Caddy variant
├── docker-compose.utilities.yml   ← monitoring stack (Prometheus, Loki, Grafana)
├── docker-compose.tasks.yml       ← Celery worker/beat definitions
└── docker-compose.docs.yml        ← documentation server

ctc-research/docker-compose.yml    ← `include: ../compose/docker-compose.yml`
lms-demo/docker-compose.yml        ← `include: ../compose/docker-compose.yml`
VResume/docker-compose.yml         ← `include: ../compose/docker-compose.yml`

utilities/docker-compose.yml       ← standalone monitoring stack
warehouses/docker-compose.yml      ← standalone dev alternative (postgres+redis+adminer)
```

### Layer 1: Shared Infrastructure

`compose/docker-compose.warehouse.yml` defines the central database and cache containers
that all three sites share:

- **structa-db** — PostgreSQL with `INITDB_MULTIPLE_DATABASES` to create all databases on first start
- **structa-cache** — Redis with password authentication

Both containers join `traefik-net` and `site_network`.

`compose/docker-compose.traefik.yml` defines:

- **structa-proxy** — Traefik v3 reverse proxy with ACME TLS, HTTP→HTTPS redirect, and the
  Traefik dashboard. Reads dynamic configuration from `compose/traefik/dynamic/`.

### Layer 2: Per-Site Services

Each site's `docker-compose.yml` uses the `include:` directive to pull in shared anchors:

```yaml
include:
  - path: ../compose/docker-compose.yml

services:
  ctc-research-website:
    <<: *django-base          # inherits the shared anchor
    environment:
      DJANGO_SITE: ctc-research
      PORT: 5070
      DB_NAME: db_ctc
```

This pattern means you can start an individual site without spinning up all three:

```bash
# Start only ctc-research (still requires structa-db/structa-cache to be running)
docker compose -f ctc-research/docker-compose.yml up

# Start full production stack
docker compose -f compose/docker-compose.warehouse.yml \
               -f compose/docker-compose.traefik.yml \
               -f ctc-research/docker-compose.yml \
               -f lms-demo/docker-compose.yml \
               -f VResume/docker-compose.yml up -d
```

### Layer 3: Utilities

`utilities/docker-compose.yml` is a standalone monitoring stack that can be started independently:

```bash
docker compose -f utilities/docker-compose.yml up -d
```

Includes: Prometheus, Loki, Grafana, Blinko (note-taking/knowledge base).

---

## Database Setup

### Production (compose/docker-compose.warehouse.yml)

`structa-db` uses a custom PostgreSQL image with an `INITDB_MULTIPLE_DATABASES` environment
variable that creates multiple databases in a single container. Format:

```
db_name:owner_user:password[,db_name2:owner2:password2]
```

Default configuration creates:
- `db_ctc` — ctc-research production database (owner: `structa`)
- `db_structa` — lms-demo production database (owner: `structa`)
- `vresume` — VResume production database (owner: `structa`)
- `blinko` — Blinko knowledge base database

Configuration via `.env`:
```bash
POSTGRES_DATABASES=db_ctc:structa:mk_pAssWord123,db_structa:structa:mk_pAssWord123,vresume:structa:mk_pAssWord123,blinko
```

### Dev Warehouses (warehouses/)

The `warehouses/` directory provides a standalone Postgres + Redis stack for local development:

```bash
docker compose -f warehouses/docker-compose.yml up -d
```

`warehouses/postgres/init/init-databases.sql` creates separate databases on first start:
- `ctc_research`
- `lms_demo`
- `vresume`

Application user: `django` (password: `django_password`)

The warehouses stack also includes an Adminer web UI at `adminer.localhost:8081`.

---

## Service Ports

| Service | Internal Port | Host Port | Domain / URL |
|---------|:---:|:---:|---|
| ctc-research | 5070 | — | ctc-research.com / www.ctc-research.com |
| lms-demo | 5071 | — | structa.cloud |
| VResume | 5072 | — | vresume.structa.cloud |
| Traefik HTTP | 80 | 80 | all sites |
| Traefik HTTPS | 443 | 443 | all sites |
| Traefik Dashboard | 8080 | 8080 | localhost:8080 |
| Adminer (warehouses) | 8080 | 8081 | adminer.localhost |
| Prometheus | 9090 | 9090 | prometheus.localhost |
| Grafana | 3000 | 3000 | grafana.localhost |
| Loki | 3100 | 3100 | loki.localhost |
| Blinko | 3010 | 3010 | blinko.localhost |
| PostgreSQL (prod) | 5432 | 5432 | structa-db |
| Redis (prod) | 6379 | — | structa-cache |
| PostgreSQL (dev) | 5432 | 5432 | warehouse-postgres |
| Redis (dev) | 6379 | 6379 | warehouse-redis |

---

## Networks

### traefik-net (shared, external-facing)

All containers that need to be reachable via Traefik join `traefik-net`.
This includes:
- `structa-proxy` (Traefik itself)
- `ctc-research-website`, `lms-demo-website`, `vresume-website`
- `structa-db`, `structa-cache` (to allow cross-service access from any site)
- Utility containers (Prometheus, Grafana, etc.)

Traefik labels on each service container tell Traefik which hostnames to route to which port.

### site_network (internal)

`site_network` is an internal network used for backend-to-database communication.
Django containers reach `structa-db` and `structa-cache` via this network without
exposing those services to the internet.

```yaml
# django container joins both networks
networks:
  - traefik-net      # for Traefik routing
  - site_network     # for DB/cache access

# postgres/redis only need site_network for production
networks:
  - traefik-net
  - site_network
```

### warehouse-net (dev only)

The `warehouses/` stack uses its own `warehouse-net` for internal communication between
`warehouse-postgres`, `warehouse-redis`, and `warehouse-adminer`. It also joins `traefik-net`
so Traefik can expose Adminer at `adminer.localhost`.

---

## Warehouses vs compose/warehouse

These serve different purposes:

| | `warehouses/` | `compose/docker-compose.warehouse.yml` |
|---|---|---|
| **Purpose** | Local development | Production / CI |
| **Image** | `postgres:14-alpine` (official) | Custom `compose/postgres/Dockerfile` |
| **Databases** | `ctc_research`, `lms_demo`, `vresume` | `db_ctc`, `db_structa`, `vresume`, `blinko` |
| **DB user** | `django` | `structa` |
| **Includes Adminer** | Yes (port 8081) | No |
| **Naming** | `warehouse-postgres`, `warehouse-redis` | `structa-db`, `structa-cache` |
| **Network** | `warehouse-net` + `traefik-net` | `traefik-net` + `site_network` |
| **Data persistence** | `./postgres/data/` (local volume mount) | Named Docker volume `postgres_data` |

**When to use which:**

- `warehouses/` → local dev without the full production stack. Start it, point your Django
  `DB_HOST=localhost:5432` (or `warehouse-postgres` from within Docker), and iterate fast.
  Adminer gives you a browser SQL client.

- `compose/docker-compose.warehouse.yml` → production and CI. Uses the custom `structa-db`
  image that supports `INITDB_MULTIPLE_DATABASES` to create all databases in one container
  with the correct production naming (`db_ctc` not `ctc_research`).

---

## Health Checks

All site containers define a health check using Django's `/health/` endpoint:

```yaml
healthcheck:
  test: ["CMD", "curl", "-fL", "http://127.0.0.1:5070/health/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 90s
```

Database and cache containers also have health checks (`pg_isready`, `redis-cli ping`)
that site containers depend on (`condition: service_healthy`).

---

## Resource Limits

| Container | CPU | Memory |
|-----------|-----|--------|
| structa-db | 2 cores | 2 GB |
| structa-cache | 1 core | 512 MB |
| structa-proxy | 1 core | 512 MB |
| per-site Django | 2 cores | 1 GB |

Reservations are set at half the limits to allow burst headroom.

---

## TLS / ACME

Traefik handles TLS termination automatically via Let's Encrypt ACME. Certificates are
stored in the `traefik_acme` Docker volume (`/etc/traefik/acme`).

Configuration:
```yaml
environment:
  TRAEFIK_ACME_EMAIL: ${TRAEFIK_ACME_EMAIL:-admin@structa.cloud}
  TRAEFIK_LOG_LEVEL: ${TRAEFIK_LOG_LEVEL:-INFO}
```

For local development, self-signed certs from `compose/traefik/certs/` are used instead.

See `docs/infrastructure/DEPLOYMENT_GUIDE_SSL.md` for full TLS setup instructions.

---

## Quick Reference Commands

```bash
# Start production warehouse + proxy
docker compose -f compose/docker-compose.warehouse.yml up -d
docker compose -f compose/docker-compose.traefik.yml up -d

# Start all sites
docker compose -f ctc-research/docker-compose.yml up -d
docker compose -f lms-demo/docker-compose.yml up -d
docker compose -f VResume/docker-compose.yml up -d

# Start dev warehouses
docker compose -f warehouses/docker-compose.yml up -d

# Start utilities (monitoring)
docker compose -f utilities/docker-compose.yml up -d

# Check status
docker ps

# View logs for a site
docker logs ctc-research-website -f
docker logs structa-db -f

# Make targets
make docker-deploy-full
make docker-up WEBSITE=ctc
make docker-logs-all
make docker-status
```

---

## See Also

- `docs/infrastructure/DEPLOYMENT_CHECKLIST.md` — step-by-step deployment
- `docs/infrastructure/DEPLOYMENT_GUIDE_SSL.md` — TLS configuration
- `docs/infrastructure/CERTIFICATE_BACKUP_GUIDE.md` — certificate management
- `docs/guides/MAKEFILE_REFERENCE.md` — all Make targets
