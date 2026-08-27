# Blinko — Prisma → SurrealDB Migration, Milestone 3 (Query Engine)

> **Tags:** #blinko #migration #surrealdb #prisma #m3 #query-engine
> **Last updated:** 2026-08-27 | **Status:** Implemented — parity harness green
>   (commit `586b5bf3` on `surrealdb/migration-auth-first`); router flips for
>   the remaining list endpoints + `notes.list` cutover pending M4.
> **Scope:** Port the **list/query where-builders** — `notes.list` first (the
> hardest), then the other list endpoints — from Prisma to SurrealQL, with a
> parity harness that proves both stores return identical results before any
> Surreal-only cutover. Also migrate the two supporting tables the query
> engine needs (`noteHistory`, `noteInternalShare`).
> **Depends on:** [`blinko-surrealdb-migration-m2.md`](blinko-surrealdb-migration-m2.md)
> (M2, committed `b919d921` + `b8c3de01` on `surrealdb/migration-auth-first`
> in the vendored checkout `application/tools/blinko/blinko/`).

---

## 1. Purpose

M2 delivered the content-graph **writes + point reads** on Surreal while
leaving every list-style query on Prisma (§4.4 of the M2 plan). M3 closes
that gap: it ports the **where-builder / query engine** to SurrealQL so the
main read path — the note list with search, filters, ordering, deep includes
and pagination — is served from Surreal.

This is the milestone where behavior can silently change, so the central
artifact is a **parity harness**: run the same list input against Prisma and
Surreal, diff the results, and only flip a list endpoint to Surreal-first
after the harness is green. M3 keeps the dual-store pattern (Surreal-first +
Prisma fallback) and never drops the fallback — that is M4's cutover.

---

## 2. Current State (verified in checkout, 2026-08-27)

### 2.1 The where-builders to port (grep-verified, `server/routerTrpc/note.ts`)

| Endpoint | Where complexity | Deep include | Notes |
|---|---|---|---|
| `notes.list` (line 46) | **Highest** — owner-OR-internalShare, `searchText` 4-way OR (content + attachment path), `isRecycle`/`isArchived`/`type`/`isShare`, `tagId` via tagsToNote, `withFile`/`withoutTag`/`withLink`/`hasTodo`, `startDate`/`endDate`, config-driven `createdAt`/`updatedAt` order, `skip/take` | tags→tag, attachments (ordered), comments→account, references→toNote, referencedBy→fromNote, `_count{comments,histories}`, internalShares | The reference implementation |
| `publicList` (276) | `isShare && !sharePassword && (expiry null \|\| future)` + optional content contains | tags→tag, account, attachments, `_count.comments` | `cache.wrap` 5s TTL |
| `listByIds` (360) | `id IN ids && accountId` | tags, attachments, references, referencedBy, `_count` | |
| `publicDetail` (453) | `shareEncryptedUrl && isShare && !isRecycle` | account, references, tags, attachments, `_count` | password/expiry handled in JS after fetch |
| `detail` (589) | `id && (owner OR internalShare)` | tags, attachments, references, referencedBy, `_count` | point-ish read, same where as list |
| `dailyReviewNoteList` (690) | `createdAt > 24h && !isReviewed && !isArchived && !isRecycle && accountId` | attachments | Simple |
| `randomNoteList` (715) | **Raw SQL** `ORDER BY RANDOM()` + attachments by noteId | attachments | `$queryRaw` — port to `ORDER BY rand()` |
| `relatedNotes` (768) | AI vector query (`AiModelFactory.queryVector`) — external store, not Prisma | — | Only the initial `findUnique` is Prisma |
| `reviewNote` (843) | Point write | — | Already has adapter surface |
| `noteReferenceList` (1383) | `noteReference.where(fromNoteId/toNoteId)` ordered by `createdAt desc` | toNote/fromNote with attachments+tags+refs | **Needs `referenceCreatedAt`** — see §4.4 |

### 2.2 Other list endpoints

| File | Endpoint | Where |
|---|---|---|
| `tag.ts` | `tags.list` | `accountId` + `sortOrder asc` + `distinct id` — trivial |
| `attachment.ts` | `attachments.list` | search: owner-OR-share + name/path contains; folder branch: **raw SQL with CTE + `DISTINCT ON`** (Postgres-specific) |
| `comment.ts` | `comments.list` | `noteId` + pagination + `checkNoteAccess` gate; include account/replies |

