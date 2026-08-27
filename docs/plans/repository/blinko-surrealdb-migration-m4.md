# Blinko — Prisma → SurrealDB Migration, Milestone 4 (Final Cutover)

> **Tags:** #blinko #migration #surrealdb #prisma #m4 #cutover
> **Last updated:** 2026-08-27 | **Status:** Plan — not yet implemented
> **Scope:** Make Surreal the **only** datastore. Drop every Prisma fallback and
> mirror, migrate the remaining tables (config, conversations/messages,
> notifications, follows, fonts, AI providers/models/MCP, jobs, plugin, cache),
> retrofit **deterministic** `accounts:<id>` record ids (today accounts use
> random Surreal ids behind `legacyPrismaId`), switch the JWT `sub` semantics,
> then delete `prisma/` and the `prisma:*` scripts.
> **Depends on:** M1–M3 committed on `surrealdb/migration-auth-first`
> (`ee502323` … `586b5bf3`) in the vendored checkout
> `application/tools/blinko/blinko/`; M3 parity harness green (19/19).

---

## 1. Purpose

M1–M3 built the Surreal side of the dual-store contract: adapters with
Surreal-first point reads + Prisma-first writes mirrored to Surreal, a
SurrealQL query engine for the note list, and a parity harness proving both
stores return identical results. Throughout, Postgres/Prisma stayed the
source of truth and the rollback path.

M4 is the **cutover**: Surreal becomes the single source of truth. The
fallback/mirror scaffolding is removed, the tables still living only in
Postgres get Surreal homes, record ids become fully deterministic (so the
`legacyPrismaId` indirection and the `_accountRef` lookup disappear), and
Prisma is deleted from the repo. After M4 there is one store, one schema
(Surreal), one set of query paths — and the rollback is a restore, not a
flip of an env var.

This is the highest-risk milestone because it is **irreversible in code**
(no Prisma to fall back to), so it is sequenced: deterministic ids first
(with a re-key migration), then the remaining-table adapters (each verified
by parity-style tests against the live Surreal), then fallback removal per
model, then Prisma deletion — with a full data-migration + verification gate
before the last step.

---

## 2. Current State (verified in checkout, 2026-08-27)

### 2.1 What Surreal already owns (M1–M3)

Adapters in `server/lib/repos/` — all dual-store (Surreal-first read with
Prisma fallback; Prisma-first write with best-effort Surreal mirror):

| Table | Adapter | Notes |
|---|---|---|
| `accounts` | `accounts.ts` | **random Surreal ids** (`accounts:<uuid>`) + `legacyPrismaId` mapping |
| `notes` | `notes.ts` | deterministic `notes:<id>`; `tags`/`references`/`referencedBy` folded in |
| `attachments` | `attachments.ts` | deterministic `attachments:<id>`; `attachmentPaths` index on the note |
| `tag` | `tags.ts` | deterministic `tag:<id>` |
| `comments` | `comments.ts` | deterministic `comments:<id>` |
| `noteHistory` | mirror helper in `notes.ts` | deterministic `noteHistory:<id>` |
| `noteInternalShare` | folded into `internalShares`/`internalShareCanEdit` on the note | join table stays in Postgres for now |

Plus the M3 query engine (`notes-query.ts`) serving `notes.list` shapes from
Surreal, gated by `SURREALDB_URL`.

### 2.2 What still lives only in Postgres (grep-verified counts)

Direct `prisma.<model>.` usage in `server/` (excluding tests):

