# Blinko — Prisma → SurrealDB Migration, Milestone 2 (Content Graph)

> **Tags:** #blinko #migration #surrealdb #prisma #m2
> **Last updated:** 2026-09-17 | **Status:** **RETIRED** (was: Complete — repos
> + migration script + tests + router wiring done, live-verified). The vendored
> `mammhoud/blinko` checkout this milestone patched was replaced by the
> SurrealDB-native runtime at `application/tools/planing/runtime/`; there is no
> Prisma content graph left to mirror. Current roadmap:
> [`blinko-surrealdb-enhancements.md`](blinko-surrealdb-enhancements.md).
> **Scope:** Extend the M1 Surreal migration to the content graph — `notes`,
> `attachments`, `tag`, `tagsToNote`, `noteReference`, `comments` — converting
> integer FK ids to Surreal record references. Auth/accounts (M1) stays as-is.
> **Depends on:** [`blinko-surrealdb-migration.md`](blinko-surrealdb-migration.md) (M1, branch
> `surrealdb/migration-auth-first` in the vendored checkout
> `application/tools/blinko/blinko/`).

---

## 1. Purpose

Move the **content graph** of the Blinko server onto SurrealDB: notes,
attachments, tags, the tags↔notes join, note↔note references, and comments.
This is where the product's real data lives, so unlike M1 (which mirrored
writes and read point-records), M2 must also decide what happens to the
**query/list paths** — the plan below keeps them on Prisma for now (see
§4.4) while every write and point-read goes through Surreal-backed adapters.

FK ids (Postgres integers) become **Surreal record references** (`notes:123`,
`tag:7`, `accounts:<uuid>`), which is the modeling Surreal is designed for
and the point of this milestone.

---

## 2. Current State (verified in checkout, 2026-08-27)

### 2.1 Schema (prisma/schema.prisma) — FK graph

| Model | PK | FKs / relations | Notes |
|---|---|---|---|
| `notes` | `id Int @id` | `accountId → accounts`; `attachments[]`; `tags[]` (via `tagsToNote`); `references`/`referencedBy` (via `noteReference`); `comments[]`; `histories[]` | Scalar flags: `type`, `content`, `isArchived/isRecycle/isShare/isTop/isReviewed`, share fields, `metadata Json?`, `sortOrder`, timestamps |
| `attachments` | `id Int @id` | `noteId → notes?`; `accountId → accounts?` | `path`, `size Decimal`, `type`, `sortOrder`, `perfixPath`, `depth`, `metadata Json?` |
| `tag` | `id Int @id` | `parent Int` (self-ref, default 0); `accountId → accounts?` | `name`, `icon`, `sortOrder` |
| `tagsToNote` | `@@id([noteId, tagId])` | `noteId → notes`; `tagId → tag` | Pure join; no extra columns |
| `noteReference` | `id Int @id` | `fromNoteId`/`toNoteId → notes`; `@@unique([fromNoteId, toNoteId])` | `createdAt` |
| `comments` | `id Int @id` | `noteId → notes` (required); `accountId → accounts?`; `parentId → comments?` | `guestName/guestIP/guestUA` for public guests |

### 2.2 Call-site inventory (grep-verified)

| File | Surface |
|---|---|
| `server/routerTrpc/note.ts` (1879 lines) | `list`, `publicList`, `listByIds`, `publicDetail`, `detail`, `dailyReviewNoteList`, `randomNoteList`, `relatedNotes`, `reviewNote`, `upsert`, `shareNote`, `updateMany`, `trashMany`, `deleteMany`, `addReference`, `noteReferenceList`, `clearRecycleBin`, `updateAttachmentsOrder`, `getNoteHistory`, `getNoteVersion`, `internalShareNote`, `getInternalSharedUsers`, `internalSharedWithMe`, `updateNotesOrder`; module-level `deleteNotes()` (cascade) and `insertNoteReference()` |
| `server/routerTrpc/tag.ts` | `list`, `fullTagNameById`, `updateTagMany`, `updateTagName`, `updateTagIcon`, `deleteOnlyTag`, `deleteTagWithAllNote`, `updateTagOrder` |
| `server/routerTrpc/attachment.ts` | `createFolder`, `list`, `rename`, `move`, `delete` (ties into `FileService` storage deletes) |
| `server/routerTrpc/comment.ts` | `create`, `list`, `delete`, `update` |
| `server/lib/helper.ts` | tag-tree builder (`buildHashTagTreeFromHashString`), hashtag extraction |
| `server/lib/files.ts` | `FileService` — upload/delete storage + DB rows (attachment lifecycle) |
| `server/routerExpress/file/{file,s3file,delete}.ts` | upload/delete/s3 paths touching `attachments` |
| `server/jobs/{archivejob,dbjob,memosJob,rebuildEmbeddingJob}.ts` | batch note reads, cleanup, embedding rebuilds |
| `server/aiServer/*` | read-only note/attachment enrichment (keep on Prisma) |
| `server/routerTrpc/{ai,analytics,user}.ts` | read-only queries + `user` cleanup paths |

