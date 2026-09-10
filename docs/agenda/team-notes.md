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
- Related feature: [`feature-tracking.md`](../feature-tracking.md) § Feature Name
- Related task: [`task-tracking.md`](../task-tracking.md) § Task Title
- Related plan: [`plans/path.md`](../plans/path.md)
- Meeting agenda: [`meeting-agenda.md`](../meeting-agenda.md)
```

---

## 🗓️ Meeting Notes Log

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
- The agenda splits into four packages: A — team delivery & memory (`docs/agenda/`), B — Anytype import set (`docs/agenda/mono-repo/`), C — canonical engineering plans (`docs/plans/`), D — product docs & guides.
- The reference contract: forward links from work → plans (`docs/plans/`), backward links from finished plans → ✅ Shipped milestones in the agenda. Finished plans are deleted (git history = archive) and recorded as milestones — never left as dangling links.
- First meeting folder (Google Drive) referenced from `CONTENT_MODEL.md` § 5.

**Decisions made:**
- `docs/agenda/CONTENT_MODEL.md` is the canonical definition; indexes (`README.md`, `MAIN.md`, `INDEX.md`) link to it instead of restating the rules.
- The ✅ Shipped milestone log (`feature-tracking.md`) is the backward map for all completed plans.
- One object type per home directory; no duplicate content across packages; schema changes land in `mono-repo/objects/` first.

**Action items:**
- [x] Create `CONTENT_MODEL.md` (glossary, packaging, reference contract) — Done (2026-09-05)
- [x] Update agenda indexes (README/MAIN/INDEX) to reference the content model — Done (2026-09-05)
- [ ] Hold the first meeting using the `CONTENT_MODEL.md` § 5 kickoff agenda and the Drive folder — Pending
- [ ] Adopt the plans → milestones reference contract for all future plan closeouts — Pending (rule is now documented)

**Blockers / Risks:**
- None; the content model is a definition, not a migration. Package B (`mono-repo/`) is already largely consistent with it.

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
- **Gaps fixed:** dangling image refs in `mono-repo/plans/business-model.md`
  (Business Model Canvas) and `mono-repo/tasks/timeline.md` replaced with real
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
`mono-repo/` knowledge graph, separate them into per-type directories with
content related to the actual projects and repository, and complete all prompts
recorded in `mono-repo/_prompts.md`.

**Key points:**
- **15 new object type definitions** added to `mono-repo/objects/` (architecture,
  guide, reference, changelog, diagram, project, report, dashboard,
  data-pipeline, methodology, insight, recommendation, repository, module,
  documentation) — each with description, relations, and related links, matching
  the established `feature.md`/`tool.md`/`product.md` format.
- **20 new type directories** created under `mono-repo/`, each with a `_index.md`
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
- Related ledger: [`mono-repo/_prompts.md`](./mono-repo/_prompts.md)
- Related object types: [`mono-repo/objects/_index.md`](./mono-repo/objects/_index.md)
- Related relations: [`mono-repo/objects/_relations.md`](./mono-repo/objects/_relations.md)

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
- Shared tasks stack (`projects/docker-compose.tasks.yml`) bind-mounted the whole monorepo `projects/assets` tree into worker+scheduler; CTC tools compose mounted the media tree into scheduler+worker even though only the worker needs it
- Docker host had no Postgres/Redis/Coder running; Precis scheduler had crashed at boot waiting on Redis
- CTC settings `MEDIA_ROOT` default resolved to a stray precis-local rendition tree (`projects/precis/assets/media/ctc-research`, 380K) while compose, docstring, and CHANGELOG all cite the monorepo tree (`projects/assets/media/ctc-research`, 139M) as canonical
- `tests/test_shared_media.py` still asserted the retired `application/proxy` shared-proxy topology; the live contract is `assets-proxy` in `application/tools`
- Anytype (anytype-ts repo + doc.anytype.io) reviewed: objects/types/properties/relations + Queries vs Collections + per-space type isolation are the transferable concepts

**Decisions made:**
- Worker/scheduler containers should stay minimal: no assets/media data except where a task genuinely writes media (CTC worker keeps its mount; scheduler never needs it)
- CTC local-dev `MEDIA_ROOT` default should match the canonical monorepo shared tree; containers override via env var
- The shared-assets contract (per-site staticfiles + per-host nginx fallback to shared roots) is validated by the rewritten `tests/test_shared_media.py`
- Anytype findings recorded as a proposal doc, not an integration commitment

**Action items:**
- [x] Remove assets/media binds from shared worker/scheduler + CTC scheduler — Done (2026-09-03)
- [x] Deploy Postgres/Redis + Coder; restart Precis scheduler — Done (2026-09-03)
- [x] Fix CTC MEDIA_ROOT default; run manage.py check — Done (2026-09-03)
- [x] Rewrite tests/test_shared_media.py to assets-proxy topology — Done (26/26 pass, 2026-09-03)
- [x] Write docs/agenda/anytype-extensibility.md proposal — Done (2026-09-03)
- [ ] Review Anytype proposal items (#3 templates, #4 relation lint first) and schedule into a sprint — Pending

**Blockers / Risks:**
- None blocking; stray 380K rendition tree at `projects/precis/assets/media/ctc-research` is leftover runtime data from the old default — safe to leave (gitignored) or delete after confirmation

**Links:**
- Related proposal: [`anytype-extensibility.md`](./anytype-extensibility.md)
- Related task board: [`task-tracking.md`](./task-tracking.md) § Sprint 2 (2026-09-03 rows)
- Related test: [`tests/test_shared_media.py`](../../tests/test_shared_media.py)

---

### 2026-09-06 — Loop-CRM + Agenda — Implementation Reconciliation, Component Audit & Model ERDs

**Attendees:** Workspace team (agent session)

**Topic / Agenda:** Close the loop on the un-recorded Loop-CRM AI-hub work, reconcile what is actually implemented (backend × frontend) per product, audit frontend components for placeholders, and stand up the model-ERD (graph_models) docs for Loop-CRM.

**Key points:**
- The 2026-09-05 Loop-CRM commit (AI hub, en/ar locale, Google/Meta/TikTok/Reddit connectors, people/search islands) was never recorded in the agenda — added as a ✅ Shipped milestone under `feature-tracking.md` § Loop-CRM.
- dev-team-plans.md now carries an **implementation-status truth table** (backend × frontend per product) and a "couldn't add" register; Loop-CRM's remaining items are operational gates (live provider credentials, realtime hardening, demo-state server verify), not feature code.
- Component audit (`docs/audit/frontend-components-2026-09-06.md`): Loop-CRM app islands are all real-data with explicit empty/pending states; genuine findings are CTC lorem blog-demo templates, the precis-main `brand.ts` "coming soon" tagline, and Formint Pro "Add … coming soon" stub toasts.
- Loop-CRM backend now follows the repo ERD convention (`django_extensions` + `make erd`/`erd-all` + `docs/erd/README.md`), generating per-app model graphs incl. **crm (sales)** and **marketing**.

**Decisions made:**
- PNG ERD outputs stay gitignored derived assets (repo convention); the per-project `docs/erd/README.md` tables are the committed contract.
- The component audit is a report, not a plan — findings move into sprint backlog tasks (task-tracking.md Backlog) rather than new plan files.

**Action items:**
- [x] Record Loop-CRM AI-hub/locale/connectors milestone — Done (2026-09-06)
- [x] Reconcile implementation status per product in dev-team-plans.md — Done (2026-09-06)
- [x] Publish frontend component audit — Done (2026-09-06)
- [x] Add Loop-CRM ERD tooling + docs/erd README — Done (2026-09-06)
- [ ] Configure live OAuth credentials and run publish/consent E2E on the deployed stack — Pending (deploy-gated)
- [x] Implement Formint Pro create-forms behind the "coming soon" toasts — Done (2026-09-06; suppliers, HR roles/schedules/payroll, admin notes, recipes + ingredients — create/edit modals wired to the Django server API; see [`../audit/frontend-components-2026-09-06.md`](../audit/frontend-components-2026-09-06.md) § 2.3)
- [x] Verify Formint Pro modals end-to-end (2026-09-06) — removed stale `item.*_name` table bindings in favor of `empName()`/`prodName()` FK resolution; added `create-forms.contract.test.ts` (payload/endpoint/method contracts); `vitest run` **86/86** passed across 8 files and `astro check` reports **0 errors / 0 warnings**. Backend suite cannot run in this sandbox: the server lockfile requires `libs/django-bolt`, which is not in this checkout — run `make test` inside the Formint Pro Docker image on the host (see audit doc § 2.3).
- [x] Finish remaining list pages + ops/shifts create/edit flow (2026-09-10) — pos/products, pos/inventory, pos/transactions delete-confirm + FK-name resolution (`catName`/`prodName`/`custName`); crm/contacts, crm/deals, crm/activities, crm/notes resolve company/contact/stage/deal names from fetched reference lists and their modals now send `company_id`/`contact_id`/`pipeline_id`/`stage_id`/`deal_id`; ops/shifts script repaired (broken `openEdit` block), unique-open-shift enforced client+server (409 before the DB partial constraint) and expected cash auto-computed as opening float + in-window cash sales. Backend: fixed the broken `models.crm_models` imports (every `/crm/*` GET 500'd), added CRM write views + shift create/close/detail URLs, and extended the server persist suite with four shift tests. `vitest run` **93/93** (8 files), `astro check` **0/0** (105 pre-existing hints); backend suite remains host-Docker-only (`py_compile` clean; see audit doc § 2.3 second follow-up).

**Blockers / Risks:**
- `graphviz` was not pre-installed in the agent sandbox — installed on request (2026-09-06) and PNGs rendered for Loop-CRM + regenerated for precis-main/precis-ctc/syntara (models unchanged — tracked `.dot` files were left at HEAD to avoid pure churn). Formint-cloud's ERD cannot re-render here because its optional `django_bolt` package is not in the sandbox venv (run `make erd` in its backend Docker image).

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
