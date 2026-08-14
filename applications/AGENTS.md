# `applications/` — Infrastructure and Operations Guidance

Read the repository root `AGENTS.md` first. This directory owns deployment and
platform tooling, not product feature code.

## Layout

```text
applications/
├── databases/               # PostgreSQL, Redis, initialization, backups
│   ├── docker-compose.yml
│   ├── postgres/             # image, entrypoint, init SQL, maintenance
│   └── redis/                # redis.conf
├── proxy/                   # Traefik, Nginx media, TLS/cert operations
│   ├── docker-compose*.yml
│   ├── traefik/              # static/dynamic routers and middleware
│   ├── nginx/                # shared static/media server
│   └── scripts/              # certificate validation/backup/restore
├── docker-compose.yml       # Coder control-plane Compose stack
├── docker-compose.tasks.yml # shared-worker + shared-scheduler compose
├── scripts/                  # dev, staging, testing, production automation
├── agents/                   # FastAPI MCP/introspection server and agent skills
├── templates/                # infrastructure templates (e.g. Terraform)
├── examples/                 # deployment/consumer examples
└── tmp/                      # local investigation scripts; not product code
```

## Runtime topology

```text
Traefik / TLS
  ├── product web services
  ├── landing/frontend and backend routes
  ├── Coder and auxiliary services
  └── shared-media (Nginx)

PostgreSQL ── product databases, Coder, application persistence
Redis ─────── cache, Celery/Dramatiq broker/result databases
Workers ───── shared task Compose stack and product workers
```

Keep network names, service names, health checks, ports, and volume names
synchronized across database, proxy, product Compose, and Makefile files. When
adding a service, update the relevant Compose include, proxy router, health
probe, documentation, and CI path filters as applicable.

## Ownership rules

- Database image/init/backup behavior belongs in `applications/databases/`.
- Host routing, TLS, certificates, static/media serving, and proxy middleware
  belong in `applications/proxy/`.
- Cross-service dependency order belongs in the root deployment Makefile, not
  in a product's application code.
- Product-specific environment defaults belong in the product Compose file or
  product `.env.example`; shared infrastructure names may be documented here.
- Validation and maintenance scripts must be explicit about target paths and
  should default to read-only checks.

## Safe operations

Treat these as destructive or environment-affecting and require explicit user
intent before running them:

```text
docker compose down --volumes
make prune-volumes / make clean / docker system prune
restore/upgrade database scripts
certificate restore/rotation scripts
make deploy / make deploy-all / production scripts
fixture reloads and data-population commands
```

Never expose secret values in logs or documentation. Use environment variable
names and redacted Compose output. Do not change production resolver, ACME,
credential, database, or volume behavior as part of an unrelated code change.

## Validation commands

Prefer no-mutation checks first:

```bash
docker compose -f applications/databases/docker-compose.yml config -q
docker compose -f applications/proxy/docker-compose.yml config -q
docker compose -f applications/docker-compose.tasks.yml config -q
python3 applications/proxy/scripts/validate-traefik-config.py
make deploy-ci                 # preflight only; inspect recipe first
```

The root Makefile's `deploy-preflight` and `preflight-network` targets can
create networks as part of their current contract. Confirm Docker context and
credentials before using them.

## Kilo/MCP

`applications/agents/` is a lightweight FastAPI MCP server. Read
`applications/agents/AGENTS.md` before changing endpoints, agent definitions, or
skills. Keep imports lightweight and avoid configuring Django or loading AI
models at module import time. Endpoint additions should include readiness,
error, and optional-dependency behavior where relevant.