### 2.3 Supporting data the query engine needs (NOT yet in Surreal)

- **`noteInternalShare`** — the `notes.list`/`detail`/`checkNoteAccess` owner-
  OR-share condition depends on it. M2 didn't migrate or mirror it.
- **`noteHistory`** — `_count.histories` in the list output needs it.
- **`noteReference.createdAt`** — `noteReferenceList` returns
  `referenceCreatedAt`; M2 folded `references`/`referencedBy` into plain
  record-id arrays, dropping the timestamp.

### 2.4 Engine constraint (verified in M1/M2 smoke testing)

The checkout pins `surrealdb.js@^1.0.0`, which rejects engines outside
`>=1.4.2 <2.0.0` (`UnsupportedVersion`); the local dev engine is
`surrealdb/surrealdb:v1.5.6`. **SurrealDB v1 has no full-text index**
(`DEFINE INDEX … FULLTEXT ANALYZER` / `SEARCH ANALYZER` arrived in v2). So:

- `contains, mode: 'insensitive'` → `string::lowercase(content) CONTAINS string::lowercase($q)`
  (substring match, case-folded — identical semantics to Postgres `ILIKE %q%`).
- No `some`/`none` relation quantifiers — use `array::*` functions
  (`array::contains`, `array::len`, `array::filter`) over the folded arrays.

---

## 3. Goals & Non-Goals (Milestone 3)

**Goals**

1. A reusable **SurrealQL where-builder** for notes
   (`server/lib/repos/notes-query.ts`) that reproduces the Prisma
   `notes.list` semantics exactly, with parameterized variables (no string
   interpolation of user input).
2. Deep-include normalization: fetch the page of note records, then resolve
   the include graph (tags, attachments, comments+account, references/
   referencedBy, `_count`, internalShares, owner) into the exact Prisma
   response shapes.
3. Port the remaining list endpoints: `publicList`, `listByIds`, `detail`,
   `publicDetail`, `dailyReviewNoteList`, `randomNoteList`,
   `noteReferenceList`, `tag.list`, `comments.list`, `attachments.list`
   (search branch; the folder CTE branch stays on Prisma — §4.5).
4. Migrate `noteHistory` + `noteInternalShare` (and backfill
   `referenceCreatedAt`) so the engine has the data it needs.
5. **Parity harness** (`server/__tests__/unit/lib/query-parity.test.ts`):
   run identical list inputs through Prisma and Surreal, assert deep-equal
   outputs. This is the gate for flipping each endpoint Surreal-first.
6. Flip endpoints to Surreal-first **with Prisma fallback kept intact**
   (same `isSurrealEnabled()` + try/catch pattern as M1/M2).

**Non-goals (later milestones)**

- Dropping the Prisma fallback / making Surreal authoritative (M4).
- `attachments.list` folder view (raw SQL CTE + `DISTINCT ON` — Postgres-
  specific; keep on Prisma and document).
- AI/vector queries (`relatedNotes` keyword extraction + `queryVector` stay
  on the external vector store).
- Analytics, jobs batch reads, `cache` table, config table.
- Engine upgrade to v2/v3 (would unblock FTS indexes but is a separate
  change — SDK bump + re-verify; tracked as M5 follow-up).

---

## 4. Architecture Decisions

### 4.1 Dual-store list reads with a parity gate

List reads become: try Surreal (if enabled) → if the query errors or returns
fewer records than expected, **fall back to Prisma** and log
`[surrealdb] notes.list query failed, falling back to Prisma`. The parity
harness (§6) must be green before each endpoint flips. Until the harness for
an endpoint exists, that endpoint stays on Prisma — the flip list in §5.4
orders them.

### 4.2 Where-builder shape: parameterized SurrealQL from the same inputs

`notes.list` builds `Prisma.notesWhereInput` imperatively. The M3 builder
takes the same zod-validated input + `ctx.id` and emits
`{ sql, vars }` for `query_raw`, e.g.:

```sql
SELECT * FROM notes
WHERE (legacyPrismaAccountId = $me
       OR $me IN internalShares)
  AND isRecycle = $isRecycle
  AND string::lowercase(content) CONTAINS string::lowercase($searchText)
  ...
ORDER BY isTop DESC, sortOrder ASC, createdAt DESC
LIMIT $size START $skip;
```

- `tagId` filter → `$tagId IN tags` (folded array) — no tagsToNote join needed.
- `withFile` → `array::len(attachments) > 0` (folded array).
- `withoutTag` → `array::len(tags) == 0`.
- `withLink`/`hasTodo` → `string::lowercase(content) CONTAINS 'http://'` /
  `CONTAINS '- [ ]'` … (exactly the Prisma OR-branches, same case-folding).
- `startDate`/`endDate` → `createdAt >= $start AND createdAt <= $end`.
- `searchText` 4-way OR reproduces the Prisma branch order: owner+content,
  owner+attachment path, shared+content, shared+attachment path. Attachment
  path search needs a join in Surreal — see §4.3.

Keep every filter branch in a function (`withOwnerOrShares`, `withSearch`,
`withTagId`, …) that appends to a `WHERE` clause builder, mirroring the
Prisma imperative builder 1:1 so the parity diff is meaningful.

### 4.3 Attachment-path search: record refs + a `paths` index on the note

Prisma searches `attachments.path` via `attachments: { some: { path:
{ contains } } }`. Surreal v1 can't do a correlated `some` over a record-ref
array with a nested field filter cheaply. Two options:

- **Option A (chosen): denormalize attachment paths onto the note.**
  `notes.<id>` gets `attachmentPaths: [string]` (and `attachments` keeps the
  record-ref array for counts/order). `toAttachment()` already reads
  `note` refs; the attachment mirror (`createAttachment`/`assignAttachmentNote`)
  appends `path` to `attachmentPaths`, and delete mirrors remove it. Then
  path search is `array::any(attachmentPaths, |p| string::lowercase(p)
  CONTAINS string::lowercase($q))` — same record, no join.
- **Option B: subquery per note** (`(SELECT … FROM attachments WHERE note =
  notes:<id>)`) — N+1 and slow; rejected.

`withFile` uses `array::len(attachments) > 0` (record refs), path search uses
`attachmentPaths` (strings) — both maintained by the same mirrors.

### 4.4 Supporting tables: migrate `noteHistory` + `noteInternalShare`, backfill `referenceCreatedAt`

The query engine needs three data shapes M2 didn't produce:

1. **`noteInternalShare`** — fold into the note record as
   `internalShares: [accounts:<uuid>]` (record refs, resolved via the M2
   `_accountRef` map). The owner-OR-share where becomes `$me IN internalShares`
   where `$me` is the **Surreal account ref** for `ctx.id` (resolved once per
   request via `accountRef()`, cached). `isInternalShared`/`canEdit` in the
   output: `canEdit` is stored as `internalShareCanEdit: [accounts:<uuid>]`
   (only shares with `canEdit: true`); the list include returns both arrays
   and the JS normalizer builds `{ accountId, canEdit }` entries like the
   Prisma `internalShares: true` include does.
   - Mirror writes: `note.ts`/`user.ts` internal-share create/delete paths
     call `addInternalShare(noteId, accountId, canEdit)` /
     `removeInternalShare(noteId, accountId)` (new repo functions).
2. **`noteHistory`** — keep it a **table** in Surreal (`noteHistory:<id>`
   with `note: notes:<id>`, `content`, `version`, `metadata`,
   `account: accounts:<uuid>?`, `createdAt`). `_count.histories` becomes a
   `count((SELECT * FROM noteHistory WHERE note = notes:<id>))` subquery in
   the include pass (page-scoped, see §4.6). Migration: add a
   `noteHistory` step to the script.
3. **`referenceCreatedAt`** — store a parallel map on the note record:
   `referencesAt: { "notes:<toId>": <datetime>, … }` (and
   `referencedByAt`). `addNoteReference`/`removeNoteReference` already exist
   in the notes repo — extend them to maintain the map. `noteReferenceList`
   reads the map instead of a join; migration backfills it from
   `noteReference.createdAt`.

