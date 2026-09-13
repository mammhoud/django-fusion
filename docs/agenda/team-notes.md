---
title: Team Notes
description: Meeting notes, decisions, blockers, and team communication log — the project's institutional memory
navigation:
  title: Team Notes
  icon: i-lucide-notebook-pen
object:
  type: "guide"
  id: "agenda.team-notes"
attributes:
  source_path: "agenda/team-notes.md"
  canonical_route: "/docs/en/agenda/team-notes"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - team-notes
  - decisions
  - meetings
  - log
links:
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "Meeting Agenda"
    to: "/agenda/meeting-agenda"
    icon: "i-lucide-calendar"
  - label: "Feature Tracking"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
---

# 📝 Team Notes — Meeting Notes, Decisions & Blockers

> **Purpose:** The team's written memory — meeting notes, key decisions, blockers, and notable events. Searchable, date-stamped, and linked to features and tasks.
> **Last updated:** 2026-09-06

---

## 📋 Note Entry Format

Every entry should be date-stamped and categorized:

```markdown
### YYYY-MM-DD — [Meeting type / Event] — [Brief title]

**Attendees:** @member1, @member2, @member3

**Topic / Agenda:** [What this meeting/event was about]

**Key points:**
- Point 1
- Point 2

**Decisions made:**
- Decision 1 — [rationale if notable]
- Decision 2

**Action items:**
- [ ] @assignee — Task description — due YYYY-MM-DD
- [ ] @assignee — Task description — due YYYY-MM-DD

**Blockers / Risks:**
- Blocker description — owner: @member

**Links:**
- Related feature: [`feature-tracking.md`](./feature-tracking.md) § Feature Name
- Related task: [`task-tracking.md`](./task-tracking.md) § Task Title
- Related plan: [`plans/path.md`](../plans/README.md)
- Meeting agenda: [`meeting-agenda.md`](./meeting-agenda.md)
```

---

## 🗓️ Meeting Notes Log

### 2026-09-13 — Agenda maintenance — Render pipeline + plan-link repair

**Attendees:** @mahmoud (General Manager) — maintenance change, no meeting held.

**Topic / Agenda:** Two stale-target defects: the agenda diagram renderer duplicated the `.mono-repo` diagrams on every run, and `docs/plans/` carried unresolved relative links to removed or renamed Precis paths.

**Key points:**
1. **Root cause** — a leading dot-directory sanitized to a leading hyphen, so the renderer asked for `-mono-repo-*` while the eight committed images are `mono-repo-*`; the skip-check missed and each run re-rendered and re-inserted them.
2. **Fix** — `slugFor()` now trims leading separators after sanitizing. A full run reports `0 rendered, 60 skipped, 0 failed` and writes no files, so the pipeline is idempotent again.
3. **Plan links** — fourteen unresolved links in `docs/plans/` were repointed at the current tree; the folder now has zero unresolved relative links.

**Decisions made:**
- Generated slugs must stay stable across directory renames; renaming a directory that contains rendered diagrams is a slug-affecting change to verify, not a no-op.
- Deleted plan targets are de-linked with their removal date instead of pointing at a missing file.

**Action items:**
- [ ] @mahmoud — Note in the plan-review checklist that moving a directory containing rendered diagrams requires checking the slug output

**Links:**
- Renderer: [`../scripts/render-agenda-diagrams.mjs`](../scripts/render-agenda-diagrams.mjs)
- Change log: [`SUMMARY.md`](./SUMMARY.md) § 2026-09-13

---

### 2026-09-13 — Agenda maintenance — Feature Tracking split per product

**Attendees:** @mahmoud (General Manager) — maintenance change, no meeting held.

**Topic / Agenda:** `feature-tracking.md` had grown to 2,282 lines with nine products in one file, so nobody could find their own product's table.

**Key points:**
1. **Split, not a rewrite** — the nine product sections moved verbatim into `feature-tracking/`, one file each; the original file became a hub. Verified line-by-line against the pre-split copy: zero content loss.
2. **References kept working** — the hub still carries a heading per product, so existing `feature-tracking.md § <Product>` pointers resolve instead of breaking.
3. **New products** now get their own file plus one hub pointer, rather than appending to a monolith.

