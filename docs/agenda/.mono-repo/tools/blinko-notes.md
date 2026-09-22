---
Object type: Tool
Tags: tool, blinko, notes, ai, surrealdb
Status: Active
Category: Operations
Related Features: documentation-system
object:
  type: "document"
  id: "docs.agenda..mono-repo.tools.blinko-notes"
attributes:
  source_path: "agenda/.mono-repo/tools/blinko-notes.md"
  canonical_route: "/docs/en/agenda/.mono-repo/tools/blinko-notes"
  section: "agenda"
  owner: "workspace"
  status: "maintained"
  source_of_truth: "repository-markdown"
tags:
  - "structa-cloud"
  - "documentation"
  - "agenda"
links:
  - label: "Documentation home"
    to: "/docs/en/"
    icon: "i-lucide-house"
  - label: "Source file"
    to: "https://github.com/mammhoud/structa.cloud/blob/generic/docs/agenda/.mono-repo/tools/blinko-notes.md"
    icon: "i-simple-icons-github"
    target: "_blank"
  - label: "Owner: workspace"
    to: "/docs/en/agenda/.mono-repo/tools/blinko-notes"
    icon: "i-lucide-link"
---

# Blinko — Self-Hosted Personal AI Notes

> **Description:** Self-hosted personal AI note tool (open source, privacy-first) served at `tools.structa.cloud/notes/` via the tools-proxy Nginx.

## Method

