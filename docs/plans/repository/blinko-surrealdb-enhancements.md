# Blinko SurrealDB workspace enhancement plan

> **Date:** 2026-09-13  
> **Last updated:** 2026-09-17  
> **Status:** Accepted for staged follow-up — Phase 1, Phase 2 (including the
> retention/soft-deletion closeout), Phase 5, and the first Phase 4 slices
> (transactions, query telemetry) are implemented and verified  
> **Scope:** `application/tools/planing/runtime/` and its SurrealDB deployment
> (the tool directory was renamed from `application/tools/blinko/`; the runtime
> code, schema, and deployment are the same, only the path and the
> `PLANING_*` env prefix changed)

<!-- AI-generated: review needed -->

## Context

Blinko now runs as a focused SurrealDB-only notes workspace. The deployed
runtime combines the original Blinko visual direction—quiet light surfaces,
strong black actions, purple secondary accents, responsive category navigation,
and compact note cards—with a smaller, auditable application boundary.

The current model has one `notes` table related to `account` and `category`.
Three system categories are available to every workspace: `Blinko`, `Notes`,
and `Agent`. Users can create additional categories without changing the
schema or rebuilding the application.

## Implemented in `workspace-v4`

The `workspace-v4` slice ported the core notes experience of the original
Blinko onto the SurrealDB runtime and moved every database interaction onto
the official `surrealdb` JS SDK (`surrealdb@1.x`, pinned for the v1.5.6
engine; CBOR record links must be `RecordId` instances):

- Note lifecycle parity with the upstream model: pin (`is_top`), archive,
  recycle/restore, share flag, metadata, tags, and attachments metadata —
  stored on a `SCHEMAFULL` `notes` table with `option<...>` fields and
  defaults so older v2/v3 records decode cleanly.
- GitHub-style markdown rendering for note content in the client, matching
  the original Blinko reading experience.
- Tags with counts, tag filtering, category reassignment, and filtered note
  reads (`all`, per-category, archive, recycle).
- Attachments: upload endpoint, per-note listing with image previews and
  display options, and pending-attachment chips in the composer.
- Full Settings surface with tabs (General, Appearance, People, AI, Data),
  including theming (light/dark/system), accent colors, and text scale,
  persisted in SurrealDB and applied to every session.
- Single-item sidenav (Notes) with People moved into Settings, per the
  original Blinko navigation structure.
- Startup reconciliation: idempotent schema defines tolerate legacy rows,
  defaults are backfilled non-destructively, and duplicate legacy category
  slugs (a v2-era artifact) are deduped with note reassignment before the
  unique slug index is rebuilt.
- Note editing from the card UI (inline editor with tag editing, cancel and
  save) backed by the `PATCH /api/notes/:id` content/tags path.
- Full-text search backed by a SurrealDB `SEARCH ANALYZER` index on note
  content (`blank` tokenizer, `lowercase` + `ngram(1,32)` filters, BM25),
  verified on the pinned v1.5.6 engine: pre-existing rows are indexed at
  `DEFINE INDEX` time, edits re-index, and matching is case-insensitive
  substring + multi-word. The analyzer and index definitions are idempotent
  across restarts.
- Category management: `PATCH /api/categories/:slug` for color (`#rrggbb`
  validated), icon, and rename (non-system lanes only; system lanes may change
  color/icon), plus `DELETE /api/categories/:slug` which reassigns the lane's
  notes to the workspace default (or a system lane if the default is being
  deleted) before removal — no note is ever left pointing at a missing lane.
  The sidebar exposes a per-lane edit panel (name, color swatches, icon) and a
  confirmed delete, permission-gated by `categories:write`, fully localized.
- Playwright coverage now includes markdown rendering, pin/archive/recycle
  flows, note editing (save and cancel), live search with empty-state, tags,
  settings tabs, theming, and the restructured navigation.

## Study notes, sharing, and AI chat (`workspace-v4`, latest slice)

The study-notes slice turned the note stream into a personal knowledge base and
closed the sharing gap that made public links unreachable:

- **Public share links actually work.** The note-card Share button was sending
  an empty payload to `PATCH /api/notes/:id/share`, so every toggle wrote
  `is_share = false` while the UI optimistically showed the note as shared and
  copied a link that then 404'd. The flag now travels in the mutation body, the
  button action flips between `share`/`unshare`, and a shared note shows a
  badge plus **Preview** and **Copy link** actions. `/share/:id` renders a
  read-only GFM page, `/share/:id/raw` serves the same note as
  `text/markdown` (downloadable as `.md`), and a friendly "This note is not
  shared" page explains an unshared or unknown id instead of a bare 404.
