# Phase 3 — Prisma / PostgreSQL Removal from Blinko Fork

**Status:** Planned  
**Scope:** `application/tools/PlanInc/planing/`  
**Owner:** Backend  
**Depends on:** Phase 2 (runtime already SurrealDB-only)  
**Can run in parallel with:** Phase 4, Phase 5

---

## Objective

Remove all Prisma, `@prisma/client`, `pg-boss`, and PostgreSQL references from
the `planing/` (Blinko fork) directory so it no longer installs or references
a database that PlanInc does not use. The active runtime is `runtime/server.mjs`
(SurrealDB); the Blinko fork is retained only as a UI component source.

---

## What Needs Removing

### In `planing/server/index.ts`

```ts
// REMOVE all of these
import { getPgBoss, stopPgBoss } from './lib/pgBoss';
import { ArchiveJob }            from './jobs/archivejob';
import { DBJob }                 from './jobs/dbjob';
import { RebuildEmbeddingJob }   from './jobs/rebuildEmbeddingJob';
import { RecommandJob }          from './jobs/recommandJob';
import { AIScheduledTaskJob }    from './jobs/aiScheduledTaskJob';

// REMOVE from bootstrap()
await initializeJobs();

// REMOVE from SIGTERM / SIGINT handlers
await stopPgBoss();
```

### In `planing/server/package.json`

Remove from `dependencies`:
```json
"@prisma/client": "^5.22.0",
"@prisma/engines": "^6.5.0",
"pg-boss": "*"
```

Remove from `devDependencies`:
```json
"prisma": "5.22.0"
```

### In `planing/package.json` (root)

Remove scripts:
```json
"postinstall": "turbo run prisma:generate --filter=@blinko/backend",
"prisma:generate": "cd prisma && prisma generate",
"prisma:migrate:dev": "cd prisma && prisma migrate dev",
"prisma:migrate:deploy": "cd prisma && prisma migrate deploy",
"prisma:studio": "cd prisma && prisma studio",
"build:seed": "tsup prisma/seed.ts --outDir dist",
"seed": "bun dist/seed.js"
```

### Files to archive (rename, not delete — preserve history)

| File | Action |
|---|---|
| `planing/prisma/schema.prisma` | Rename to `schema.prisma.archive` |
| `planing/server/prisma.ts` | Delete (PrismaClient singleton) |
| `planing/server/lib/pgBoss.ts` | Delete |
| `planing/server/jobs/archivejob.ts` | Delete |
| `planing/server/jobs/dbjob.ts` | Delete |
| `planing/server/jobs/rebuildEmbeddingJob.ts` | Delete |
| `planing/server/jobs/recommandJob.ts` | Delete |
| `planing/server/jobs/aiScheduledTaskJob.ts` | Delete |

---

## Full Audit Command

Run before and after to confirm zero remaining references:

```bash
rg '@prisma/client|PrismaClient|pg-boss|getPgBoss|DATABASE_URL|POSTGRES' \
  application/tools/PlanInc/planing/server/ \
  --type ts
```

Expected after cleanup: **0 matches**.

---

## Prisma Schema Archive

The full `schema.prisma` (21 models) is preserved at
`planing/prisma/schema.prisma.archive` for reference. Key models and their
SurrealDB equivalents in `runtime/server.mjs`:

| Prisma model | SurrealDB table in runtime |
|---|---|
| `accounts` | `account` |
| `notes` | `notes` |
| `attachments` | `attachments` |
| `tag` + `tagsToNote` | `tag` + `tagged_with` (RELATE edge) |
| `config` | `workspace` (settings fields) |
| `noteReference` | `note_link` (RELATE edge) |
| `comments` | `note_comment` |
| `noteHistory` | (not yet ported — backlog) |
| `noteInternalShare` | `workspace_member` role scoping |
| `conversation` + `message` | `chat_session` + `chat_message` |
| `aiProviders` + `aiModels` | `ai_provider` |
| `aiScheduledTask` | `ai_job` |
| `mcpServers` | `integration` |
| `session` | JWT-based (no DB session table) |
| `follows` | `integration` (external feed) |
| `notifications` | `note_activity` |
| `plugin` | `integration` |
| `cache` | (in-memory or SurrealDB `cache` table) |
| `fonts` | (static assets, not in SurrealDB) |

---

## Verification Steps

```bash
# 1. Install without prisma
cd application/tools/PlanInc/planing
bun install
# Confirm @prisma/client NOT in node_modules

# 2. Start backend — no prisma:generate, no pg-boss
bun run dev:backend
# Should start without errors and without any pg-boss log lines

# 3. Confirm zero prisma references
rg '@prisma/client|PrismaClient|pg-boss' planing/server/ --type ts
# → 0 matches

# 4. Confirm postinstall no longer runs prisma:generate
bun install 2>&1 | grep -i prisma
# → no output
```

---

## Impact on Frontend

The Blinko frontend (`planing/app/src/`) uses the tRPC client (`api.*`) to
communicate with the backend. **None of the frontend stores reference Prisma
directly** — they only call tRPC endpoints. As long as the tRPC routers
continue to work (they delegate to `prisma.ts` internally), the frontend is
unaffected by this cleanup.

However: since `planing/server/prisma.ts` is the single source of PrismaClient,
all 18 tRPC sub-routers import it. After removal, those routers will need to
either:
1. Be redirected to `runtime/server.mjs` REST endpoints (preferred for the
   interim step), or
2. Be replaced wholesale by Tauri commands (Phase 1 long-term).

**Interim approach (this phase):** Keep the tRPC routers but replace
`prisma.*` calls with `fetch()` calls to `runtime/server.mjs` REST endpoints
running on `localhost:1111`. This keeps the frontend working without Prisma.

---

## Notes

- `pg-boss` uses PostgreSQL as its job queue backing store — it fails to start
  without `DATABASE_URL`. Removing it eliminates the startup error entirely.
- The `planing/prisma/migrations/` directory can be kept as historical
  documentation but should not be run.
- Do not delete `planing/server/routerTrpc/` — these routers are the tRPC
  API layer and will be migrated to SurrealDB REST calls, not deleted.
