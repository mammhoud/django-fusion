---
Object type: Tool
Tags: tool, postgres, redis, database, infrastructure
Status: Active
Category: Data
Related Features: crm-core-features
Related Plans: deployment
---

# PostgreSQL + Redis — Shared Data & Cache

> **Description:** The shared relational database and cache backing deployed products — Postgres primary, Redis for queues/cache (Celery/Dramatiq-related workers).

## Method

- Postgres databases per product (`db_loop_crm`, `db_precis_*`, `blinko`, `coder`…) created by `application/databases/`
- Redis backs queues/cache in deployed environments
- Compose topology in `application/`; stable DNS names `postgres`, `default-redis` on the `common` network

## Boundary

- Do not run migrations, destructive fixture loads, or volume pruning against shared environments without explicit direction
- `docker compose down --volumes`, `docker system prune` are effectful — confirm first

## Use case

Django products read/write tenant-scoped rows in Postgres; background workers consume Redis-backed queues for email, webhooks, and AI tasks.

## Related

- → `../guides/deployment.md` — Deployment method
- → `../objects/tool.md` — Tool object type