- **Wiki-link graph.** `[[Another note title]]` renders as a chip in the shared
  markdown renderer (client and share page use one module). The **Links** action
  on a note card opens an inline panel with outgoing links (resolved against
  note titles) and incoming **backlinks**, so study notes can be traversed
  without leaving the stream. Unwritten targets are marked as such instead of
  linking nowhere.
- **Markdown file import.** Settings → Data imports one or many `.md` / `.mdx`
  files (picker or drag-and-drop) through `POST /api/notes/import-markdown`.
  The first heading becomes the note title, missing headings fall back to the
  file name, and content that already exists verbatim is skipped — re-importing
  a folder never duplicates notes.
- **Study prompt templates.** Seeded prompt styles now include study flows
  (study-notes-from-source, flashcards, quiz-me, revision summary, explain-like-
  a-tutor) alongside the general ones, selectable per chat session.
- **Session durability.** The HTTP transport signs in once at boot; if the
  engine restarts or rotates its signing key the stored token goes stale and
  every query fails until the process is restarted. `q()` now detects an auth
  error, re-signs in once (shared across concurrent failures) and retries, so a
  long-running deployment heals instead of reporting a degraded workspace.

## Workspace bundles and the study-tenancy repair (`workspace-v10`)

A workspace can now leave one deployment and arrive in another intact, and the
path that made that visible also exposed a real tenancy bug in study.

- **`GET /api/workspaces/:id/bundle`** exports the workspace as a portable
  envelope: its settings (name, description, default lane, agent context,
  appearance, context roots), lanes with colour and icon, tags, notes with their
  ids, study cards, comment threads, custom prompts, and attachment metadata.
  Deployment state stays out on purpose — providers hold credentials, a chat
  belongs to a provider, and audit rows are history rather than content.
- **`POST /api/workspaces/import`** always restores into a **new** workspace, so
  a move never merges into or overwrites what the target already holds. Record
  ids are preserved when they are free — which is what keeps `[[wiki links]]`,
  share links, and study cards pointing at the same records after a move — and
  remapped when they are taken, with the remap applied to every dependent card
  and comment so the copy stays internally consistent. Wiki-link edges are
  rebuilt after the import, so links resolve *inside* the imported workspace
  rather than at the source deployment. The name is de-duplicated (`Lab (2)`)
  and importing switches the session to the copy.
- **Attachment files are not part of the bundle.** Only their metadata travels,
  because the bytes live in the source deployment's data volume; restoring rows
  that point at files which are not there would render broken chips. Copy the
  volume if the files matter.
- **Study cards and reviews were filed under the wrong workspace.**
  `createStudyItems` relied on the `workspace` field default, so a card
  generated in any workspace other than `workspace:default` landed in
  `workspace:default` — invisible to the workspace that created it, and its
  reviews never reached that workspace's analytics. The creator now writes the
  workspace it was called from, the review endpoint scopes the card it grades and
  logs the review to the same workspace, `studyStats` is asked for the request's
  workspace, and a boot migration re-files existing rows from their note or
  item.

## Note comment threads (`workspace-v9`)

Discussion now lives next to the note it is about, and it inherits the tenancy
of that note.

- **`note_comment` rows repeat the note's workspace.** A comment stores its
  `note`, its `workspace`, and its `author`, and every read and write resolves
the *note* through the active workspace first (`noteInWorkspace`). From another
workspace the note is `404`, and a comment id from there resolves to nothing —
the same answer for a wrong workspace and a wrong id.
- **Roles decide who may reply.** `comments:write` (owner, admin, editor,
  commenter) gates posting, editing, and deleting; `viewer` reads the thread.
  Authors edit and delete their own replies, and a member who can manage people
  moderates the thread. Deletion is a soft flag, so the thread keeps its shape
  and the audit trail keeps its record (`comment.create`, `comment.edit`,
  `comment.delete` with `moderated`).
- **On the note card.** A `Comments` action opens the thread inline — the same
  pane idiom as the link graph — with the reply count, author, timestamps, an
  `edited` marker, inline editing, and a reply box that appears only for roles
  that may comment. Bodies render as markdown through the shared renderer, so a
  comment cannot inject HTML.

## Per-workspace invitations and owner/commenter roles (`workspace-v8`)

This slice closes the membership half of Phase 2. Invitations and roles now
belong to one workspace each, so a code issued here can no longer be listed,
revoked, or redeemed from somewhere else.

- **Roles `owner` and `commenter`.** `owner` holds the workspace — it is the
  only role that can hand out ownership or archive the workspace — while
  `commenter` reads and replies. `admin`/`editor`/`viewer` stay valid so
  existing memberships keep working, and the permission set gained
  `comments:write` and `workspace:manage` ahead of comment threads. Roles are
  compared by rank (`viewer 1 … owner 5`), so **a member can only grant a role
  at or below their own** — an admin gets `403` for `{"role":"owner"}` — and
  `superadmin` is never grantable through the People tab.
