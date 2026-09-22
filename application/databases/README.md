# Shared Databases

`application/databases/` owns the monorepo's shared PostgreSQL cluster and
Redis instance. Both are started by `docker-compose.yml` (which includes both
`postgres/docker-compose.yml` and `redis/docker-compose.yml`), or individually
from their respective subdirectories.

## Layout

```text
application/databases/
├── docker-compose.yml          # include-based orchestrator (postgres + redis)
├── .env.example                # ALL database credentials
├── Makefile                    # up/down/deploy/build/logs/status
├── postgres/
│   ├── docker-compose.yml      # PostgreSQL standalone
│   ├── Dockerfile              # Custom entrypoint + init scripts
│   ├── entrypoint              # Custom postgres entrypoint
│   ├── init/
│   │   ├── 00-create-databases.sql         # Database + role bootstrap (SQL)
│   │   └── 00.initdb-multiple-databases.sh # Role-scoped DB creation (shell)
│   ├── maintenance/            # Backup/upgrade scripts
│   └── backups/                # Volume mount for backups
└── redis/
    ├── docker-compose.yml      # Redis standalone
    └── redis.conf              # Redis server configuration
```

## Databases created

On first start, the init scripts create every database the monorepo needs:

| Database | Owner | Application |
|---|---|---|
| `db_precis_lms` | `django` | Precis Main (unified product) |
| `db_precis_dev` | `django` | Precis Dev (development copy) |
| `db_precis_ctc` | `django` | CTC Research center |
| `db_loop_crm` | `django` | Loop CRM |
| `db_vresume` | `django` | VResume (legacy) |
| `coder` | `coder` | Coder control plane (space.structa.cloud) |
| `blinko` | `blinko` | Blinko AI notes (tools.structa.cloud/notes/) |

**SQL (`00-create-databases.sql`):** Creates the `django` role, all project
databases, the `blinko` database, schema grants, and extensions.

**Shell (`00.initdb-multiple-databases.sh`):** Creates role-scoped databases
from the `INITDB_MULTIPLE_DATABASES` env var (used for Coder and `blinko`).

## Environment

Copy `.env.example` to `.env` before starting:

```bash
cd application/databases
make setup     # creates .env from .env.example (safe to re-run)
```

The `.env` file in this directory is the Compose interpolation source AND is
loaded into containers — credentials for interpolation and runtime are identical.

## Quick start

```bash
# From this directory
docker compose up -d

# From repo root
make deploy-databases

# Validate
docker compose ps
docker compose exec postgres pg_isready
```

## Force re-init

Set `FORCE_REINIT=true` in `.env` to ignore the `.init_done` marker and re-run
all init scripts on the next start. Only use for local/dev resets.

## Remarks & Notes

- Container names (`postgres`, `default-redis`) are the stable DNS names every
  service resolves on the `common` network.
- Blinko uses its own `blinko` role with a dedicated password — the init shell
  script creates it from `INITDB_MULTIPLE_DATABASES`.
- Add a new database by adding it to both `00-create-databases.sql` (for the
  `django` role) or to `POSTGRES_DATABASES` in `.env` (for dedicated roles).
- The databases Makefile reads `.env` from this directory; the postgres and
  redis Compose files read `../../../.env` then `../.env` (local wins).