| Model | Uses | Where |
|---|---|---|
| `config` | 20 | `config.ts` router (`getGlobalConfig`), `helper.ts` (JWT secret), `note.ts` (order-by config), webhook |
| `tagsToNote` | 16 | `note.ts` upsert/tag-delete paths (read + write) |
| `noteReference` | 11 | `note.ts` reference flows |
| `noteInternalShare` | 9 | `note.ts` share flows |
| `conversation` / `message` | 10 / 11 | chat (`conversation.ts`, `message.ts`) |
| `notifications` | 8 | `notification.ts` |
| `cache` | 9 | jobs (`dbjob`, `recommandJob`, `rebuildEmbeddingJob`), `follows.ts` |
| `fonts` | 8 | `font.ts` |
| `aiProviders` / `aiModels` | 8 / 11 | `ai.ts`, `config.ts`, `mcpServers.ts` |
| `mcpServers` | 11 | `mcpServers.ts`, `McpClientManager.ts` |
| `aiScheduledTask` | 12 | `aiScheduledTask.ts`, `aiScheduledTaskJob.ts` |
| `plugin` | 4 | `plugin.ts` |
| `follows` | 6 | `follows.ts` |

Also: `analytics.ts` uses `prisma.$queryRaw` (Postgres SQL aggregation),
`attachment.ts` folder view uses `DISTINCT ON` raw SQL (documented M3
non-goal), and `session` (0 uses) is dead.

### 2.3 Id scheme today

- Content tables: deterministic record ids (`notes:<id>`, `tag:<id>`, …)
  with the numeric Prisma id embedded in the record id — `toNote`/`toTag`
  etc. already read it via `/(\d+)$/` on the record id.
- `accounts`: **Surreal-generated random ids**; the numeric Prisma id is
  stored in `legacyPrismaId` (21 references across repos + the query engine).
  `_accountRef.ts` resolves numeric → `accounts:<uuid>` with a cached
  `SELECT VALUE id ... WHERE legacyPrismaId = $id` lookup.
- JWT `sub` = numeric account id string (`helper.ts` `generateToken`/
  `generateApiToken`); `ctx.id = token.sub` (string), routers do
  `Number(ctx.id)`.

### 2.4 Test surface

- `query-parity.test.ts` (M3) — real Prisma + live Surreal, 19 tests, green.
- `surrealdb-repos.test.ts` (M2) — mocked Prisma + live Surreal, 9 tests.
- `attachment.deleteMany.test.ts`, `sanitizeUploadFileName.test.ts`,
  `integration/file/upload.test.ts` (mocked prisma), E2E upload suite
  (live server). Full run: 62 pass / 0 fail.

---

## 3. Goals & Non-Goals (Milestone 4)

### Goals

1. **Deterministic accounts ids** — accounts become `accounts:<numericId>`,
   `legacyPrismaId` deleted everywhere, `_accountRef` becomes a pure
   `accounts:${id}` string (no lookup, no cache).
2. **Remaining tables on Surreal** — config, tagsToNote/noteReference/
   noteInternalShare join reads, conversations, messages, notifications,
   follows, fonts, aiProviders, aiModels, mcpServers, aiScheduledTask,
   plugin, cache get Surreal adapters or are deliberately retired.
3. **Drop the dual-store pattern** — adapters become Surreal-only (no Prisma
   fallback, no mirror); routers stop importing `server/prisma.ts`.
4. **JWT `sub` semantics** — `sub` stays the numeric id (now equal to the
   Surreal record id), so `ctx.id`/`Number(ctx.id)` and the frontend id
   contract are unchanged; only the server-side id plumbing simplifies.
5. **Delete Prisma** — `prisma/` directory, `@prisma/client` dependency,
   `prisma:*` root scripts, and `server/prisma.ts` removed; Postgres
   container can be dropped from the dev compose.
6. **Verification gate** — parity harness re-pointed at Surreal-only, full
   suite green, live smoke of auth + note CRUD + chat + config after cutover.

### Non-Goals

- **Schema redesign** — M4 keeps Surreal's current record shapes; it only
  changes accounts ids, adds the missing tables, and removes Postgres.
  Deeper normalization (e.g. separate `noteTags`/`noteReferences` tables
  instead of folded arrays) is post-M4.
- **Vector/AI search rewrite** — embedding queries and the MCP/AI pipeline
  are ported 1:1 (same semantics), not re-architected.