Per-model call counts (grep of `prisma.<model>.<op>`): `notes` 54,
`attachments` 26, `tag` 20, `tagsToNote` 12, `comments` 18, `noteReference` 8.

### 2.3 Why this milestone is bigger than M1

- **List/query complexity:** `notes.list` builds a `Prisma.notesWhereInput`
  (owner OR internal-shares, `isRecycle`, `type`, date ranges, `searchText`
  contains, `withoutTag`/`withFile`/`withLink`/`hasTodo` conditions) with deep
  `include` (`attachments`, `tags→tag`, `references→toNote`, `referencedBy→
  fromNote`, `_count comments/histories`, `owner`) and pagination. Porting this
  where-builder to SurrealQL 1:1 is its own milestone — see §4.4.
- **Write cascades:** `deleteNotes()` deletes tagsToNote rows, noteReference
  rows, garbage-collects orphan tags (`_.difference`), deletes attachment
  storage files, comments, notes, noteHistory, and fires per-note webhooks +
  AI vector deletes. The Surreal mirror of this must be a transaction-style
  sequence (Surreal has no multi-doc transactions via the JS client yet;
  see §4.3).
- **Shape normalization:** API responses expect Prisma shapes
  (`tags: [{id, noteId, tagId, tag}]`, `references: [{toNoteId, toNote}]`,
  numeric ids everywhere). Surreal records with record-ref arrays must be
  normalized back — this is the bulk of the adapter work.

---

## 3. Goals & Non-Goals (Milestone 2)

**Goals**

1. Surreal adapters for `notes`, `attachments`, `tag`, `comments`
   (`server/lib/repos/{notes,attachments,tags,comments}.ts`) covering the
   write paths + point reads used by the routers in §2.2.
2. Record-ref modeling: `note.tags: [tag:<id>]`, `note.references: [notes:<id>]`,
   `attachments.note: notes:<id>`, `comments.note: notes:<id>`,
   `comments.parent: comments:<id>`, `*.account: accounts:<id>`.
3. Route the M2 routers' writes + point reads through the adapters
   (Prisma-first + Surreal mirror for writes, Surreal-first + Prisma fallback
   for point reads — same dual pattern as M1).
4. Extend `scripts/migrate/prisma-to-surreal.ts` to migrate the M2 tables
   (ordered, FK→ref conversion, idempotent by record id).
5. Keep list-style query reads, AI/enrichment, analytics, and jobs on Prisma
   (§4.4) — documented, so M3 knows what remains.

**Non-goals (later milestones)**