### 4.5 Boundaries that stay on Prisma (documented, greppable)

- `attachments.list` folder branch — raw SQL CTE + `DISTINCT ON` is
  Postgres-specific; keep on Prisma with a `// Prisma query read (M3
  boundary)` comment.
- `relatedNotes` AI keyword + vector parts — external store.
- Jobs (`archivejob`, `memosJob`, `rebuildEmbeddingJob`, `dbjob`) batch
  reads — keep on Prisma (M4+).
- `config` lookup (`getGlobalConfig`) — stays on Prisma (config table is a
  non-goal); it only decides `createdAt` vs `updatedAt` ordering, which the
  where-builder consumes as a plain field name.

### 4.6 Include normalization: page-scoped N+1 avoidance

Fetch the page (LIMIT/START), collect the page's numeric ids, then run
**five batched queries** (all `WHERE … IN [page ids]` / record-id lists):

1. `tags`: `SELECT * FROM tag WHERE id IN [tag:<id>, …]` → build
   `{id, noteId, tagId, tag}` per note (M2 `toNote()` already synthesizes
   the join shape — extend it to attach the full `tag` object).
2. `attachments`: `SELECT * FROM attachments WHERE note IN [notes:<id>, …]`
   → order by `sortOrder asc, id asc`, attach.
3. `comments`: `SELECT * FROM comments WHERE note IN […]` + account rows →
   the `comments` include (account `{image,nickname,name}`).
4. `references`/`referencedBy` + `_count.comments`/`_count.histories`:
   resolve `references`/`referencedBy` refs to `{toNoteId, toNote{content,
   createdAt, updatedAt}}` shape (page-scoped `SELECT … WHERE id IN […]`),
   `_count.histories` via the noteHistory subquery for the page's notes,
   `_count.comments` from the batched comments count.
5. `internalShares`/`owner`: account refs → `accounts` rows for
   `internalShares` and `owner` (`{id, name, nickname, image}`).

All five run in parallel (`Promise.all`) per page. This mirrors the Prisma
include graph exactly and keeps it at 1 + 5 queries per page regardless of
page size.

---

## 5. Implementation Steps

### 5.1 Branch

```bash
cd application/tools/blinko/blinko
git checkout surrealdb/migration-auth-first   # contains M1+M2 commits
git checkout -b surrealdb/migration-query-engine
```

### 5.2 Supporting mirrors + migration (do first — engine data)

- `server/lib/repos/notes.ts` — add `addInternalShare(noteId, accountId,
  canEdit)`, `removeInternalShare(noteId, accountId)`; extend
  `addNoteReference`/`removeNoteReference` to maintain
  `referencesAt`/`referencedByAt`.
- `server/lib/repos/attachments.ts` — maintain `attachmentPaths` on the note
  in `createAttachment`/`assignAttachmentNote`/`deleteAttachments`
  (`array::union`/`array::remove`).
- `server/routerTrpc/{note,user}.ts` — internal-share create/delete paths
  call the new repo functions (mirror after Prisma write, same pattern).
- `scripts/migrate/prisma-to-surreal.ts` — add ordered steps:
  `noteHistory` (table, `note` ref), `noteInternalShare` (fold into
  `notes.<id>.internalShares`/`internalShareCanEdit`), and a
  **backfill pass** that sets `referencesAt`/`referencedByAt` from
  `noteReference.createdAt` and `attachmentPaths` from
  `attachments.path`. All idempotent by record id; respect `--tables`/
  `--dry-run`.

### 5.3 Query engine

- `server/lib/repos/notes-query.ts` — `buildNoteListQuery(input, ctx)`
  returning `{ sql, vars }`; `fetchNoteListPage(input, ctx)` that runs the
  query + the §4.6 include pass and returns Prisma-shaped rows; `toListNote()`
  normalizer.
- Extend `_surreal.ts` if needed with a `queryPage(sql, vars)` helper.
- Port the simpler where-builders: `publicList`, `listByIds`, `detail`,
  `publicDetail`, `dailyReviewNoteList`, `randomNoteList` (→
  `ORDER BY rand()`), `noteReferenceList` (reads `referencesAt` map),
  `tag.list`, `comments.list`, `attachments.list` search branch. Each gets a
  small builder + page fetch in its repo file, reusing `notes-query.ts`
  helpers where possible.