**Decisions made:**
- The **finished-milestone log** is now per product: record a ✅ Shipped milestone in the owning product's file, not in the hub.
- The hub holds only the lifecycle contract, status definitions, entry template, index, and shipped roll-up. Feature entries never go in the hub.
- `link-agenda-relations.mjs` reads `feature-tracking/` as a source directory so role ↔ object relations keep resolving.

**Action items:**
- [ ] @moustafa — Confirm the three P0 Syntara features (`Owner: TBD`) get real owners — carried over from Sprint 2 backlog

**Links:**
- Hub: [`feature-tracking.md`](./feature-tracking.md)
- Per-product files: `feature-tracking/` (9 files)
- Change log: [`SUMMARY.md`](./SUMMARY.md) § 2026-09-13

---

### 2026-09-10 — Kickoff Meeting — Agenda System Adoption (CONTENT_MODEL § 5)

**Attendees:** Workspace team — @mahmoud (General Manager, presiding), @moustafa (Product Manager + Marketing), @yahia (Front-end + UX), @asmaa (Data Development), @dariia (Contributor)

**Topic / Agenda:** First team meeting on the agenda system, walked in the order defined in [`CONTENT_MODEL.md`](./CONTENT_MODEL.md) § 5. Held ahead of the 2026-09-16 due date.

**Key points (per agenda item):**
1. **Content model (CONTENT_MODEL.md)** — reviewed the four packages (A team delivery, B Anytype import set, C canonical plans, D product docs) and the separation rules. Team aligned: the agenda is the working memory; `docs/plans/` stays the only plan source.
2. **Hub (MAIN.md)** — walked the business star schema: facts (milestones, tasks, leads, claims) × dimensions (products, teams, sprints, plans). The sales pipeline file completes the fact set — no objections.
3. **Meeting templates (meeting-agenda.md)** — adopted the 6 templates as standing practice; Sprint 2 opens with sprint planning on 2026-09-15 using template 1.
4. **Finished-milestone log (feature-tracking.md § ✅ Shipped)** — reviewed the closed plans (Loop-CRM finance integration, demo state, Twenty/Postiz research, AI hub/locale/connectors, POS launch scope, unified Precis). Confirmed: no dangling links to deleted plan files.
5. **Anytype concepts (anytype-extensibility.md + CONTENT_MODEL § 2)** — shared vocabulary: Objects/Types/Properties/Views/Queries/Collections; the assignment matrix (Owner → Assigned To → Reviewer) and the 9 property formats in `_relations.md`.
6. **Owner assignment (task-tracking.md)** — initial executors assigned to all Sprint 2 tasks from the people roster (see below); feature-owner decisions for the 3 P0 Syntara features stay with Product during the sprint.

**Decisions made:**
- The agenda content model is adopted as the **team-wide working contract** from this meeting forward.
- The plans → milestones reference contract is binding: no plan closeout without a ✅ milestone entry, a team-notes decision record, and reference updates.
- Sprint 2 is confirmed as defined (goal + 11 tasks, window 2026-09-15 → 09-28); executors assigned at this meeting may be adjusted at sprint planning.
- Sales-pipeline ownership defaults to the Founder until a dedicated sales owner exists (roster currently has none).

**Action items:**
- [x] Hold the first agenda meeting — Done (this entry)
- [x] Record initial Sprint 2 executors in task-tracking.md — Done (2026-09-10)
- [ ] @moustafa — Run sprint planning for Sprint 2 with template 1 (capacity check + commitment) — due 2026-09-15
- [ ] @moustafa — Assign feature owners to the 3 P0 Syntara features — due 2026-09-22
- [ ] @mahmoud — Run the documentation validation and link check across the agenda — due 2026-09-19
- [ ] @mahmoud — Configure Loop-CRM live OAuth credentials + publish E2E (deploy-gated) — due 2026-09-26
- [ ] @mahmoud — Verify demo-state server half on the deployed stack — due 2026-09-26
- [ ] @asmaa — Review all 8 case studies for completeness (Context → Lessons) — due 2026-09-18
- [ ] @yahia — Confirm every ✅ Shipped feature entry links its case study — due 2026-09-19
- [ ] @mahmoud — Seed sales pipeline: owners + convert-pilot plan for the 3 restaurant rows — due 2026-09-22
- [ ] @moustafa — Backlog refinement: schedule the 11 remaining rows → Sprint 3 or Parked — due 2026-09-24

