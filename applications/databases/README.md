# Databases Infrastructure

**Location:** `applications/databases/`
**Purpose:** Data storage, caching, and database services (PostgreSQL + Redis)
**Created:** Phase 11

---

## Overview

The `applications/databases` directory contains the shared data infrastructure:

- **PostgreSQL** — primary relational database (multi-database bootstrap)
- **Redis** — caching and session store / Dramatiq broker

Database administration UI (**Adminer**) now lives in
`applications/tools/adminer/` (path-routed at `tools.structa.cloud/adminer/`),
not in this stack.

---

## Directory Structure

```
applications/databases/
├── README.md                    (this file)
├── docker-compose.yml           (PostgreSQL + Redis)
├── postgres/                    (PostgreSQL config)
│   ├── Dockerfile               (custom entrypoint)
│   ├── init/
│   │   └── 00.initdb-multiple-databases.sh
│   └── backups/
└── redis/                       (Redis config)
    └── redis.conf
```

---

## Services

### PostgreSQL

**Purpose:** Primary relational database
**Port:** `${POSTGRES_PORT:-5432}`
**Container:** `postgres`

**Environment (from repo-root `.env`):**
- `POSTGRES_USER` (default `admin`)
- `POSTGRES_PASSWORD` — **required** (`POSTGRES_PASSWORD=...` in `.env`)
- `POSTGRES_DB` (default `app_db`)
- `POSTGRES_PORT` (default `5432`)
- `POSTGRES_DATABASES` — comma-separated `db:owner:password` list for the
  multi-database bootstrap (defaults to all site + tool DBs)
- `FORCE_REINIT` — `true` re-runs init scripts on every start (default `false`)

**Multiple databases:** The `00.initdb-multiple-databases.sh` entrypoint creates
every database listed in `POSTGRES_DATABASES`. The default value covers the
known sites and tools:

```text
db_precis_lms, db_precis_ctc, db_vresume, coder, db_loop_crm,
db_precis_landing, affine
```

**Volumes:**
- `postgres_data` — named volume for database files
- `./postgres/init` — initialization scripts
- `./postgres/backups` — backup destination

### Redis

**Purpose:** Caching and session store / Dramatiq broker
**Port:** `${REDIS_PORT:-6379}`
**Container:** `default-redis` (name is a hard contract — every site + the
shared task stack resolves `redis://default-redis:6379/<db>`)

**Configuration:**
- `requirepass` — `REDIS_PASSWORD` (**required** in `.env`)
- `--appendonly yes` — persistence enabled (AOF)
- `redis_data` named volume

---

## Coder control plane

The Coder service is owned by `applications/docker-compose.yml`, separate from
this database Compose file. PostgreSQL still creates the dedicated `coder`
database and role through `INITDB_MULTIPLE_DATABASES`; the Coder container
joins the external `common` network and connects to that database by service
name.

```bash
# Start PostgreSQL/Redis first, then Coder from the application boundary.
cd applications/databases
make up
cd ..
docker compose -f applications/docker-compose.yml up -d coder
```

### AFFiNE shared-service database

AFFiNE is a permanent service owned by `applications/tools/affine/` (was
`applications/proxy/docker-compose.nginx.yml`). The `proxy-affine` container
connects to this PostgreSQL service through the external `common` and
`warehouse-net` networks:

| Setting | Value |
|---|---|
| Database | `affine` |
| Role | `affine` |
| Host | `postgres` |
| Password source | repo-root `.env` (`AFFINE_DB_PASSWORD`) |

---

## Docker Compose

**File:** `applications/databases/docker-compose.yml`

**Services:**
- `postgres` (main database)
- `default-redis` (cache / broker)

**Networks:** `common`, `warehouse-net`, `internal`, `traefik-net`,
`site_network` (all external).

---

## Deployment

```bash
# Start databases
cd applications/databases
make up            # or: docker compose up -d

# Stop
make down

# View logs
make logs
```

Root Makefile shortcut: `make deploy-databases`.

### Backup Database

```bash
# Dump database
docker exec postgres pg_dump -U admin app_db > backup.sql

# Restore database
docker exec -i postgres psql -U admin app_db < backup.sql
```

---

## Adminer

Adminer is no longer part of this stack. It lives at
`applications/tools/adminer/` and is served at
`https://tools.structa.cloud/adminer/` (Traefik → shared-proxy Nginx path
split). To connect it to this PostgreSQL instance, use:

- System: **PostgreSQL**
- Server: `postgres`
- Username / Password / Database: from `.env`

```bash
cd applications/tools/adminer && make up
```

---

## Connection Strings

- **PostgreSQL:** `postgresql://admin:<password>@postgres:5432/<db>`
- **Redis:** `redis://:<password>@default-redis:6379/0`

---

## Environment Variables

**Required in repo-root `.env`:**
```bash
POSTGRES_USER=admin
POSTGRES_PASSWORD=...
POSTGRES_DB=app_db
POSTGRES_PORT=5432
POSTGRES_DATABASES=db_precis_lms:structa:<pw>,db_precis_ctc:structa:<pw>,...
REDIS_PASSWORD=...
CODER_DB_PASSWORD=...
AFFINE_DB_PASSWORD=...
```

---

## Maintenance

### Regular Tasks

- ✅ Monitor disk space for the database
- ✅ Review slow query logs
- ✅ Backup database daily
- ✅ Verify Redis persistence
- ✅ Check connection pool usage

### Troubleshooting

**PostgreSQL not starting:**
1. Port 5432 free: `lsof -i :5432`
2. Disk space: `df -h`
3. Permissions on `postgres_data` volume
4. `.env` has `POSTGRES_PASSWORD` set

```bash
docker compose logs postgres
```

**Redis connection issues:**
1. Redis running: `docker ps | grep redis`
2. Password matches `.env`: `docker exec default-redis redis-cli -a "$REDIS_PASSWORD" PING`

---

**Status:** ✅ COMPLETE
**Services:** PostgreSQL (primary database), Redis (cache & session store)
**DB UI:** Adminer at `applications/tools/adminer/`
