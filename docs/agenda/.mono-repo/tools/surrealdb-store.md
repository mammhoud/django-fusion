---
Object type: Tool
Tags: tool, surrealdb, database, blinko
Status: Active
Category: Data
Related Features: documentation-system
Related Plans: deployment
---

# SurrealDB — Blinko Document Store

> **Description:** The SurrealDB 1.x document/graph store backing Blinko AI notes — auth records, content graph, and query engine.

## Method

- Started via `surrealdb start --user root --pass <pass> file:/data/blinko.db`
- v1-compatible upsert semantics (`UPDATE ... MERGE` on explicit record IDs) in `server/lib/scheduler.ts`
- M1–M4 migration moved auth, content graph, and queries off Prisma/PostgreSQL

## Boundary

- Pin to 1.x line; v2/v3 engines rejected by the bundled `surrealdb.js@^1.0.0` (`UnsupportedVersion`)
- Shell-less scratch image — use `/surreal isready` for healthchecks

## Use case

Blinko persists notes and their links/relations; searches traverse the graph without a separate relational DB.

## Related

- → `blinko-notes.md` — Consumer
- → `../../diagrams/blinko-surrealdb.md` — Topology
- → `../objects/tool.md` — Tool object type