**Blockers / Risks:**
- Loop-CRM verification tasks (@mahmoud) need the deployed `crm.structa.cloud` stack + provider secrets — if the deploy slips these become Sprint 3 carry-overs.
- No dedicated sales/marketing person on the roster; pipeline execution capacity is a single-person risk on the Founder.
- @dariia has no Sprint 2 assignment (contributor role) — product to propose content-work tasks at sprint planning.

**Links:**
- Related definition: [`CONTENT_MODEL.md`](./CONTENT_MODEL.md) § 5 (this meeting's source agenda)
- Related task board: [`task-tracking.md`](./task-tracking.md) § Sprint 2
- Related roster: [`.mono-repo/objects/people/`](./.mono-repo/objects/people/)
- Meeting folder: <https://drive.google.com/drive/folders/1-A0MxVvAUpaOc56Nr9t2672DkrvgILb0>

---

### 2026-09-10 — Sprint Planning — Sprint 2 Defined (2026-09-15 → 09-28)

**Attendees:** Workspace team (agent session, planning pass)

**Topic / Agenda:** Define Sprint 2 using the sprint-planning template:
carry open Sprint 1.5 items forward, pull prioritized backlog rows, and commit
the sprint goal.

**Key points:**
- Sprint 1.5 closed at 36/41 (88%); its 5 open rows were carried into Sprint 2
  with updated due dates rather than dropped.
- Sprint 2 mixes three kinds of work: agenda open loops (meeting, validation,
  case-study review), deploy-gated Loop-CRM verifications (OAuth credentials +
  demo-state server half), and first sales-pipeline actions (pilot conversion
  plan, P0 owner assignments).
- Backlog pruned from 15 to 11 rows: the promoted rows left, conditional
  case-study rows re-baselined to their triggering events, and the Arabic
  case-studies row flagged for a policy decision first (they are EN-only by
  design — see INDEX.md).
- Sprint 3 seed pre-marked: goal definition at the Sprint 2 review (2026-09-28).

**Decisions made:**
- Sprint 2 window: **2026-09-15 → 2026-09-28**
- Sprint 2 goal: close the agenda's open loops (kickoff meeting, docs
  validation, Loop-CRM deploy-gated verifications) while seeding the sales
  pipeline for the Formint Professional launch.
- 11 tasks committed (4× P0, 6× P1, 1× P2); backlog refined in the same pass.

**Action items:**
- [x] Hold the first agenda meeting — Done (2026-09-10, held early; see Kickoff Meeting entry above)
- [ ] @mahmoud — Configure Loop-CRM live OAuth credentials + publish E2E — due 2026-09-26
- [ ] @mahmoud — Verify demo-state server half on deployed stack — due 2026-09-26
- [ ] @mahmoud — Seed sales pipeline owners + pilot conversion plan — due 2026-09-22
- [x] Define Sprint 2 goal and seed tasks — Done (2026-09-10)

**Blockers / Risks:**
- Loop-CRM verification tasks are deploy-gated: they need the live
  `crm.structa.cloud` stack + provider secrets; if the deploy slips, these
  become the first Sprint 3 carry-over candidates.
- All Sprint 2 tasks lack assignees — owner assignment is itself a committed
  task; until then every row is unowned.

**Links:**
- Related task board: [`task-tracking.md`](./task-tracking.md) § Sprint 2
- Related backlog: [`task-tracking.md`](./task-tracking.md) § Backlog
- Related template: [`meeting-agenda.md`](./meeting-agenda.md) § Sprint Planning
- Related pipeline: [`sales-pipeline.md`](./sales-pipeline.md) § 2 Targets

---

### 2026-08-31 — Project Kickoff — Agenda System Setup

**Attendees:** Workspace team

**Topic / Agenda:** Setting up the project agenda tracking system — feature tracking, case studies, task tracking, team notes, completion checklist, and meeting templates.

**Key points:**
- Anytype documentation was reviewed as a reference for object-based knowledge management
- Anytype uses Objects, Types, Properties, and Links as its core model — analogous to how we track Features, Tasks, and Decisions
- The agenda system mirrors this: Features are Types, Tasks are Objects with Properties (status, assignee, due), and links connect everything
- Mermaid diagrams are the standard for architecture documentation in case studies
- Docus frontmatter with object/attributes/tags/links is the canonical format for all docs