- Porting the note list/search where-builder to SurrealQL (M3 "query
  engine").
- `noteHistory`, `noteInternalShare`, `follows`, `notifications`, `cache`,
  `plugin`, `conversation`/`message`/AI tables, `config`, `fonts`,
  `aiProviders`/`aiModels`/`aiScheduledTask`/`mcpServers`.
- Removing Prisma or changing the deployed `application/tools/blinko` compose
  stack.

---

## 4. Architecture Decisions

### 4.1 ID strategy: deterministic Surreal record ids

Surreal accepts explicit record ids. **Use `notes:<legacyId>`, `tag:<legacyId>`,
`attachments:<legacyId>`, `comments:<legacyId>`.** Benefits:

- FK resolution is free: `attachments.note = notes:123` with zero id-maps.
- Point reads become `db.select('notes:123')` — no `WHERE legacyPrismaId`.
- Migration idempotency = "does `notes:123` exist?" — one `db.select`.

**Accounts (M1) exception:** M1 created `accounts` with random ids + a
`legacyPrismaId` field. References to accounts (`note.account`,
`attachment.account`, `tag.account`, `comment.account`) must resolve through
a `legacyPrismaId → recordId` map:
- The migration script builds it once at start (query
  `SELECT legacyPrismaId, id FROM accounts`).
- The adapters resolve account refs at write time via
  `SELECT id FROM accounts WHERE legacyPrismaId = $id LIMIT 1` (cheap, or a
  cached map). M4 can retrofit deterministic account ids.

**Normalizer:** every adapter exports a `toX()` that converts a Surreal row
back to the Prisma shape callers expect (numeric `id` extracted from the
record id / `legacyPrismaId`, refs expanded to numeric fks, dates → `Date`).
`toNote()` synthesizes the API's `tags`/`references`/`referencedBy` array
shapes from the record-ref arrays (§4.2).

### 4.2 Record modeling (join tables fold into the note)

- **`tagsToNote`** → `note.tags: [tag:<id>, ...]`. API shape
  `{id, noteId, tagId, tag: {...}}` is synthesized by `toNote()`:
  `tagId = Number(recordId)`, `id = tagId`, `noteId = Number(noteId)`.
  Keep `tag.accountId` on the tag record; the tag's own `parent` stays a
  plain number for now (self-ref conversion is M3 polish; `parent: 0` works
  as-is).
- **`noteReference`** → `note.references: [notes:<id>, ...]` (outgoing) and
  `note.referencedBy: [notes:<id>, ...]` (incoming). `toNote()` synthesizes
  `{toNoteId, toNote: {...}}` / `{fromNoteId, fromNote: {...}}`; `createdAt`
  of a reference is dropped (or stored as a parallel `referencesAt` map if
  the UI needs it — check `noteReferenceList` consumers before deciding).
- **`attachments`** stays a table with `note: notes:<id>?` and
  `account: accounts:<id>?`.
- **`comments`** stays a table with `note: notes:<id>`, `account: accounts:<id>?`,
  `parent: comments:<id>?`.

### 4.3 Write semantics: Prisma-first + Surreal mirror (as M1)

Keep M1's proven dual pattern to stay rollback-safe:

- **Writes** (`create`, `update`, `delete`, joins): execute Prisma first
  (source of truth, numeric ids), then mirror to Surreal best-effort with a
  `console.error` on failure (never throw — the app keeps working on Prisma).
- **Point reads** (`findNoteById`, `findAttachmentById`, `findTagBy...`):
  Surreal-first with Prisma fallback when Surreal misses or errors.
- **Cascades** (`deleteNotes`, tag GC): keep the Prisma cascade authoritative;
  mirror each step to Surreal (`DELETE notes WHERE id IN ...`,
  `UPDATE notes SET tags = tags - [...]`...). Surreal record ids make the
  mirrored deletes trivially addressable. Do **not** attempt cross-record
  atomicity — accept eventual consistency between Prisma and Surreal until
  the Prisma cutover in M4.

### 4.4 List/query reads stay on Prisma (documented boundary)

`notes.list`, `publicList`, `listByIds`, `publicDetail`, `dailyReviewNoteList`,
`randomNoteList`, `relatedNotes`, `noteReferenceList`, `comments.list`,
`attachments.list`, `tag.list`, `analytics`, AI enrichment, and the jobs'
batch reads **remain on Prisma**. Rationale: the where-builder + deep includes
are not portable piecemeal; porting them without the query engine work (M3)
would either silently change results or require duplicating the filter logic
in SurrealQL. This is a documented, tested boundary: when `SURREALDB_URL` is
set, writes land in both stores, point reads prefer Surreal, and list reads
come from Postgres (consistent because Prisma is still authoritative).

---

## 5. Implementation Steps

### 5.1 Branch

From `surrealdb/migration-auth-first` (M1) in the vendored checkout:

```bash
cd application/tools/blinko/blinko
git checkout surrealdb/migration-auth-first   # or main once M1 merges
git checkout -b surrealdb/migration-content-graph
```

### 5.2 Adapters — `server/lib/repos/`

Add (mirroring the M1 `accounts.ts` structure: `isSurrealEnabled()` gate,
`queryOne`/`queryMany`/`queryRaw` helpers, `toX()` normalizers, Prisma-first
writes, Surreal-first point reads):

**`notes.ts`**
- `createNote(data)` / `updateNote(id, patch)` / `deleteNote(id)`
- `findNoteById(id)` (Surreal `select('notes:'+id)` → `toNote()`)
- `setNoteTags(noteId, tagIds: number[])` (mirror `note.tags = [tag:<id>…]`)
- `setNoteReferences(noteId, toNoteIds, direction)` (mirror
  `references`/`referencedBy` arrays; resolve account refs via §4.1 map)
- `addNoteReference(fromId, toId)` / `deleteNoteReferences(noteId)`
- `batchUpdateNotes(ids, patch)` (for `trashMany`/`updateMany`)

**`attachments.ts`**
- `createAttachment(data)` / `updateAttachment(id, patch)` /
  `deleteAttachments(ids)` / `deleteAttachmentsByNoteIds(noteIds)`
- `findAttachmentById(id)`; `findAttachmentsByNoteId(noteId)` (used by
  `detail`/`deleteNotes`)
- `updateAttachmentsOrder(noteId, orderedIds)` (mirror `sortOrder`)

**`tags.ts`**
- `createTag(data)` / `updateTag(id, patch)` / `deleteTags(ids)`
- `findTagById(id)` / `findTagByNameParentAccount(name, parent, accountId)`
- `incrementTagRefCount`/GC is handled by the note adapter mirror; keep the
  Prisma GC authoritative in `deleteNotes`.

**`comments.ts`**
- `createComment(data)` / `updateComment(id, patch)` /
  `deleteComments(ids)` / `deleteCommentsByNoteIds(noteIds)`
- `findCommentById(id)`

Account-ref resolution shared helper: `server/lib/repos/_accountRef.ts`
(`accountRef(legacyId): Promise<string>` → `accounts:<uuid>` with a tiny
in-process cache + `SELECT id FROM accounts WHERE legacyPrismaId = $id`).

### 5.3 Router swaps (writes + point reads only)

- **`note.ts`** — `upsert` (permission `findFirst` → `findNoteById` +
  ownership check; tag tree `findFirst/create` → tag adapter; tagsToNote
  `findFirst/create/deleteMany` → `setNoteTags`; note create/update →
  note adapter; reference inserts → `addNoteReference`), `trashMany` →
  `batchUpdateNotes`, `deleteMany`/`deleteNotes()` cascade →
  adapter mirrors, `addReference`, `detail`/`publicDetail` point reads →
  `findNoteById` (keep the deep-`include` list reads on Prisma),
  `updateAttachmentsOrder` → attachment adapter.
- **`tag.ts`** — `fullTagNameById`, `updateTagName/Icon/Order`, `deleteOnlyTag`,
  `deleteTagWithAllNote` write paths → tags/notes adapters; `list` stays
  Prisma.
- **`attachment.ts`** — `createFolder`, `rename`, `move`, `delete` →
  attachments adapter (file storage deletes stay in `FileService`); `list`
  stays Prisma.
- **`comment.ts`** — `create`, `delete`, `update` → comments adapter;
  `list` stays Prisma.
- **`lib/files.ts` / `routerExpress/file/*`** — attachment row creates/deletes
  → attachments adapter (upload path).
- **`jobs/{archivejob,memosJob,rebuildEmbeddingJob}.ts`** — any *writes*
  (cleanup deletes) → adapters; batch reads stay Prisma.

Rule of thumb per file: swap a call only if it is a point read or a write;
leave `findMany` where-builder queries on Prisma and add a `// Prisma query
read (M3 query engine)` comment so the boundary is greppable.

### 5.4 Migration script — `scripts/migrate/prisma-to-surreal.ts`

Extend the M1 script (keep `accounts` step, add the rest). Table order
respects FK refs; refs are resolved to record ids:

1. `accounts` (existing M1 step).
2. Build the account map: `SELECT legacyPrismaId, id FROM accounts`.
3. `tag` — `findMany` with pagination; create `tag:<legacyId>` with
   `account: accountRef(accountId)`; skip if `select('tag:'+id)` exists.
4. `notes` — pass 1: `findMany({ include: { tags: { select: { tagId } },
   references: { select: { toNoteId } }, referencedBy: { select: {
   fromNoteId } } } })`; create `notes:<legacyId>` with scalars +
   `account: accountRef(accountId)`; **defer** the tag/ref arrays.
5. `notes` — pass 2 (after all notes exist): for each note, resolve
   `tagIds → tag:<id>` and `toNoteIds → notes:<id>` (skip refs to notes
   still missing, log them), then `db.merge('notes:<id>', { tags: [...],
   references: [...], referencedBy: [...] })`.
6. `attachments` — `findMany`; create `attachments:<legacyId>` with
   `note: notes:<noteId>` / `account: accountRef(accountId)` (null-safe).
7. `comments` — `findMany({ orderBy: createdAt })`; create
   `comments:<legacyId>` with `note: notes:<noteId>`,
   `parent: comments:<parentId>` (null-safe), `account: accountRef`.

Idempotency: per-record `select` skip, so partial failures are re-runnable.
Reports per-table created/skipped/failed; exit non-zero on failures.
New flags: `--tables accounts,notes,attachments,tags,comments` (default all)
and `--dry-run` (counts only, no writes). `prisma.$disconnect()` at the end.

### 5.5 Docs & config

- `README.md` / `DEV.md`: update the SurrealDB section — content graph now
  migrates too; note the Prisma-query-read boundary (§4.4) and new script
  flags.
- `.env.tmpl` / `turbo.json`: no changes (same `SURREALDB_*` vars).
- Update the M1 plan's §10 link and this plan's status after merge.

---

## 6. Tests & Manual Validation

Automated (extend the M1 suite; same "skipped when `SURREALDB_URL` unset"
pattern):

- Adapter unit tests against a local Surreal:
  `notes` create/update/delete + `setNoteTags`/`setNoteReferences` round-trip;
  `attachments` create/delete + note ref; `tags` find-or-create; `comments`
  create + parent ref. Verify `toNote()` normalization returns the exact
  Prisma shapes the routers consume.
- Migration script test: seed a throwaway Postgres (or reuse test DB) with
  notes/tags/attachments/comments incl. cross-references; run the script
  twice; assert second run = all skipped; assert refs resolve to real
  Surreal record ids.
- Existing `server/__tests__` must stay green (`bun run test`).

Manual smoke:

1. Start Surreal + Postgres; run the migration script.
2. `POST /api/trpc/note.upsert` with hashtags → note lands in Surreal with
   `tags: [tag:<id>]`; add a `#` reference to another note →
   `references: [notes:<id>]`.
3. `POST /api/trpc/note.list` still returns identical results (reads Prisma).
4. `POST /api/trpc/note.batch-delete` → note, its attachments (files +
   rows), join rows, and comments disappear from **both** stores.
5. `SELECT * FROM notes, tag, attachments, comments` in Surreal shows
   record-ref fields, not int fks.
6. Rollback: unset `SURREALDB_URL`, restart — everything works on Prisma;
   Postgres untouched by the script.

**Verified 2026-08-27 (live Postgres 14 + SurrealDB v1.5.6):** full
migration of the seeded content graph (seed Welcome data + synthetic
tags/notes/attachments/comments) succeeds: accounts `skipped=1` (M1
random-id record found via `legacyPrismaId` — no duplicate), tags `7`,
notes `8`, attachments `7`, comments `1` created. Re-run is fully
idempotent (all skipped). Typed refs confirmed: `notes:2001.tags =
[tag:1001, tag:1002]`, `notes:2002.references = [notes:2001]`,
`attachments:4001.note = notes:2001`, `comments:5001.note = notes:2001`,
`tag:1001.account`/`notes:2001.account` resolve to the M1 accounts record.
Adapter test suite (`server/__tests__/unit/lib/surrealdb-repos.test.ts`,
bun:test, mocked Prisma, skipped without `SURREALDB_URL`) passes 9/9.
Committed on `surrealdb/migration-auth-first` as `b919d921`.

**Router wiring (DONE 2026-08-27, commit `b8c3de01`):** §5.3 is implemented
and live-verified:

- `note.ts` — `upsert` create/update mirror (tag tree via tag adapter,
  tagsToNote create/delete → `addNoteTag`/`removeNoteTag`, reference
  inserts/deletes → `addNoteReference`/`removeNoteReference`, note
  create/update via note adapter), `trashMany` → `batchUpdateNotes(ids,
  {isRecycle:true}, accountId)` (Surreal mirror scoped to the account),
  `deleteNotes()` cascade mirrors each step (noteReference cleanup →
  `deleteNoteReferences`, tag GC → `deleteTags`, attachment row deletes →
  `deleteAttachments`, comments → `deleteCommentsByNoteIds`, notes →
  `deleteNotes`), `insertNoteReference` mirrors.
- `tag.ts` — `fullTagNameById`/`deleteOnlyTag` chain reads via
  `findTagById` (Surreal-first), `updateTagName`/`updateTagOrder` via
  `updateTag`, `deleteOnlyTag` write path via `updateTag` + `removeNoteTag`
  + `deleteTags` GC.
- `attachment.ts` — `createFolder` via `createAttachment`; `rename`/`move`
  keep `tx.*` writes inside the Prisma transaction and defer Surreal
  mirrors until after commit (`mirrorAttachmentUpdate`); `delete`/`deleteMany`
  use `deleteAttachmentsSurrealOnly` (FileService owns the Prisma row delete,
  tests forbid a second `prisma.deleteMany`).
- `comment.ts` — `create`/`delete`/`update` via comment adapter; webhook
  payloads reloaded via `findUnique` after the adapter write.
- `_accountRef` fix: `SELECT VALUE id` returns a raw RecordId, so typed
  account refs were silently skipped on new writes — now stringified.

**Verified 2026-08-27 (live):** full unit suite 70/70 pass (incl. the
previously-isolated `sanitizeUploadFileName` + `attachment.deleteMany`
suites), `build:web` clean, and live router smoke tests — `notes.upsert`
create (typed tag refs) and update (`id: 10`, mirror MERGE with typed
`account` ref preserved), `comments.create` (typed `note`/`account` refs),
`tags.fullTagNameById` (Surreal-first read). Zero `[surrealdb] … fallback`
/ mirror errors in the server log during smoke tests. Committed as
`b8c3de01` on `surrealdb/migration-auth-first`.

**Remaining M2 runtime step (not yet implemented):** `lib/files.ts` upload
path + `routerExpress/file/*` attachment row writes, and job cleanup deletes
(§5.3 last bullets) — these still run Prisma-only; the note/tag/attachment/
comment routers are fully wired. List/query reads stay on Prisma (M3 query
engine).

---

## 7. Rollback Plan

1. **Code:** `git checkout main` (or revert the M2 branch) in the blinko
   checkout. Prisma code untouched for list reads; writes still ran Prisma-
   first, so nothing is lost.
2. **Runtime:** unset `SURREALDB_URL` — bootstrap skips Surreal, adapters
   become plain Prisma passthroughs (§4.3 fallback).
3. **Data:** Postgres is never written by the script. Re-running the script
   is idempotent. To clean up Surreal, drop the namespace/db — no app state
   depends on it yet.

---

## 8. PR Checklist (for the blinko repo PR)

- [ ] Branch `surrealdb/migration-content-graph` from M1 branch/main.
- [ ] `server/lib/repos/{notes,attachments,tags,comments}.ts` + `_accountRef.ts`
      added, gated on `SURREALDB_URL`, with `toX()` normalizers.
- [ ] Record-ref modeling: `note.tags`/`references`, `attachment.note`,
      `comment.note`/`parent` as Surreal record refs.
- [ ] Router swaps limited to writes + point reads; list/query reads left on
      Prisma with `// Prisma query read (M3)` markers.
- [ ] `deleteNotes` cascade mirrored to Surreal (tags GC + attachments +
      comments + references).
- [ ] Migration script extended: ordered tables, FK→ref conversion,
      idempotent by record id, `--tables` + `--dry-run` flags.
- [ ] README/DEV updated; `bun run test` passes; manual smoke steps in PR body.
- [ ] PR title: `feat(db): migrate notes/attachments/tags/comments to Surreal with record refs (step 2)`,
      with run instructions + rollback notes.

---

## 9. Follow-up Milestones (M3+)

1. **M3 — query engine** (plan: [`blinko-surrealdb-migration-m3.md`](blinko-surrealdb-migration-m3.md)):
   port `notes.list`/`publicList`/`listByIds`/`detail`/`publicDetail`/
   `dailyReviewNoteList`/`randomNoteList`/`noteReferenceList` +
   `attachments.list`/`tag.list`/`comments.list` where-builders to
   SurrealQL (parameterized, paginated, deep-include normalization) with a
   Prisma↔Surreal parity harness; migrate `noteHistory`/`noteInternalShare`
   and backfill `referenceCreatedAt`/`attachmentPaths`. Switch point reads
   to Surreal-only (drop Prisma fallback) in M4, once the harness is green.
2. **M4 — final Prisma removal:** delete `prisma/`, drop the client +
   `prisma:*` scripts; retrofit deterministic `accounts:<id>` ids; switch
   JWT `sub` semantics; remove `legacyPrismaId`.
3. **M5 — runtime:** Surreal service in `application/tools/blinko` compose +
   backup/restore before enabling in the deployed stack.
```