### 5.4 Router flip order (each gated by its parity test)

1. `dailyReviewNoteList`, `tag.list` (simplest — flip first).
2. `listByIds`, `detail`.
3. `publicList`, `publicDetail`.
4. `randomNoteList`, `noteReferenceList`.
5. `comments.list`, `attachments.list` search branch.
6. **`notes.list` last** — the reference where-builder; flip only when the
   full input-matrix parity test is green.

Each router swap keeps the pattern: `if (isSurrealEnabled()) { try {
… } catch { log + Prisma fallback } }`.

### 5.5 Docs

- `README.md`/`DEV.md`: list reads now Surreal-first with Prisma fallback;
  note the `attachments.list` folder branch + jobs still on Prisma; new
  migration tables.
- Update M2 plan §9 + this plan's status after merge.

---

## 5.6 Implementation status (2026-08-27, commit `586b5bf3`)

**Done:**

- `server/lib/repos/notes-query.ts` — SurrealQL where-builder + page-scoped
  include normalization. Verified against the live v1.5.6 engine: no
  closures in `WHERE` (use correlated `$parent` subqueries + `attachmentPaths`
  join), `string::join` is broken in v1 (use `array::join`), `LIMIT $size
  START $skip` is the v1 pagination form, bound record ids match via
  `type::thing("tag", $tagId) IN tags`, datetime ranges need bound `Date`
  objects.
- Supporting mirrors: `internalShares`/`internalShareCanEdit` arrays,
  `referencesAt`/`referencedByAt` maps, `attachmentPaths` index (maintained
  by the attachment mirrors), `createNoteHistoryMirror` helper wired into
  `upsert` + the `deleteNotes` cascade.
- Migration script: `noteHistory` + `noteInternalShare` steps, plus backfill
  passes for `referencesAt`/`referencedByAt`/`attachmentPaths`; note pass 2
  now folds internal-share refs (with `canEdit`) into the note record.
- Routers: internal-share write paths (`internalShareNote`,
  `updateNoteInternalShare`) + account-delete cleanup mirror to Surreal.
- `server/__tests__/unit/lib/query-parity.test.ts` — the gate. 19-test input
  matrix (base/type/archived/isShare/isRecycle/searchText incl. attachment
  path/tagId/withFile/withoutTag/withLink/hasTodo/date-range/pagination/
  ordering/sharee-view/combined), deep-equal against the real Prisma
  where-builder.

**Engine quirks replicated for byte-parity (production note.ts):**

- `withLink`/`hasTodo` **overwrite** `where.OR`, dropping account scoping —
  reproduced in the builder via the OR-group replacement.
- Tags join-row `id` (tagsToNote autoincrement) and internalShares join-row
  `id`/`createdAt`/`updatedAt` are synthesized by the mirror and normalized
  out of the parity comparison (documented deviations).

**Parity harness hygiene:**

- Re-mocks `../../../prisma` with the real client inside `beforeAll` to
  defeat bun's cross-file `mock.module` leakage (oven-sh/bun#12823) from
  `surrealdb-repos.test.ts`.
- Wipes only the content tables (both stores), leaving accounts intact so
  the E2E upload suite (which needs account 1) stays green.

**Verification:** 62/62 server tests pass (E2E + integration + unit),
`bun run build:web` (esbuild) clean. A live router smoke test through the
server exercised `notes.upsert` create/update against Surreal with typed
refs — see M2 commit history for the pre-engine wiring.