**Decisions made:**
- Agenda system files live in `docs/agenda/` with a MAIN.md hub
- Feature tracking mirrors the priority roadmap in `features/feature-roadmap.md`
- Every shipped feature should have a case study with at least one mermaid diagram
- Task tracking is sprint-based and maps to features
- Team notes capture decisions that affect multiple files

**Action items:**
- [x] Create `docs/agenda/MAIN.md` — hub/index — Done
- [x] Create `docs/agenda/feature-tracking.md` — feature lifecycle tracking — Done
- [x] Create `docs/agenda/case-studies.md` — case study template with mermaid — Done
- [x] Create `docs/agenda/task-tracking.md` — sprint task board — Done
- [x] Create `docs/agenda/team-notes.md` — meeting notes and decisions — Done
- [ ] Create `docs/agenda/meeting-agenda.md` — meeting templates — Pending
- [ ] Create `docs/agenda/completion-checklist.md` — project closeout checklist — Pending
- [ ] Add initial active features to feature-tracking.md — Pending
- [ ] Add initial sprint tasks to task-tracking.md — Pending

**Blockers / Risks:**
- None at this stage — system is being stood up

**Links:**
- Related plan: [`plans/README.md`](../plans/README.md)
- Related roadmap: [`features/feature-roadmap.md`](../features/feature-roadmap.md)
- Anytype docs reference: [Objects](https://doc.anytype.io/anytype/create/objects), [Types](https://doc.anytype.io/anytype/organize/types), [Properties](https://doc.anytype.io/anytype/organize/properties)

### 2026-09-05 — Agenda System — Content Model Definition & First Meeting

**Attendees:** Workspace team (agent session)

**Topic / Agenda:** Define the agenda content system — what content lives where, how objects map to markdown files, and how every reference routes through plans and milestones. This definition is the team-wide reference and the kickoff agenda for the first meeting.

**Key points:**
- Researched the current Anytype model (doc.anytype.io: Objects, Types, Properties, Views, Queries, Collections) and mapped it conceptually onto the agenda markdown files + frontmatter.
- The agenda splits into four packages: A — team delivery & memory (`docs/agenda/`), B — Anytype import set (`docs/agenda/.mono-repo/`), C — canonical engineering plans (`docs/plans/`), D — product docs & guides.
- The reference contract: forward links from work → plans (`docs/plans/`), backward links from finished plans → ✅ Shipped milestones in the agenda. Finished plans are deleted (git history = archive) and recorded as milestones — never left as dangling links.
- First meeting folder (Google Drive) referenced from `CONTENT_MODEL.md` § 5.

**Decisions made:**
- `docs/agenda/CONTENT_MODEL.md` is the canonical definition; indexes (`README.md`, `MAIN.md`, `INDEX.md`) link to it instead of restating the rules.
- The ✅ Shipped milestone log (`feature-tracking.md`) is the backward map for all completed plans.
- One object type per home directory; no duplicate content across packages; schema changes land in `.mono-repo/objects/` first.

**Action items:**
- [x] Create `CONTENT_MODEL.md` (glossary, packaging, reference contract) — Done (2026-09-05)
- [x] Update agenda indexes (README/MAIN/INDEX) to reference the content model — Done (2026-09-05)
- [ ] Hold the first meeting using the `CONTENT_MODEL.md` § 5 kickoff agenda and the Drive folder — Pending
- [ ] Adopt the plans → milestones reference contract for all future plan closeouts — Pending (rule is now documented)

**Blockers / Risks:**
- None; the content model is a definition, not a migration. Package B (`.mono-repo/`) is already largely consistent with it.

**Links:**
- Related definition: [`CONTENT_MODEL.md`](./CONTENT_MODEL.md)
- Related hub: [`MAIN.md`](./MAIN.md)
- Related research: [`anytype-extensibility.md`](./anytype-extensibility.md)
- First meeting folder: <https://drive.google.com/drive/folders/1-A0MxVvAUpaOc56Nr9t2672DkrvgILb0>

---

### 2026-09-05 — Agenda — De-dup, Content Update & Diagram Package (Rendered Images)

**Attendees:** Workspace team (agent session)

**Topic / Agenda:** Clean the agenda: remove duplicated content, update stale
content, fix dangling references, and add a diagram package with **rendered
images** (API request UML, Django/Rust ERDs, Blinko SurrealDB) so diagrams are
viewable outside Docus (GitHub, Anytype import, Drive).

**Key points:**
- **De-duplicated:** `SUMMARY.md` slimmed to a change log (was duplicating
  README/MAIN tables + Anytype glossary); `INDEX.md` tail section removed;
  `case-studies.md` "Existing Case Studies" summaries replaced with a pointer
  to `case-studies/INDEX.md` (canonical index).
- **Gaps fixed:** dangling image refs in `.mono-repo/plans/business-model.md`
  (Business Model Canvas) and `.mono-repo/tasks/timeline.md` replaced with real
  rendered mermaid diagrams.
- **Diagram package created:** `docs/agenda/diagrams/` — README index +
  `api-request-flows.md` (6 request/response sequences with auth + tenant
  rules), `django-loop-crm-er.md` (all Loop-CRM apps ERD), `rust-sqlite-er.md`
  (Formint Community Diesel schema + relations + module map),
  `blinko-surrealdb.md` (Blinko + SurrealDB topology + M1–M4 migration).
- **Rendering pipeline:** `docs/scripts/render-agenda-diagrams.mjs` renders every
  `mermaid` block under `docs/agenda/` to SVG via mermaid.ink (base64url),
  writes to `docs/public/agenda/diagrams/`, and inserts `![Rendered diagram]`
  lines. 59 SVGs rendered; case-study diagrams included.
- **Bug found in existing docs:** the `UUID pk` erDiagram attribute and
  `Note over X,Y` state-diagram syntax render as 400 on mermaid.ink's parser —
  adjusted the two affected blocks to portable syntax.

**Decisions made:**
- Rendered images are **derived assets** — the mermaid block in the source doc
  is canonical; re-run the render script after editing a diagram.
- Diagram assets live in `docs/public/agenda/diagrams/` (served at
  `/agenda/diagrams/...`); sources stay next to the content that uses them.
- The diagrams package is **A.1** in the CONTENT_MODEL package split (sub-
  package of A — team delivery & memory).

**Action items:**
- [x] De-duplicate agenda top-level docs (SUMMARY, INDEX, case-studies.md) — Done (2026-09-05)
- [x] Fix dangling mono-repo image refs with rendered diagrams — Done (2026-09-05)
- [x] Create diagrams package (README + 4 diagram docs) — Done (2026-09-05)
- [x] Render 59 SVGs + insert image references — Done (2026-09-05)
- [x] Wire diagrams into agenda indexes + CONTENT_MODEL package table — Done (2026-09-05)
- [ ] Re-render diagrams whenever a mermaid source changes (documented in diagrams/README.md) — Ongoing

**Blockers / Risks:**
- mermaid.ink is a public render service with rate limits; the script retries
  and serializes requests. For offline/CI rendering, a local mermaid-cli
  (puppeteer) would be the replacement.

**Links:**
- Related package: [`diagrams/README.md`](./diagrams/README.md)
- Related render script: [`docs/scripts/render-agenda-diagrams.mjs`](../scripts/render-agenda-diagrams.mjs)
- Related index: [`case-studies/INDEX.md`](./case-studies/INDEX.md)

---

### 2026-09-05 — Agenda — Object Types & Objects Separation (Anytype Schema)

**Attendees:** Workspace team (agent session)

**Topic / Agenda:** Add the missing Anytype object types and objects to the
`.mono-repo/` knowledge graph, separate them into per-type directories with
content related to the actual projects and repository, and complete all prompts
recorded in `.mono-repo/_prompts.md`.

**Key points:**
- **15 new object type definitions** added to `.mono-repo/objects/` (architecture,
  guide, reference, changelog, diagram, project, report, dashboard,
  data-pipeline, methodology, insight, recommendation, repository, module,
  documentation) — each with description, relations, and related links, matching
  the established `feature.md`/`tool.md`/`product.md` format.
- **20 new type directories** created under `.mono-repo/`, each with a `_index.md`
  and content objects tied to real repo entities: `projects/` (loop-crm-merge,
  ctc, formint-editions-chain, django-fusion, docs-agenda-system), `editions/`
  (all 5 Formint editions + precis-unified), `sprints/`, `releases/`,
  `integrations/` (stripe, social, email-oauth, pos-ingest), `apis/`,
  `components/`, `tools/` (tauri, blinko, surrealdb, postgres-redis, docus),
  `pipelines/`, `styles/`, `diagrams/`, `reports/`, `dashboards/`,
  `data-pipelines/`, `methodologies/`, `insights/`, `recommendations/`,
  `repositories/`, `modules/`, `documentation/` — 87 new files total.
- **Prompts completed:** every workflow in `_prompts.md` marked ✅ Completed with
  pointers to where each landed (object types, features, install guides, graph
  integrity, relations update, channel setup).
- **Relations extended:** `objects/_relations.md` now covers the new
  data-analysis (Report/Dashboard/DataPipeline/Methodology/Insight/
  Recommendation) and monorepo (Repository/Module/Documentation/Project) types.

**Decisions made:**
- New files use the mono-repo's established Anytype-style frontmatter
  (`Object type:`/`Tags:`/`Status:`) — the Docus validator flags these exactly
  like the 133 pre-existing mono-repo files already at baseline; no pre-existing
  file regressed.
- Directory-per-type separation mirrors Anytype's object model: each content
  object lives under its type's home directory and links across types via
  relations.

**Action items:**
- [x] Define all missing object types in `objects/` — Done (2026-09-05)
- [x] Create per-type directories with repo-tied content — Done (2026-09-05)
- [x] Complete all `_prompts.md` workflows — Done (2026-09-05)
- [x] Update indexes (mono-repo README, objects/_index, CONTENT_MODEL package B) — Done (2026-09-05)
- [ ] Extend the graph with more real objects as projects evolve (reports,
  sprints, releases) — Ongoing

**Blockers / Risks:**
- Content objects reference the repo as of 2026-09-05; sprint/release details
  will drift and should be re-synced at each sprint boundary.

**Links:**
- Related ledger: [`.mono-repo/_prompts.md`](./.mono-repo/_prompts.md)
- Related object types: [`.mono-repo/objects/_index.md`](./.mono-repo/objects/_index.md)
- Related relations: [`.mono-repo/objects/_relations.md`](./.mono-repo/objects/_relations.md)

---

### 2026-09-05 — Loop-CRM — Finished Plans Closed as Milestones

**Attendees:** Workspace team (agent session)

**Topic / Agenda:** Close out the completed Loop-CRM plans — delete the finished plan files from `docs/plans/loop-crm/` and record them as finished milestones in the agenda system.

**Key points:**
- `formint-integration-finance-workflows.md` was fully complete (all steps `[x]`): POS finance ingestion, workflow action/template expansion, webhooks/email/Slack/social/export connectors.
- `demo-state-gap-fixing.md` was complete except the server-half deploy verification of Task 6 (local half verified).
- `twenty-postiz-comparison.md` was a supporting research doc (no task steps) that shipped alongside the demo-state work.
- `wagtail-landing-plan.md` and `merge-plan.md` stay active — they still carry open work (Phases 5/7/8, adapters, AI hub).

**Decisions made:**
- Delete the three finished plan files; git history is the archive (per `docs/plans/document-lifecycle.md`).
- Record each as a ✅ Shipped milestone in `docs/agenda/feature-tracking.md` § Loop-CRM.
- Update the plans registry (`docs/plans/README.md`), the Loop-CRM plan index, `docs/REFERENCE.md`, `docs/ar-content/REFERENCE.md`, and the product audit to point at the milestone records instead of the deleted files.

**Action items:**
- [x] Delete `demo-state-gap-fixing.md`, `formint-integration-finance-workflows.md`, `twenty-postiz-comparison.md` — Done (2026-09-05)
- [x] Add Loop-CRM ✅ Shipped milestones to feature-tracking.md — Done (2026-09-05)
- [x] Add milestone tasks to task-tracking.md § Sprint 2 — Done (2026-09-05)
- [ ] Server-half demo-state verification on the deployed stack — Pending (real deploy required)

**Blockers / Risks:**
- None; the remaining demo-state item is a deploy-gated verification, not code work.

**Links:**
- Related feature tracking: [`feature-tracking.md`](./feature-tracking.md) § Loop-CRM
- Related task board: [`task-tracking.md`](./task-tracking.md) § Sprint 2
- Related plans index: [`plans/loop-crm/README.md`](../plans/loop-crm/README.md)

---

### 2026-09-03 — Infrastructure & Docs Workstreams — Worker Assets, Coder Deploy, Shared Assets, Anytype Research

**Attendees:** Workspace team (agent session)

**Topic / Agenda:** Four approved workstreams: (1) minimize assets data in scheduler/worker containers, (2) verify + redeploy Coder, (3) audit shared assets dir between precis-ctc and precis-main with fallback, (4) research anytype.io and record agenda/project-separation extensibility.

**Key points:**
- Background workers and schedulers were mounted with the entire shared assets tree, even where the task never touches media — more data in more containers than the work requires
- The Docker host had no Postgres, Redis, or workspace runtime up; the Precis scheduler had crashed at boot waiting on Redis
- A research-site media default pointed at a stray local rendition tree (≈380 KB) while the build, docs, and changelog all treated the shared tree (≈139 MB) as canonical
- The shared-media contract check still asserted a retired proxy topology while the live contract had moved to the assets proxy
- Anytype was reviewed: objects, types, properties, and relations, queries vs. collections, and per-space type isolation are the transferable concepts

**Decisions made:**
- Workers and schedulers stay minimal: no media data except where a task genuinely writes media (the research worker keeps its mount; the scheduler never needs one)
- The research-site local default should match the canonical shared media tree; containers override it by environment variable
- The shared-assets contract (per-site static files plus per-host fallback to shared roots) is the accepted contract, and its check now asserts the live topology
- Anytype findings are recorded as a proposal, not an integration commitment

**Action items:**
- [x] Remove media mounts from the shared workers/scheduler and the research scheduler — Done (2026-09-03)
- [x] Bring up Postgres, Redis, and the workspace runtime; restart the Precis scheduler — Done (2026-09-03)
- [x] Align the research-site media default and re-run the configuration check — Done (2026-09-03)
- [x] Update the shared-media contract check to the live assets-proxy topology — Done (2026-09-03)
- [x] Publish the Anytype extensibility proposal — Done (2026-09-03)
- [ ] Review the Anytype proposal items (templates, then relation lint) and schedule them into a sprint — Pending

**Blockers / Risks:**
- None blocking; the stray ≈380 KB rendition tree is leftover runtime data from the old default — safe to leave (ignored by version control) or delete after confirmation

**Links:**
- Related proposal: [`anytype-extensibility.md`](./anytype-extensibility.md)
- Related task board: [`task-tracking.md`](./task-tracking.md) § Sprint 2 (2026-09-03 rows)

---

### 2026-09-06 — Loop-CRM + Agenda — Implementation Reconciliation, Component Audit & Model ERDs

**Attendees:** Workspace team (agent session)

**Topic / Agenda:** Close the loop on the un-recorded Loop-CRM AI-hub work, reconcile what is actually implemented (backend × frontend) per product, audit frontend components for placeholders, and stand up the model-ERD (graph_models) docs for Loop-CRM.

**Key points:**
- The 2026-09-05 Loop-CRM work (AI hub, en/ar language, Google/Meta/TikTok/Reddit connectors, people and search surfaces) was never recorded in the agenda — added as a ✅ Shipped milestone under `feature-tracking.md` § Loop-CRM.
- The engineering plans now carry an **implementation-status truth table** (backend × front end per product) and a "couldn't add" register; Loop-CRM's remaining items are operational gates (live provider credentials, realtime hardening, demo-state server verification), not feature work.
- Component audit: Loop-CRM surfaces are all real-data with explicit empty and pending states; genuine findings are the research site's demo blog templates, the Precis LMS "coming soon" tagline, and Formint Pro's "Add … coming soon" stub toasts.
- Loop-CRM now follows the repo's ERD convention and publishes per-app model diagrams for **crm (sales)** and **marketing**.

**Decisions made:**
- Diagram image outputs stay derived, ignored artifacts; the committed contract is the per-project diagram index.
- The component audit is a report, not a plan — findings move into sprint backlog tasks rather than new plan files.

**Action items:**
- [x] Record the Loop-CRM AI hub / language / connector milestone — Done (2026-09-06)
- [x] Reconcile implementation status per product — Done (2026-09-06)
- [x] Publish the front-end component audit — Done (2026-09-06)
- [x] Add Loop-CRM model-diagram tooling and its index — Done (2026-09-06)
- [ ] Configure live provider credentials and run publishing/consent end-to-end on the deployed stack — Pending (deploy-gated)
- [x] Implement the Formint Pro create forms that sat behind the "coming soon" toasts — Done (2026-09-06; suppliers, HR roles/schedules/payroll, admin notes, recipes and ingredients now create and edit against the real server)
- [x] Verify Formint Pro modals end to end (2026-09-06) — table columns now resolve the related names they display instead of showing stale bindings; the client checks passed clean with no errors or warnings. The server suite is host-Docker-only in this sandbox (see the audit doc § 2.3).
- [x] Finish the remaining list pages and the operations/shifts create-edit flow (2026-09-10) — products, inventory, and transactions gained delete confirmation and real related-name resolution; contacts, deals, activities, and notes resolve company/contact/stage/deal names and send the correct identifiers. Shifts were repaired, a unique open shift is enforced on both sides before the database constraint, and expected cash is computed as opening float plus in-window cash sales. Previously broken contact-relation reads (every CRM list request failed) were fixed, CRM write paths and shift create/close/detail were added, and the server persist checks were extended. Client checks green (93/93); the server suite remains host-Docker-only (see the audit doc § 2.3).

**Blockers / Risks:**
- The diagramming tool was not pre-installed in the working environment — installed on request (2026-09-06) and diagrams were rendered for Loop-CRM and regenerated for Precis and Syntara (models unchanged, so tracked sources were left untouched to avoid pure churn). The Formint cloud diagrams cannot be re-rendered here because their optional package is not present; run the project's diagram target in its backend image.

**Links:**
- Related feature tracking: [`feature-tracking.md`](./feature-tracking.md) § Loop-CRM — AI Hub, locale & connectors
- Related component audit: [`../audit/frontend-components-2026-09-06.md`](../audit/frontend-components-2026-09-06.md)
- Related task board: [`task-tracking.md`](./task-tracking.md) § Sprint 2 + Backlog

---

## ✍️ Adding New Notes

When you have a meeting or make a significant decision:

1. **Copy the entry format** above
2. **Date it** with the meeting date
3. **Categorize** — Meeting type (Sprint Planning, Standup, Review, Retro, Decision, Incident)
4. **Link out** — Reference the relevant feature, task, or plan
5. **Note action items** with assignees and due dates
6. **Note blockers** with owners

---

## 🔍 Searching Notes

| What you're looking for | Search in |
|------------------------|-----------|
| A decision about feature X | `rg "Feature Name" docs/agenda/team-notes.md` |
| Who was assigned task Y | `rg "Task title" docs/agenda/team-notes.md` |
| When a blocker was raised | `rg "Blocked" docs/agenda/team-notes.md` |
| What was decided in sprint N | `rg "Sprint N" docs/agenda/team-notes.md` |

---

## 🔗 Related

| Topic | Path |
|-------|------|
| Meeting agenda templates | [./meeting-agenda.md](./meeting-agenda.md) |
| Feature tracking (decisions affect features) | [./feature-tracking.md](./feature-tracking.md) |
| Task tracking (decisions affect tasks) | [./task-tracking.md](./task-tracking.md) |
| Plans registry (major decisions become plans) | [`../plans/README.md`](../plans/README.md) |

---

## 🔄 Maintenance

- **Add notes after:** Every meeting, every significant decision, every incident
- **Update notes when:** Action items complete, blockers resolve, decisions change
- **Reference in PRs:** Link to the relevant note when a PR implements a decision
- **Archive old notes:** When a project closes, move notes to an archive section or file

---

## Remarks & Notes

- Team notes are not a replacement for detailed plans — they're the decision log
- If a decision affects multiple files, write it here AND update a plan
- Action items without owners and due dates are just wishes — always assign them
- The note format is intentionally lightweight — don't over-engineer it

<!-- AI-generated: review needed -->