- **The role lives on the membership edge.** `PATCH /api/members/:id` writes
  `workspace_member.role` instead of the global `account.role`, so promoting
  someone in one workspace leaves their role everywhere else untouched.
  `GET /api/auth/profile`, `/api/auth/login`, and `/api/settings` report the
  *effective* role for the active workspace, which is what the sidebar chip and
  the permission gates follow.
- **A workspace always keeps one owner.** The last owner cannot be demoted or
  removed (`400 A workspace must keep at least one owner`), members cannot
  change their own role or remove themselves, and creating a workspace makes the
  creator its owner rather than an admin.
- **Per-workspace invitations.** `GET`/`POST`/`DELETE /api/invitations` are all
  filtered on the active workspace: another workspace's code is neither listed
  nor revocable (404). Codes carry `expires_at` (14 days, backfilled for pre-v8
  rows by the boot migration) and are refused once expired, revoked, or claimed
  — all with the same message, so a probe cannot tell them apart.
- **Joining an existing account.** `POST /api/invitations/redeem` lets an
  account that already exists join with a code from Settings → People → *Join a
  workspace*: it adds the membership edge and switches the joiner to that
  workspace. Registration still redeems a code into the issuing workspace, and
  `account.active_workspace` is set at creation so a new member lands where they
  were invited.
- **People tab.** Members show their workspace role, an `OWNER` badge, and
  controls only where the signed-in member outranks the row; the invitation
  list shows the role, who issued the code, and when it expires. Viewers and
  commenters see who is in the workspace and the join form, but no management
  controls. All new copy ships in EN/AR.

## Multiple workspaces, richer context, and recall analytics (`workspace-v6`/`workspace-v7`)

This slice finished the Phase 2 tenancy work and deepened the two surfaces that
make the workspace useful day to day — what a chat can read, and how recall is
tracked.

- **Multiple workspaces with a switcher.** An account holds many memberships
  (`workspace_member` edges), and `account.active_workspace` records which one a
  session is looking at. `auth` resolves that scope once per request
  (`resolveWorkspaceScope`), and every content query is bounded by it: notes,
  lanes, study cards, reviews, chats, prompts, integrations, audit events, and
  the graph. The sidebar switcher re-reads each view on change, and Settings →
  General lists workspaces with create, rename, switch, and archive.
- **Per-workspace lanes.** Lanes are addressed by slug *inside* a workspace, so
  two workspaces can both own a `notes` lane. The global unique index on
  `category.slug` was replaced by a composite `(workspace, slug)` index, and the
  legacy-dedupe pass now groups by that pair before the index is rebuilt. The
  default workspace keeps its readable `category:<slug>` ids; every other
  workspace gets generated ids, so a new lane can never overwrite an existing
  one.
- **Per-workspace context roots.** `workspace.context_roots` is the allow-list
  for chats in that workspace, editable from Settings → AI. A disabled root is
  invisible to the picker *and* rejected server-side — the tree, file, and write
  endpoints resolve the root through the workspace, so a guessed id returns 404
  exactly like an unknown root. An empty list means "all configured roots", the
  pre-existing behaviour, and a workspace can never be left with none.
- **PDF and image context.** Context roots now cover `.pdf` and images as well
  as text. PDFs contribute extracted text (`extractPdfText`, the same routine
  used for attachments) and images are sent to the model as multimodal
  `image_url` data-URL parts on the current turn only, capped at four per message
  and 2 MiB each. The picker marks each entry by kind, and Save-as-note is
  offered only where there is real text.
- **Study review analytics.** Every grading now writes a `study_review` row
  (grade, box before/after, interval, item, note), so retention is derived from
  history instead of only from the counters on a card. `GET /api/study/analytics`
  returns totals (retention, reviews, lapses, reviewed cards, average box, due
  now), per-tag retention, lapse hotspots, a seven-day due forecast, and a
  fourteen-day activity strip; the Study view renders all of it and refreshes
  after each grade.

## Chat context roots, prompt library, and study surfaces (`workspace-v5`/`workspace-v6`)

The knowledge-base slice turned the note stream into study material and gave
chats a bounded, auditable view of the files a task is about:

- **Spaced recall (Phase 5).** `study_item` records carry the Leitner box,
  `due_at`, review count, and lapses; `POST /api/study/generate` builds cards
  from a note offline (or through a provider), and grading an answer schedules
  the next review. The Study view shows box counts, the due queue, and the
  answer reveal.
- **Markdown bundles and import.** `GET /api/export/markdown` streams a `.zip`
  of linked markdown files for a lane or tag (dependency-free, zlib-based),
  with front-matter that re-imports cleanly; the importer skips content that
  already exists so a folder can be re-imported.