**Not yet done (this milestone's remaining work):**

- Flipping `notes.list` and the other list endpoints Surreal-first with
  Prisma fallback (§5.4 order) — the parity gate is green, so the flips are
  mechanical; they are batched with the M4 cutover to avoid churning both
  stores while the fallback is still the production path.

---

## 6. Tests & Manual Validation

### Parity harness (the gate) — `server/__tests__/unit/lib/query-parity.test.ts`

Build an **input matrix** covering the where-builder branches, run each
against **both** stores, `expect(deepEqual)`:

- base owner list; internal-shared note visible; recycle=true; archived
  true/false/null; each `type`; `isShare` true/false; `searchText` matching
  content / attachment path / case-insensitive / no match; `tagId`;
  `withFile`; `withoutTag`; `withLink` (http/https); `hasTodo` (- [ ], - [x],
  * [ ]); `startDate`+`endDate` boundaries; `orderBy` asc/desc; `page`/`size`
  (page 2, size 1); combined filters.
- Include-graph parity: `tags`, `attachments` ordering, `comments`+account,
  `references`/`referencedBy` shapes, `_count`, `internalShares`,
  `owner`/`isInternalShared`/`canEdit`.
- Same matrix for `publicList`/`listByIds`/`detail`/`dailyReviewNoteList`/
  `noteReferenceList`/`tag.list`/`comments.list`/`attachments.list`.
- Skipped when `SURREALDB_URL` unset (CI without Surreal stays green) —
  same `describe.skipIf` pattern as the M2 adapter tests.

Seeding for parity: reuse the M2 seed approach (Postgres rows + migration
script to Surreal) so both stores hold identical content before each run.

### Manual smoke (live, Postgres + Surreal v1.5.6)

1. Run migration (now includes noteHistory + internalShares + backfills).
2. Create a note with tags, a link reference, an attachment; internally
   share it with a second account.
3. `notes.list` with every filter from the matrix → identical JSON from both
   stores; watch server log for zero `falling back to Prisma` lines.
4. `noteReferenceList` returns `referenceCreatedAt` correctly.
5. Rollback: unset `SURREALDB_URL`, restart — list reads come from Prisma.

---

## 7. Rollback Plan

1. **Code:** revert the M3 branch — list reads return to Prisma (they are
   the default when Surreal is disabled or the query throws).
2. **Runtime:** unset `SURREALDB_URL` — the parity harness and all list
   endpoints become Prisma passthroughs again.
3. **Data:** Postgres untouched by the script (read-only); Surreal gains
   `noteHistory`/`noteInternalShare`/backfill fields — dropping the Surreal
   ns/db removes them with no app-state loss.

---

## 8. PR Checklist (for the blinko repo PR)

- [ ] Branch `surrealdb/migration-query-engine` from M2 branch/main.
- [ ] `server/lib/repos/notes-query.ts` — parameterized where-builder +
      include pass, gated on `SURREALDB_URL`.
- [ ] Supporting mirrors: `internalShares`/`internalShareCanEdit`,
      `referencesAt`/`referencedByAt`, `attachmentPaths`; router write paths
      updated.
- [ ] Migration script: `noteHistory` + `noteInternalShare` steps +
      `referenceCreatedAt`/`attachmentPaths` backfill, idempotent.
- [ ] List endpoints flipped Surreal-first w/ Prisma fallback per §5.4 order.
- [ ] `attachments.list` folder branch + jobs + AI queries left on Prisma
      with `// Prisma query read (M3 boundary)` markers.
- [ ] Parity harness in `server/__tests__/unit/lib/query-parity.test.ts`
      green; full `bun test` green; README/DEV updated.
- [ ] PR title: `feat(db): serve note list/search from Surreal (query engine, step 3)`,
      with parity-harness results + manual smoke steps in the body.

---

## 9. Follow-up Milestones (M4+)

1. **M4 — final cutover** (plan:
   [`blinko-surrealdb-migration-m4.md`](blinko-surrealdb-migration-m4.md)):
   make Surreal the only datastore — retrofit deterministic `accounts:<id>`
   ids (re-key + `_accountRef` becomes `accounts:${id}`), migrate the
   remaining tables (config, chat, notifications, follows, fonts, AI/MCP,
   jobs, plugin, cache), drop every Prisma fallback/mirror, switch JWT
   `sub` plumbing, then delete `prisma/` + `prisma:*` scripts +
   `@prisma/client`; parity harness becomes golden-fixture assertions.
2. **M5 — engine/SDK upgrade (optional):** bump `surrealdb.js` + engine to
   v2/v3 for `FULLTEXT ANALYZER` indexes (replace `string::lowercase
   CONTAINS` with indexed FTS) and multi-doc transactions; add Surreal to
   the deployed `application/tools/blinko` compose + backup/restore.