- **Analytics raw-SQL aggregation** — `analytics.ts` `$queryRaw` and the
  attachment folder `DISTINCT ON` are ported to SurrealQL **or** explicitly
  marked as deferred with a greppable boundary (see §4.6) — decide in §5.
- **Redis adoption** — the `cache` table moves to a Surreal `cache` table,
  not Redis (Redis stays a queue/cache backend, out of scope here).

---

## 4. Architecture Decisions

### 4.1 Deterministic accounts ids (do FIRST — everything depends on it)

**Decision:** re-key accounts from `accounts:<uuid>` to `accounts:<numericId>`.

Why it's safe: content tables already use `notes:<id>`-style ids and the
frontend/API contract is the numeric id (zod schemas, JWT `sub`, `Number(ctx.id)`).
Making accounts match removes the only remaining indirection.

Steps:
1. **Re-key migration script** (`scripts/migrate/accounts-rekey.ts`, new):
   - For each `accounts` record with `legacyPrismaId = N` and id `accounts:<uuid>`:
     `CREATE ONLY accounts:N CONTENT $payload` (copy fields, drop
     `legacyPrismaId`), then `DELETE accounts:<uuid>`, then rewrite every
     ref: `notes.account`, `comments.account`, `attachments.account`,
     `tag.accountId`→`account`, `internalShares`, `internalShareCanEdit`,
     `config.userId`→`account`, `follows`, `notifications`, `conversation`,
     `message.account`, `message.receiveAccountId`, `aiScheduledTask`.
   - Idempotent (skip when `accounts:N` exists).
   - Wrap in a transaction where Surreal v1 allows; otherwise order so a
     crash leaves a consistent-enough state to re-run (skip-existing).
2. **Adapter change** (`accounts.ts`): `createAccount` uses
   `CREATE ONLY accounts:${id} CONTENT $payload`; `findAccountById` uses
   `SELECT * FROM accounts:${id}`; delete/update use `accounts:${id}`.
   Drop `legacyPrismaId` from payloads and `toAccount`.