- **Attachment text.** Attachments extract text (`.md`, `.txt`, PDF text
  streams) so a file can become a note in one click (`/api/attachments/:id/to-note`).
- **Knowledge graph.** `GET /api/graph` returns notes and their wiki-link edges;
  the Graph view renders a deterministic, layout-stable SVG graph.
- **Chat context roots (new).** A chat can now read real files. Roots are
  configuration-only (`BLINKO_CONTEXT_ROOTS`, or `project` / `documents` /
  `notes` defaults): the **project** root is the repository mounted read-only at
  `/app/context`, while **documents** and **notes** are writable and live in the
  persisted data volume. `GET /api/context/roots`, `/tree`, and `/file` browse
  and read inside a root; every path is resolved lexically *and* through
  `realpath`, so parent traversal and symlink escapes are rejected before any
  filesystem call. The composer attaches up to 12 files per message (single
  file or a whole folder), the session stores them as `context_files` refs, and
  each message ships a bounded read-only `WORKSPACE FILES` block to the model —
  the browser only ever names files the server already exposes.
- **Prompt library.** `PATCH /api/prompts/:id` edits custom prompts; built-ins
  stay read-only and are cloned with **Duplicate** from Settings → AI. The chat
  toolbar picks any library entry per session.
- **Writable documents root.** `POST /api/context/roots/:root/file` writes only
  into writable roots, so a task can put its artifact next to the material it
  was given. A context file can also be promoted into notes in one click.
- **Translation parity is enforced.** `tests/i18n-parity.spec.mjs` fails the
  suite when a locale is missing a key, when a `data-i18n*` hook in the shell
  does not resolve in every locale, or when Arabic copy is left untranslated —
  new copy can no longer ship half-translated.

## Implemented in `workspace-v3`

The following are deployed in the current runtime (schema `workspace-v3`) and
are no longer open items:

- A `workspace` record with name, description, default category, and an
  agent operating-context field, exposed through read/write settings APIs.
- Role-based access control with `superadmin`, `admin`, `editor`, and `viewer`
  roles and permission guards (`notes:read`, `notes:write`, `categories:write`,
  `members:write`, `settings:write`) enforced server-side on every mutating
  endpoint.
- Member management APIs: list, create, role change, and removal, with
  self-protection rules and superadmin-only escalation.
- A redesigned workspace shell with Notes, People, and Settings views,
  permission-aware navigation, and a responsive GPT-taste-derived design
  system with dark mode.
- Complete English/Arabic localization: a single translation catalog, `lang`
  and `dir` switching, RTL layout, translated metadata, aria labels, dynamic
  role names, plural-aware note counts, and persisted locale preference.
- Playwright coverage for admin onboarding, category/note flows, settings
  saves, Arabic RTL switching, mobile-viewport overflow checks, and invalid
  credentials; live API checks for the viewer permission boundary.

## Phase 2 closeout and the first Phase 4 slices (`workspace-v12`)

This slice closed the last Phase 2 item and took the two Phase 4 items that do
not depend on an engine upgrade:

- **Retention controls (Phase 2 closeout).** `workspace.retention_days` (1–3650
  whole days, `NONE` = keep forever) is edited in Settings → Data → Retention
  through `PATCH /api/settings`, alongside `purge_after_days` for future use.
  `purgeExpiredContent()` runs at boot's hourly sweep and on demand through
  `POST /api/retention/purge` (permission-gated by `settings:write`, recorded
  as a `retention.purge` audit event): recycle-bin notes past the window are
  hard-deleted with their attachments — rows and files — inside one
  transaction, and soft-deleted comments older than 30 days are dropped. The
  sweep also prunes the telemetry ledger past 30 days, so the table cannot grow
  without bound (the read API only looks back 168 h). It reports
  `{ purgedNotes, purgedComments, purgedMetrics }`, so an empty bin is a
  provable no-op rather than a silent success.