- JWT sessions issued by the tracked runtime (`runtime/server.mjs`) with role-based membership edges (`superadmin`/`owner`/`admin`/`editor`/`commenter`/`viewer`) and invitation-code registration; NextAuth is no longer used. The role a request carries is the membership role for its active workspace, not the account's global row
- Markdown-first notes on a `SCHEMAFULL` note table: pin, archive, recycle, tags, lane assignment, full-text search (SurrealDB `SEARCH ANALYZER` + BM25)
- Wiki-link graph: `[[Note title]]` chips render in note cards and public share pages, with an inline panel listing outgoing links and backlinks
- Markdown file import (`.md`/`.mdx` picker or drag-and-drop) that skips content already present, so a folder can be re-imported safely
- Markdown bundle export: a lane or tag downloads as a `.zip` of linked markdown files whose front-matter re-imports cleanly
- Public, read-only share pages at `/share/<note-id>` (GFM) with raw markdown at `/share/<note-id>/raw`; the share flag is off by default, so a note is only reachable once shared
- Attachment text extraction (`.md`, `.txt`, PDF text streams) so an uploaded file can become a note in one click
- Spaced recall built from notes: cards carry a Leitner box and a due date, grading an answer schedules the next review, and the Study view shows the due queue and box counts
- AI chat over any OpenAI-compatible provider, with provider keys stored server-side and never returned to the browser; a prompt library (built-in styles are read-only, duplicate one to edit it) is selected per chat session
- Chat context roots: a chat attaches real files — singly or as a whole folder, up to 12 per message — from configured directories (the `project` root is the repository mounted read-only at `/app/context`; `documents` and `notes` are writable roots inside the data volume). Markdown and text are read, PDF text is extracted, and images travel to the model as multimodal parts; the server resolves each `root:path` reference itself and sends a bounded read-only `WORKSPACE FILES` block with the message, so the browser never handles a filesystem path
- Workspace bundles: Settings → Data exports a whole workspace as one JSON envelope (settings, lanes, tags, notes with ids, study cards, comment threads, prompts, attachment metadata) and imports a bundle as a **new** workspace, so a workspace can move between deployments. Ids are preserved when free and remapped when taken, with cards and comments following the remap; attachment bytes stay in the source deployment's volume
- Multiple workspaces: an account holds memberships, `active_workspace` records the selected one, and notes, lanes, chats, study cards, reviews, prompts, integrations, and audit events are all scoped to it. The sidebar switches workspaces; Settings → General creates, renames, and archives them
- Note comment threads: a note card opens an inline thread (author, timestamps, edited marker, markdown bodies, inline edit). Comments repeat the note's workspace, so a thread is unreadable from another workspace; `comments:write` decides who may reply, authors manage their own replies, and members who manage people moderate the thread
- Per-workspace invitations: Settings → People creates, lists, and revokes codes for the workspace you are in (another workspace's code is neither listed nor revocable), each code carries a 14-day expiry, and a role it is allowed to grant. Registration redeems a code into the issuing workspace; an account that already exists joins with `POST /api/invitations/redeem` from the same tab and is switched there
- Ownership and commenter roles: `owner` holds the workspace (the only role that can hand out ownership or archive it) and `commenter` reads and replies. A member can only grant a role at or below their own rank, the last owner of a workspace cannot be demoted or removed, and creating a workspace makes the creator its owner
- Per-workspace context roots: each workspace allow-lists which configured directories its chats may read, enforced in the tree, file, and write endpoints, not just hidden in the picker
- Study review analytics: every grading is logged, and retention per tag, lapse hotspots, a seven-day due forecast, and a fourteen-day activity strip are derived from that history
- AI policy and run ledger (`workspace-v11`): each workspace allow-lists providers, pins a default, and caps AI runs per hour — the cap is enforced (`workspace-v12`): chat and study generation answer 429 once the hourly budget is spent while offline extraction keeps working. Every provider round-trip writes an `ai_run` row with feature, model, sizes, latency, token counts (provider-reported or estimated), and estimated cost from a per-model pricing table; the Settings → AI panel shows this-hour usage plus per-provider tokens and cost. Auth surfaces are rate-limited per identity through fixed-window counters, and login/register/invite/token outcomes land in a security-event feed beside the workspace audit stream
- Queued AI runs (`workspace-v12`): `ai_job` rows hold the whole lifecycle (queued → running → succeeded/failed/cancelled) in SurrealDB, claimed by an in-process worker through a conditional UPDATE so a job can never run twice; failed attempts retry with exponential backoff up to the job's attempt limit, and queued jobs can be cancelled by their requester or a workspace admin until they start. A restart re-queues jobs that were mid-flight
- Idempotent, schedulable jobs with a monthly budget (`workspace-v13`): enqueues dedupe on a caller key or a derived operation identity so a retry or double-click never double-spends provider budget, terminal jobs release their key for deliberate re-runs, a `runAt` schedule defers first execution up to an hour, and a per-workspace `monthlyBudgetMicros` answers 429 with its own refusal across chat, study generation, and job enqueue once the month's ledgered spend exceeds it
- Per-note activity history: every note mutation writes a `note_activity` row, and the note card's History pane shows that timeline (action, actor, time) without filtering the workspace-wide audit stream
- SurrealDB store (`surrealdb:v1.5.6`, `file:/data/blinko.db`) accessed exclusively through the `surrealdb` JS SDK — no Prisma, no PostgreSQL, no SQL over HTTP ad hoc
- Compose: `application/tools/blinko/docker-compose.yml`; data in `blinko-data/` (gitignored)

## Boundary

- Pin SurrealDB to the 1.x line (`surrealdb.js@^1.0.0` rejects v2/v3)
- Shell-less surrealdb image — readiness via `/surreal isready`
- The HTTP transport signs in once per process; the runtime re-signs in and retries on an auth error so a long-running deployment recovers from an engine restart without redeploying
- Context roots are configuration-only (`BLINKO_CONTEXT_ROOTS`, or the `project` / `documents` / `notes` defaults; `BLINKO_CONTEXT_DIR` sets the host directory mounted read-only at `/app/context`). A request picks from the roots its workspace allows but can never introduce a path, and paths are validated lexically and through `realpath`, so traversal and symlink escapes fail before any filesystem read
- Tenancy splits content, not credentials: AI providers stay instance-wide (they hold deployment keys), and the `workspace-v11` policy decides which of them each workspace may reach; tags are one shared vocabulary whose links and counts are workspace-local
- Roles are stored on the `workspace_member` edge, so a role change in one workspace never follows an account into another; a workspace must always keep at least one owner, and `superadmin` is not grantable from the People tab
- The Playwright suite fails on a missing translation key, an unresolved `data-i18n*` hook, or untranslated Arabic copy, and it points the context roots at disposable fixtures instead of the deployed project tree

## Use case

Team members take private AI-assisted notes and build study material from them: markdown files are imported, related notes are linked with `[[wiki links]]` and navigated through backlinks, study prompts turn source notes into summaries, flashcards, and revision sheets, review cards schedule themselves through spaced recall, and retention per tag shows which material is actually sticking. A chosen note can be published as a read-only markdown link, and separate workspaces keep a team's, a client's, or a research line's notes apart while sharing one deployment. When the work is about real files rather than notes, a chat attaches a directory from the read-only project mount or a writable document folder — including PDFs and images — so the model reads the material it was asked about without the browser ever touching the filesystem.

## Related

- → `surrealdb-store.md` — Storage layer
- → `../../diagrams/blinko-surrealdb.md` — Topology + data flow
- → `../guides/deployment.md` — Deployment method
- → `../objects/tool.md` — Tool object type
