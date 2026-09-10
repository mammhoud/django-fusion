---
Object type: Tool
Tags: tool, blinko, notes, ai, surrealdb
Status: Active
Category: Operations
Related Features: documentation-system
---

# Blinko — Self-Hosted Personal AI Notes

> **Description:** Self-hosted personal AI note tool (open source, privacy-first) served at `tools.structa.cloud/notes/` via the tools-proxy Nginx.

## Method

- NextAuth login + note CRUD + graph search
- SurrealDB store (`surrealdb:v1.5.6`, `file:/data/blinko.db`) — auth, content graph, and query engine migrated off Prisma/PostgreSQL (M1–M4)
- Compose: `application/tools/blinko/docker-compose.yml`; data in `blinko-data/` (gitignored)

## Boundary

- Pin SurrealDB to the 1.x line (`surrealdb.js@^1.0.0` rejects v2/v3)
- Shell-less surrealdb image — readiness via `/surreal isready`

## Use case

Team member takes private AI-assisted notes; notes are searchable via the content graph without leaving self-hosted infra.

## Related

- → `surrealdb-store.md` — Storage layer
- → `../../diagrams/blinko-surrealdb.md` — Topology + data flow
- → `../guides/deployment.md` — Deployment method
- → `../objects/tool.md` — Tool object type