- **Transactions for multi-record mutations (Phase 4).** A `transaction()`
  helper issues `BEGIN TRANSACTION; … COMMIT TRANSACTION;` over the query
  endpoint with optional bound variables. Note deletion (attachments, comments,
  wiki links, then the note row), invite redemption (claim the code, write the
  membership edge, switch the account's active workspace), and the retention
  purge are now atomic — a failure between the statements rolls the whole batch
  back instead of leaving an orphaned edge or a claimed invitation with no
  membership.
- **Query-budget telemetry (Phase 4).** The `query_metric` ledger records one
  row per query shape with `duration_ms`, an `ok`/`error_kind` outcome, and the
  workspace, and is read back through `GET /api/telemetry/queries` (per-shape
  totals, avg/max latency, failures by kind, 1–168 h window, capped at 50 rows
  per section). Shapes are caller-declared names such as `notes.list` or
  `graph.notes` — no SQL text, no bound values, and no note content ever reaches
  the table, which is why it is safe to keep the ledger in the workspace
  database. Writes are buffered and flushed at 200 rows, every 30 s, and after
  each retention sweep, so a quiet deployment still persists its ledger.
- **Verification.** Server-level smoke runs against a disposable engine
  confirmed the purge deletes a backdated recycle-bin note (and its rows), that
  a failing statement inside a transaction leaves no partial state behind, and
  that the ledger records shapes with latency. Playwright covers the retention
  form (set, persist, clear back to forever), the non-destructive purge path,
  and the ticket custom-field flows; `npm test` is 39/39 green (32 main + 7
  extra config).

## Product direction

Make the workspace more useful for teams and AI models without returning to an
ORM or a second database. SurrealDB should remain the source of truth for
identity, content, permissions, retrieval metadata, and model execution state.

## Staged enhancements

### Phase 1 — safer daily use

- ~~Add note editing, archive, restore, and recycle-bin views.~~ Shipped in
  `workspace-v4` (see above).
- ~~Add pagination and cursor-based loading ordered by `updated_at`.~~ Shipped
  in `workspace-v4` (keyset cursor pages, Load-more flow).
- ~~Add optimistic UI with retryable mutations and an offline outbox.~~ Shipped
  in `workspace-v4`: note mutations apply instantly client-side, network
  failures queue in an outbox with backoff + online/reconnect flushing, 4xx
  rejections roll back and surface the error. Express ETag was disabled on
  `/api/*` because its 304 replays served stale note lists after mutations;
  Playwright now boots a disposable SurrealDB engine container instead of the
  shared deployed engine.
- Add category color/icon editing and category deletion with note reassignment.
  ~~Shipped in `workspace-v4` (see above).~~
- ~~Add full-text search backed by a SurrealDB index when the deployed engine
  supports it; keep a bounded `string::lowercase` fallback for v1.~~ Shipped:
  the pinned v1.5.6 engine supports `SEARCH ANALYZER` with BM25, so search is
  fully indexed with no fallback path needed.
- ~~Add export/import using versioned JSON and a SurrealDB backup runbook.~~
  Shipped in `workspace-v4`: `GET /api/export` (existing) plus a new idempotent
  `POST /api/import` (`settings:write` gated) that restores versioned JSON
  without duplicating existing categories, tags, or notes; Settings → Data
  exposes file import with full EN/AR strings. The engine-level backup and
  restore procedure is documented in
  `docs/plans/repository/blinko-surrealdb-backup-runbook.md`. **Phase 1 is
  complete.**

### Phase 2 — team workspaces (remaining after `workspace-v3`)

Shipped in `workspace-v4` (single default workspace):

- ~~`workspace_member` graph edges and `workspace_invitation` records with an
  invite flow~~ — Settings → People creates one-time codes (viewer/editor/admin),
  lists and revokes pending invitations, and registration redeems a code into a
  membership edge. Roles resolve from membership, not the account row.
- ~~Workspace scoping enforced in SurrealQL~~ — every category and note query
  filters on the workspace record; note/category mutations require membership.
- ~~Note sharing and audit events~~ — `PATCH /api/notes/:id/share` toggles a
  public share, `/share/:id` renders a read-only page, and mutations record
  `audit_event` rows surfaced in Settings → Activity (`GET /api/audit`).
- Playwright covers the invite→register round trip, code reuse rejection,
  public share access and unshare, and audit visibility; full EN/AR localization.
- ~~Upgrade markdown rendering to the upstream Blinko quality~~ — a shared,
  dependency-free GFM renderer (`runtime/public/markdown.mjs`) now powers note
  cards and public share pages identically: tables (with alignment), task lists
  with checkboxes, nested lists, blockquotes, `==highlights==`, language-tagged
  code blocks, safe-link images and autolinks, and thematic breaks. All input is
  escaped before tag emission, so note content cannot inject HTML.
- ~~Preview data~~ — `POST /api/samples` loads curated idempotent sample notes
  (markdown showcase, agent brief, spec checklist, an Arabic RTL note) through
  the same import core as JSON restore; Settings → Data exposes a
  Load-samples button with EN/AR strings, and note cards gained a copy-markdown
  action and an edited badge.

Still remaining for full multi-tenancy (the first two are now done):

- ~~Extend from the single `workspace:default` record to multiple workspaces~~
  — shipped in `workspace-v7`.
- ~~Add owner and commenter roles on top of the existing four~~ — shipped in
  `workspace-v8`, together with per-workspace invitations.
- ~~Add comments on notes~~ — shipped in `workspace-v9`; per-note activity
  history followed in `workspace-v11` (`note_activity` rows + a History pane
  on the note card), closing the gap that the audit stream is workspace-wide.
- ~~Add retention controls, soft deletion, and per-workspace export~~ —
  per-workspace export shipped as the `workspace-v10` bundle; retention
  controls and the recycle-bin purge sweep shipped in the Phase 2 closeout
  slice (Settings → Data → Retention), together with the transactions and
  query telemetry described under Phase 4.
- Add rate limits and security events for registration, login, and token use
  — shipped in `workspace-v11` (fixed-window counters per IP/identity backed
  by `rate_limit_hit`, `security_event` rows for login/register/invite/token
  outcomes, surfaced in Settings → Activity).

### Phase 5 — study notes and knowledge base

The review skills installed for this workstream (`book-study`,
`knowledge-base`, `ai-exam-coach`, `obsidian-vault-builder`) share one model:
capture → link → review on a schedule. The shipped slice covers capture
(markdown files), linking (`[[wiki links]]` + backlinks), and assisted study
(prompt templates). The remaining backlog, in dependency order:

- **Spaced recall records.** Add `study_item` rows (question, answer, source
  note, box, due date) with a `GET /api/study/due` endpoint, so a note can be
  turned into flashcard/quizzable cards and surfaced on a review schedule
  rather than only read. This is the highest-value gap: everything else is
  organisation, this is retention.
- **Note → card generation.** Reuse the chat completion path with the seeded
  flashcard prompt to write `study_item` rows from a note, keeping the review
  queue inside the workspace instead of a separate tool.
- **Graph and tag taxonomy.** A read-only graph view (notes as nodes,
  `[[wiki links]]` as edges) plus hierarchical tags (`subject/chapter`) would
  make larger study sets navigable. Backlinks already expose the data the graph
  needs; only rendering and tag parsing are missing.
- **Markdown bundle export.** Export a lane or tag as a `.zip` of `.md` files
  with front-matter-tagged links, so the workspace is portable to any
  markdown editor (and re-importable through the existing importer).
- **Attachment-aware study.** Attachments are metadata-only today; extracting
  text from uploaded PDFs and MD files into note content would let book and
  paper material flow through the same link-and-review pipeline.
- **Per-workspace model policy for study flows.** Tie prompt selection to the
  active provider so a study workspace can default to a specific model, which
  is the Phase 3 dependency that gates multi-workspace model routing.

### Phase 3 — AI model operations

- ~~Per-workspace provider policy and run records~~ — shipped in
  `workspace-v11`: `GET/PATCH /api/ai/policy` (allow-list, default provider,
  hourly run cap) gates every chat and study-generation call through
  `resolveProviderForWorkspace`, and each provider round-trip writes an
  `ai_run` row (feature, model, prompt/response size, latency, error) listed
  at `GET /api/ai/runs`. Settings → AI exposes the policy editor and ledger.
- Add `ai_model`, `agent`, `agent_run`, and `agent_message` records with
  workspace ownership and encrypted provider configuration (the `ai_run`
  half of this line shipped in `workspace-v12` with the ledger).
- Let a workspace select approved models and define capabilities, context
  limits, temperature, tool access, and data-retention policy.
- Add retrieval scopes by category, explicit note citations, and a per-run
  context manifest so model answers are explainable.
- Add queued runs, retry policy, cancellation, token/cost accounting, and
  idempotency keys. Keep job state in SurrealDB; use a separate worker only
  when execution needs isolation — the queue half shipped in `workspace-v12`
  (`ai_job` rows with a conditional-UPDATE claim, exponential backoff to a
  max-attempts limit, cancel-before-running), alongside token/cost accounting
  on every `ai_run` (provider-reported usage or a length estimate, cost from
  a per-model pricing table in micros) and enforcement of the per-workspace
  hourly cap: chat and study-generation answer 429 once the budget is spent,
  offline extraction stays available, and the Settings → AI panel shows
  this-hour usage plus per-provider tokens and estimated cost.
  `workspace-v13` completed this line: enqueues are **idempotent** (a caller
  key or a derived operation identity dedupes active jobs, so a retry or
  double-click can never double-spend provider budget; terminal jobs release
  their key for deliberate re-runs), jobs accept a **scheduled** `runAt` (up
  to an hour ahead), and the **monthly budget** (`monthlyBudgetMicros` on the
  workspace policy) answers 429 with its own refusal message across chat,
  study generation, and job enqueue once this month's ledgered spend exceeds
  it — unpriced models cost zero by design, so budgets gate priced models.
- Add MCP/tool permissions as explicit workspace grants, never implicit model
  access.

### Phase 4 — SurrealDB-native scale

- Upgrade the engine and client together after compatibility tests pass.
- Add record links for workspace, category, note, run, and actor relations.
- Add full-text and vector indexes for hybrid retrieval.
- ~~Use transactions for multi-record mutations such as invitations, sharing,
  note versioning, and agent runs.~~ — shipped: `BEGIN/COMMIT` batches now wrap
  note deletion (attachments + comments + wiki links + the note row), invite
  redemption (claim + membership edge + active-workspace switch), and the
  retention purge. Category deletion reassigns its notes before removal, so it
  stays a separate read-then-write pair rather than one batch.
- Add live queries for team activity and agent run progress. — **deferred with
  reason:** the deployed topology frequently runs more than one runtime
  process against one engine, so an in-process WebSocket subscription would
  only ever see its own process's writes. The Activity surfaces stay
  poll-on-open until the runtime is guaranteed single-writer per workspace, or
  the subscription is moved to a shared worker that fans out to clients.
- Add namespace/database isolation for larger tenants and a tested backup,
  restore, and point-in-time recovery procedure — namespace-per-run isolation
  is exercised by the Playwright harness, which gives every run its own
  namespace/database pair; the deployed backup/restore procedure lives in
  `blinko-surrealdb-backup-runbook.md`.
- ~~Add query-budget telemetry: latency, scanned records, result counts, and
  failed queries with secrets and note content redacted.~~ — shipped as the
  `query_metric` ledger behind `GET /api/telemetry/queries` (per-shape totals,
  avg/max latency, failure counts by error kind over a 1–168 h window). Shapes
  are caller-declared names, so no SQL text, bound values, or note content is
  ever recorded.

## Data model target

```text
workspace ──< workspace_member >── account
    │
    ├──< category ──< notes
    ├──< agent ──< agent_run ──< agent_message
    ├──< ai_provider ──< ai_model
    └──< audit_event
```

Every user-controlled query must include the authenticated account and
workspace boundary. Every AI run must retain the selected model, prompt policy,
retrieved note ids, actor, status, and timestamps so the result can be
replayed or audited without storing provider secrets in note content.

## Accuracy and quality gates

1. API contract tests cover authentication, authorization, category ownership,
   note CRUD, pagination, search, and invalid input.
2. SurrealDB integration tests run against the exact engine version used by
   Compose; no PostgreSQL service or Prisma fixture is required.
3. Browser tests cover first-admin setup, sign-in, responsive category controls,
   note creation, error recovery, and theme preference.
4. Migration tests verify idempotent import, export round trips, and backup
   restore before enabling a new schema version.
5. Performance checks establish targets for p95 list/search latency and
   bounded query result sizes before team or AI features ship.
6. Security checks verify that users cannot read, mutate, or retrieve notes
   outside their workspace, category grants, or agent context policy.

## Delivery order

Phase 1 is complete, and the Phase 2 foundation (membership, invitations,
workspace-scoped SurrealQL, sharing, audit events) is shipped in
`workspace-v4`, together with the study-notes slice (wiki-link graph, markdown
file import, study prompt templates). Public share links, note editing, search,
and markdown file import are all live and verified end to end.

Multiple workspaces, per-workspace context roots, PDF/image context, recall
analytics, and the membership half of Phase 2 (owner/commenter roles and
per-workspace invitations, `workspace-v8`) are shipped, and **Phase 2 is
complete**: note comment threads landed in `workspace-v9`, reusing the
`comments:write` permission and the `commenter` role that shipped one slice
earlier. The first Phase 3 slice is now shipped as `workspace-v11`: per-
workspace provider policy, the `ai_run` ledger, per-note activity history,
and rate limits + security events for the auth surfaces. The Phase 2 closeout
(retention + purge, `workspace-v12`) also carried the first two Phase 4 items —
transactional multi-record mutations and the `query_metric` telemetry ledger —
leaving engine/client upgrades, record-link and index work, live queries, and
namespace-per-tenant isolation as the remaining Phase 4 scope.

## Remarks & Notes

### Context roots stay server-side by design

A chat attachment is a **reference**, not a filesystem handle: the browser names
`root:path`, the server re-validates it against its configured roots, and only
then reads it. In review a batch of three refs — one real file, one missing
path, one traversal attempt — was accepted as exactly one, with `rejected: 2`
returned to the client instead of a silent drop. Attaching before a provider
exists still stores the refs, so the context survives an outage.

### What tenancy deliberately does not split

Two things stay instance-wide, on purpose. **AI providers** are addressed by
name (`ai_provider:<name>`) and are shared by every workspace, because they hold
deployment credentials rather than content. Phase 3 (`workspace-v11`) added
the per-workspace control plane on top: a policy (allow-list, default, cap)
that decides which of the shared providers a workspace may actually reach.
**Tags** are one shared vocabulary: the `tag`
record is created once by name and reused, while the note↔tag links and the
counts shown in the UI are workspace-local. A workspace therefore never sees
another workspace's notes through a tag, but `#study` means the same thing
everywhere, which is what makes tags worth having.

### A helper that reached for a request it never received

`applyImport` gained `req.workspaceId` during the tenancy pass while its
signature only takes `(body, accountSub, options)`, so JSON import and the sample
loader failed with a bare `req is not defined` — the catch-all returned a 500
with only "Import failed partway", and the sample loader reported a partial
load. The workspace id now travels through the options object, and the smoke run
covers import and samples explicitly.

### Membership edges need real record links

Creating a workspace wrote its membership edge with `created_by` as a plain
account id string, which `option<record<account>>` rejects in schemafull mode
(`Found 'x' for field created_by`). The edge write now passes a `RecordId`, the
same class of bug the RELATE and option-field failures hit earlier: on this
engine, a record-typed field needs a record, not a string that looks like one.

### Sending a message without a prompt style

`prompt_id` is an `option<string>` field on a `SCHEMAFULL` table, and v1.5.6
rejects an explicit `null`. Creating the user message always passed `promptId`,
so the first message of a chat with no prompt style selected failed with
`Found NULL for field prompt_id`. The field is now only written when a style is
actually chosen — the same class of bug that produced the earlier audit-event
failure.

- The current runtime is intentionally smaller than the ignored upstream
  reference checkout. Features from that checkout are not considered migrated
  until they have a SurrealDB schema, API contract, tests, and browser coverage.
- SurrealDB v1.5.6 is pinned in `application/tools/planing/docker-compose.yml`.
  Engine/client upgrades must be treated as a compatibility project, not a
  dependency-only change.
- Do not place provider API keys, JWT secrets, or passwords in notes, fixtures,
  screenshots, or documentation.
- The wiki-link graph is deliberately markdown-derived (`[[Title]]` matched
  against note titles) rather than a separate edge table: notes remain plain
  portable text, there is no second source of truth to keep in sync, and the
  backlink query is a bounded `string::lowercase(content) CONTAINS` scan. If the
  graph view in Phase 5 ships, revisit this with a real edge table written at
  note-save time.
- Chat context roots are deliberately capped (12 files per message, 256 KiB per
  file, 96 K chars per assembled block) and filtered by extension. Raising those
  limits is a provider-window decision, not a UI one: the block travels in the
  system message and pays for itself on every turn of the conversation.
- The Playwright suite points the context roots at disposable fixtures created
  by `playwright.config.mjs`, so the tests never read the deployed project tree
  and never write into real documents. The suite also fails if a locale is
  missing a key or if a `data-i18n*` hook in the shell resolves nowhere.
- Playwright restarts the worker process after a failing test, which
  re-evaluates the spec module. Shared fixtures must therefore be pinned outside
  the module — the run id lives in the config env (`PLANING_PW_RUN`) and the
  seeded admin name in a temp file keyed by that id — otherwise later tests sign
  in as an account that was never created.
- Element-level `data-i18n-title` must not be used on arbitrary containers: only
  the document `<title>` sets the page title, every other element receives the
  value as its own `title` tooltip. The reverse order silently overwrote the
  page title with the last matching attribute on the page.

### Four SurrealDB v1.5.6 traps worth knowing before the next slice

Each of these cost real debugging time and none of them fails at parse time, so
they are recorded here rather than re-discovered:

- **A `SCHEMAFULL` `option<object>` field strips its untyped inner keys.**
  `custom_fields` on `ticket` accepted the object and came back `{}` — the
  engine validates nested keys too. The fix is to declare the sub-field
  (`DEFINE FIELD custom_fields.* TYPE string;` with a `flexible` variant where
  several types are expected), exactly as `attachments.*` already does. Objects
  stored into a *schemaless* table are unaffected, which is what makes this
  look like an SDK bug in a quick probe.
- **Aggregate subqueries return arrays, not scalars.**
  `(SELECT count() FROM … GROUP ALL).count` yields `[1]`, which an
  `option<number>` field rejects. Extract with `VALUE` (or unwrap the array)
  instead of binding the subquery result directly.
- **The SDK encodes JS `null` as SurrealDB `NULL`, and `option<T>` rejects
  `NULL`.** Clearing a field needs `NONE` (`SET field = NONE`), and a helper
  that filters `null` out of its assignments — `literalAssignments` here — will
  silently drop the clear entirely, so the old value survives a "successful"
  request. Both the settings PATCH (retention window) and the notes PATCH
  (planning dates, event colour) now build explicit `NONE` assignments, and a
  Playwright test pins the note-date case.
- **The SDK serializes an ISO *string* as a SurrealDB string, not a datetime.**
  `updated_at < $cutoff` with `cutoff` passed as an ISO string never matches,
  so a retention sweep silently purges nothing; binding a `Date` object makes
  CBOR encode a real datetime and the same query works unchanged.