3. **`_accountRef.ts` becomes a pure function**: `return \`accounts:${id}\``
   — delete the query + cache (or keep the file as a thin helper so call
   sites don't churn, exporting the same signature).
4. **Query engine** (`notes-query.ts`): `accountUuid`/`meUuid` logic
   collapses to `accounts:${me}`; internalShares include reads
   `legacyPrismaId` from the record id.

### 4.2 Remaining-table adapters (one per model, same shape as M1/M2)

New files in `server/lib/repos/`:

- `config.ts` — deterministic `config:<id>`; `getGlobalConfig` reads
  `SELECT * FROM config` (same reduce logic); JWT secret read/create in
  `helper.ts` moved here; `userId` becomes an `account` record ref.
- `conversation.ts` / `message.ts` — deterministic ids; `account` refs
  (both `message.account` and `message.receiveAccountId`).
- `notifications.ts`, `follows.ts`, `plugin.ts`, `fonts.ts` — deterministic
  ids; `account` refs where the model has FKs.
- `aiProviders.ts`, `aiModels.ts`, `mcpServers.ts` — deterministic ids;
  port `McpClientManager.ts` reads; `aiModels.provider` becomes a
  `aiProviders:<id>` ref.
- `aiScheduledTask.ts` — deterministic ids + `account` ref; port the job
  (see §4.5).
- `cache.ts` — deterministic `cache:<id>` keyed by the existing string key
  (add a `key` field + unique index via Surreal `DEFINE INDEX`), port
  `upsert`/`findUnique`/`delete` semantics.

Each adapter is **Surreal-only** (no Prisma fallback) because by the time
each is wired, the corresponding Prisma usage is being deleted in the same
change. Join-table reads (`tagsToNote`/`noteReference`/`noteInternalShare`)
that the routers still do get replaced by reads against the folded Surreal
arrays (they already exist on the note records) — see §4.3.

### 4.3 Replace join-table reads with folded-array reads

The M2 mirrors already fold `tags`/`references`/`referencedBy`/
`internalShares` onto the note record, so the remaining `prisma.tagsToNote`
/`prisma.noteReference`/`prisma.noteInternalShare` calls in `note.ts` become:

- `prisma.tagsToNote.findMany({where:{tagId}})` → `SELECT * FROM notes WHERE
  tag:<id> IN tags` (the M3 engine already does this).
- `prisma.tagsToNote.findFirst({where:{tagId,noteId}})` / create/delete →
  `SET tags = tags - tag:<id>` / `array::union` on `notes:<id>` (M2
  `addNoteTag`/`removeNoteTag` already exist).
- `prisma.noteReference.findMany/createMany/deleteMany` → add/remove on
  `notes.<id>.references`/`referencedBy` (+ the `referencesAt` map from M3).
- `prisma.noteInternalShare.*` → `internalShares`/`internalShareCanEdit`
  array ops (M3 mirrors already exist).

Net effect: the join tables stop being read at all; their Postgres rows are
already redundant (kept only because Prisma was the writer).

### 4.4 JWT `sub` stays numeric — the "switch" is internal

`sub: user.id.toString()` keeps working because `accounts:<id>` uses the
same numeric id. The real change is plumbing:

- `server/context.ts` `ctx.id` stays `token.sub` (numeric string).
- Routers' `Number(ctx.id)` stays.
- `_accountRef` (now `accounts:${id}`) makes every `account` ref correct
  with no DB round-trip.
- The **frontend is untouched** — no id-type change crosses the API.

### 4.5 Jobs & AI pipeline

Jobs (`server/jobs/*`) read `prisma.cache`, `prisma.aiScheduledTask`,
`prisma.conversation`/`prisma.message` (AI chat). Port each to the new
adapters; keep scheduling (cron) unchanged. `aiScheduledTaskJob.ts` +
`baseScheduleJob.ts` swap their prisma calls for adapter calls. The MCP
manager (`McpClientManager.ts`) swaps `prisma.mcpServers` for the adapter.

### 4.6 The two raw-SQL holdouts — decide explicitly

1. **`analytics.ts` `$queryRaw`** (daily/word stats): port to SurrealQL
   (`SELECT count() GROUP BY time::day(createdAt)` etc.) — small, do it.
2. **`attachment.ts` folder view** (`DISTINCT ON (folder_name)` on the raw
   path prefix): port to SurrealQL with `array::group`/`count()` or a
   Surreal `DEFINE`-level aggregation. If it proves awkward in v1.5.6,
   mark the branch `// Prisma query read (M4 boundary)` and keep the
   Postgres read for that single branch — **explicitly deferred, greppable,
   and listed in the PR description** rather than silently left behind.

### 4.7 Deletion order (safety)

Never delete Prisma while any router still imports `server/prisma.ts`.
Sequence per model: (a) adapter + router swap in one change, (b) grep
`prisma.<model>` == 0, (c) only then the global `prisma/` removal. The final
step — `rm -rf prisma/`, drop `@prisma/client` + `prisma:*` scripts,
delete `server/prisma.ts` — requires a zero-`prisma` grep across
`server/` + `shared/` + `scripts/` (excluding `prisma-to-surreal.ts`, which
is deleted too since its job is done).

---

## 5. Implementation Steps

### 5.1 Branch

Continue on `surrealdb/migration-auth-first` (the PR branch) or open
`surrealdb/migration-cutover` from it. Recommend a new branch name so the
M1–M3 PR stays reviewable; the M4 PR depends on M1–M3 being merged first.

### 5.2 Phase A — deterministic accounts ids (foundation)

1. `scripts/migrate/accounts-rekey.ts` (new, idempotent, dry-run flag).
2. `accounts.ts` adapter: deterministic ids; drop `legacyPrismaId`.
3. `_accountRef.ts` → pure `accounts:${id}` (keep export signature).
4. `notes-query.ts` + `notes.ts` + `attachments.ts` + `comments.ts` +
   `tags.ts`: drop `legacyPrismaId` reads, use record-id extraction.
5. Update migration script `prisma-to-surreal.ts` accounts step to create
   `accounts:<id>` directly (for fresh environments).
6. Tests: `surrealdb-repos.test.ts` + `query-parity.test.ts` still green;
   re-key script run against a copy of the dev Surreal DB; verify refs.

### 5.3 Phase B — remaining tables (each a small PR-sized change)

Order (cheapest, most-contained first):

1. `config` (blocks everything: JWT secret, order-by, webhooks).
2. `notifications`, `follows`, `plugin`, `fonts`.
3. `conversation` + `message` (chat).
4. `aiProviders` + `aiModels` + `mcpServers` (+ `McpClientManager`).
5. `aiScheduledTask` + jobs (`dbjob`, `recommandJob`, `rebuildEmbeddingJob`,
   `aiScheduledTaskJob`).
6. `cache` adapter + job swaps.
7. Join-table read replacements in `note.ts` (§4.3) — fold-in already
   exists, so these are read-path swaps.
8. `analytics.ts` SurrealQL aggregation; attachment folder branch (§4.6).

### 5.4 Phase C — drop the dual-store pattern

Per adapter, delete: the `isSurrealEnabled()` gates, the Prisma fallback in
reads, and the Prisma-first write + mirror in writes. Routers drop
`import { prisma } from '../prisma'` once their last call is swapped.
`connectSurreal()` moves from "if env set" to unconditional bootstrap; a
missing Surreal connection becomes a hard startup error.

### 5.5 Phase D — delete Prisma

1. `rm -rf prisma/` (schema, migrations, seed, defaultFonts, seedData).
2. Root `package.json`: remove `prisma:generate`, `prisma:migrate:dev`,
   `prisma:migrate:deploy`, `prisma:studio`, `build:seed`, the
   `postinstall` prisma hook, and `@prisma/client` from dependencies.
3. `server/prisma.ts` deleted; `shared/lib/prismaZodType.ts` regenerated
   by hand (zod schemas already match the Surreal record shapes) or replaced
   by explicit schema files.
4. Delete `scripts/migrate/prisma-to-surreal.ts` (job done) — keep
   `accounts-rekey.ts` only if a re-key is still useful for legacy data.
5. Tests: delete/replace mocks of `../../../prisma` (the M2 unit test gets a
   Surreal-only rewrite; the parity harness's Prisma reference side is
   replaced by golden snapshots or Surreal-only assertions — see §6).
6. Drop Postgres from the blinko dev compose + README/DEV.md.

### 5.6 Docs

- `README.md`/`DEV.md`: Surreal is the only store; new env contract
  (`SURREALDB_URL` required); how to start/backup/restore Surreal;
  migration runbook for existing installs (re-key + remaining tables).
- Update M3 plan §9 + this plan's status; registry row in `docs/plans/README.md`.

---

## 6. Tests & Manual Validation

### Parity harness re-point

The M3 harness compares Prisma vs Surreal; after M4 there is no Prisma
reference. Convert it to:

- **Golden snapshot parity** — freeze the current Prisma-vs-Surreal outputs
  (already proven equal) as JSON fixtures; Surreal-only tests assert the
  engine still matches the fixtures after cutover.
- Or keep a `scripts/migrate/prisma-to-surreal.ts` **read-only** copy purely
  as the reference oracle in tests until the fixtures are frozen (then
  delete it). Recommend the fixture route (no Postgres needed in CI).

### Test suite changes

- `surrealdb-repos.test.ts` — drop the `mock.module('../../../prisma')`;
  tests become Surreal-only against live Surreal (same describe.skipIf gate).
- `attachment.deleteMany.test.ts` / `integration/file/upload.test.ts` —
  re-point mocks at the Surreal adapters or make them live-Surreal tests.
- E2E upload suite — unchanged (server still on :1111), now Surreal-backed.
- New adapter tests for config/chat/notifications/follows/fonts/AI/MCP/cache
  (Surreal-only, mirroring the M2 pattern).
- `query-parity.test.ts` — fixtures (above).

### Manual smoke (live, Surreal v1.5.6, no Postgres)

1. Fresh Surreal + `bun scripts/migrate/accounts-rekey.ts` (or fresh
   migration) → verify accounts carry `accounts:<id>` ids and all refs
   resolve (run the existing live smoke: signup/login, note CRUD with
   tags/attachments/comments/refs, internal share, chat, config save/load).
2. Every router touched in §5.3 exercised via curl/browser; watch the log
   for zero `prisma` references and zero adapter errors.
3. Restart the server → no Prisma import, no Postgres connection.
4. `docker compose down` the Postgres container; server + frontend still
   fully functional against Surreal alone.

### Rollback

- **Code:** revert the M4 branch (M1–M3 dual-store code still in history)
  and re-point env — but note Postgres data was never the source of truth
  for M4-written records. Realistically: **backup Surreal before the
  cutover** (`surrealdb export`) and restore if M4 is rolled back.
- **Data:** re-key script is idempotent and non-destructive to Surreal
  source rows until the delete step; run with `--dry-run` first. Keep the
  Postgres container (unused) until M4 is verified, then drop it.

---

## 7. PR Checklist (for the blinko repo PR)

- [ ] Branch `surrealdb/migration-cutover` (or continued) from merged M1–M3.
- [ ] `scripts/migrate/accounts-rekey.ts` — idempotent, dry-run, ref rewrite.
- [ ] Accounts deterministic ids: adapter + `_accountRef` pure + query engine;
      `legacyPrismaId` grep == 0.
- [ ] Remaining-table adapters (config, chat, notifications, follows, fonts,
      AI, MCP, plugin, cache) + router swaps; `prisma.<model>` grep == 0 per
      model.
- [ ] Join-table reads replaced with folded-array reads in `note.ts`.
- [ ] Analytics + attachment folder branches ported or explicitly marked
      `// Prisma query read (M4 boundary)` in the PR description.
- [ ] Dual-store pattern removed: no `isSurrealEnabled` gates, no mirrors.
- [ ] `prisma/` + `prisma:*` scripts + `@prisma/client` + `server/prisma.ts`
      deleted; grep for `prisma` (case-sensitive, excluding docs) == 0.
- [ ] Parity harness → golden fixtures; unit/integration/E2E suite green.
- [ ] README/DEV.md updated (Surreal-only, runbook, backup/restore).
- [ ] PR title: `feat(db): cut over to SurrealDB as the only datastore (step 4)`,
      with the §6 smoke results + rollback/backup notes in the body.

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Accounts re-key breaks refs in prod data | Idempotent script, `--dry-run`, ref-rewrite pass, smoke against a copy first |
| Chat/AI/MCP tables are wide (many fields) | Port field-for-field from the Prisma zod schemas; keep shapes identical |
| `config` is load-bearing (JWT secret, order-by) | Port first (§5.3 step 1); verify login + config save/load before anything else |
| Analytics/folder raw SQL awkward in Surreal v1.5.6 | Explicit defer with greppable `// Prisma query read (M4 boundary)` marker + PR note |
| Surreal v1 lacks multi-doc transactions (re-key safety) | Order writes so re-runs are safe (skip-existing); document the window |
| Rollback after Prisma deletion is impossible in code | Backup Surreal before cutover; keep unused Postgres container until verified |

---

## 9. Follow-up (post-M4)

- **M5 — engine/SDK upgrade:** bump `surrealdb.js` + engine to v2/v3 for
  `FULLTEXT ANALYZER` indexes (replace `string::lowercase CONTAINS`),
  multi-doc transactions, and Surreal-native backups; add Surreal to the
  deployed `application/tools/blinko` compose + backup/restore runbook.
- **Schema normalization:** split folded arrays into proper
  `noteTags`/`noteReferences` Surreal tables if query performance demands.
- **Analytics enrichment:** move the deferred raw-SQL branches onto Surreal
  once the v2 engine lands.
