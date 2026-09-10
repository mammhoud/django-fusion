# 📋 Project Agenda System — Summary

> Complete team tracking system in `docs/agenda/`, built 2026-08-31, extended
> 2026-09-05 with the content model definition and the plans → milestones
> reference contract. Inspired by Anytype's object-based knowledge model.

---

## What this directory is

The agenda is the team's delivery + memory layer:

| What | Where |
|------|-------|
| **Definition** (packages, glossary, reference contract) | [`CONTENT_MODEL.md`](./CONTENT_MODEL.md) — read first |
| **Overview + quick start** | [`README.md`](./README.md) |
| **Hub / how everything connects** | [`MAIN.md`](./MAIN.md) |
| **Feature lifecycle** | [`feature-tracking.md`](./feature-tracking.md) |
| **Case studies with diagrams** | [`case-studies.md`](./case-studies.md) + [`case-studies/`](./case-studies/INDEX.md) |
| **Rendered diagrams** (API UML, ERDs, Blinko) | [`diagrams/README.md`](./diagrams/README.md) — SVGs in `docs/public/agenda/diagrams/` |
| **Anytype object graph** (types + per-type content) | [`mono-repo/README.md`](./mono-repo/README.md) — object types, 20 content dirs, prompt ledger |
| **Sprint tasks** | [`task-tracking.md`](./task-tracking.md) |
| **Team notes / decisions** | [`team-notes.md`](./team-notes.md) |
| **Meeting templates** | [`meeting-agenda.md`](./meeting-agenda.md) |
| **Closeout checklist** | [`completion-checklist.md`](./completion-checklist.md) |
| **Legacy Blinko-style team index** | [`INDEX.md`](./INDEX.md) |

## Change log

- **2026-09-10 (5)** — **Kickoff meeting held and recorded.** The first team
  meeting on the agenda system ran through the CONTENT_MODEL § 5 agenda
  (content model → star-schema hub → meeting templates → milestone log →
  Anytype concepts → owner assignment) with the full roster
  (mammhoud/moustafa/mahmoud/asmaa/yahia/dariia). Outcomes: content model
  adopted as the team-wide working contract; plans → milestones rule binding;
  Sprint 2 confirmed as defined; executors assigned to all 11 Sprint 2 tasks
  from the people roster (mahmoud 4, moustafa 3, mammhoud 2, asmaa 1,
  yahia 1); sales-pipeline ownership defaults to the Founder until a dedicated
  sales owner exists. Recorded per the team-notes template; kickoff task
  closed on the board.

- **2026-09-10 (4)** — **Sprint 2 defined and seeded.** Sprint 1.5 formally
  closed (36/41, 88%); its 5 open rows carried into Sprint 2 with updated due
  dates. Sprint 2 (2026-09-15 → 09-28) commits 11 tasks — 5 carried, 4 pulled
  from backlog (incl. the deploy-gated Loop-CRM OAuth + demo-state
  verifications), 2 new (docs validation, backlog refinement) — with a
  bilingual goal focused on closing open loops and seeding the sales pipeline
  for the Formint Professional launch. Backlog pruned 15 → 11 rows
  (conditionals re-baselined to trigger events); Sprint 3 seed pre-marked for
  the 2026-09-28 review. Planning recorded as a dated entry in team-notes.md;
  metrics recomputed.

- **2026-09-10 (3)** — **Anytype schema completion + repo-scope cleanup.** (1)
  Deleted unrelated content: removed dead-path project references (VResume/
  `projects/portfolio`, `projects/lms`, `projects/tinker`, `projects/cypercloud`,
  `projects/ctc-research`, `projects/pos`) from startup-planner, projects,
  project-guide, market-research, networking — all normalized to the current
  tree (precis-main, precis-ctc, syntara, loop-crm, formints) with a retired-
  paths note; deleted the completed `task_plan.md` housekeeping object.
  (2) Schema completion: added the missing **Plan** type definition
  (`objects/plan.md` — the most-used type, 32 objects, previously undefined)
  with properties, lifecycle contract, default views, and a rendered graph;
  unified the **Blog Post** type name (was Blog/Post) across registry,
  definition, index, and relations; removed the duplicate ⚙️ Configuration
  registry section. (3) Graph enhancement per anytype.io (Objects, Types,
  Properties — describe *and* connect): `_relations.md` gained **Sales &
  leads** (Stage/Related Product/Source/Owner/Next Step/Deal Value/Converted
  To/Lost Reason — grounds `sales-pipeline.md`), **Assignment & accountability**
  (Assigned To, Reviewer, Blocked By, Reported In, Sign-off By), and
  **Marketing claims evidence** (Evidence Level/Source, Review Date, Approved
  By, Safe Wording) sections with Anytype property formats (Text, Number,
  Date, Select, Multi-select, Email/Phone/URL, Checkbox, File & Media,
  Object). `_templates.md` gained the **per-type assignment matrix**
  (accountable → doer → verifier per object type) and **default views per
  type** incl. an "Unowned" review view. (4) **Cross-checked against current
  doc.anytype.io via Context7** (`/anyproto/docs`): all relation property
  formats confirmed within Anytype's 9-format set; added verified behavior
  notes (Type appears in Sidebar only after its first Object; changing Type
  retains Properties; Types are Channel-scoped; Default Object Type setting;
  object formats = Page/View/Chat — this set uses Page only) to `_object-types.md`
  and `guides/channel-structure.md`; Views guidance updated with the
  Query-vs-Collection rule and multi-sort precedence. (5) Housekeeping: README now registers
  the schemas/, blog/, references/, changelogs/ dirs; fixed missing `Status`
  frontmatter on `brand/logos-icons.md` and `schemas/_index.md`; rendered the
  new `plan.md` graph SVG. (5) Checked against doc.anytype.io (Types:
  Properties+Views+Templates; Properties: 9 formats, describe + connect
  functions) — schema remains conceptual markdown, no service integration.
- **2026-09-10 (2)** — **Minimal-content enhancement pass.** (1) Created
  [`sales-pipeline.md`](./sales-pipeline.md) — the missing "Leads" fact table
  of the MAIN.md star schema: 6 pipeline stages (EN/AR), 12-month targets
  vs. pricing-plans, seeded active pipeline (3 pilot restaurants + listing/
  landing sources), closed/lost log with mandatory reasons, lead-source
  generation steps, and the weekly 15-minute review rhythm. Wired into MAIN.md
  (navigation + rhythm + AR index). (2) Replaced the all-placeholder task
  metrics with real computed numbers (Sprint 1: 17/17; Sprint 1.5: 36/41 =
  88%; backlog 15). (3) Audit confirmed remaining minimal files are
  pointers-by-design (backend-plans stub) or reference material — no padding
  added.
- **2026-09-10** — **Business reorganization pass.** (1) Fixed broken audit links
  in `dev-team-plans.md` (`../../audit/` → `../audit/`) and the malformed code
  fence + unclosed bold headings in `feature-tracking.md`. (2) Merged
  `backend-plans.md` into `dev-team-plans.md` § Backend delivery workstreams —
  now a pointer stub; INDEX updated. (3) Reconciled `feature-tracking.md` with
  the 2026-09-06 truth table: added **Precis Landing** and **CTC Research
  Center** sections, renamed LMS → **Precis (precis-main) — LMS** with a core-
  platform ✅ Shipped milestone, marked **Portfolio** as legacy, recorded the
  Loop-CRM AI-hub milestone entry. (4) Rewrote `MAIN.md` as a **business star-
  schema hub** (facts: milestones/tasks/leads/claims; dimensions:
  products/teams/sprints/plans) with complete file inventory and **bilingual
  EN/AR blocks**; `README.md` inventory extended to the full plans family. (5)
  Added Arabic summary blocks to `dev-team-plans.md`, `pricing-plans.md`,
  `marketing-plans.md`, `data-analyst-plans.md`. (6) Refreshed stale dates:
  sprint bookkeeping labeled (Sprint 1.5 note), marketing claims re-baselined
  to 2026-Q4, Formint Cloud launch re-baselined to 2027-Q1, Last-updated
  headers corrected. (7) Clarified the Arabic-parity policy in `INDEX.md`.
- **2026-09-06** — Recorded the un-tracked Loop-CRM AI-hub/locale/connectors work as a ✅ Shipped milestone; added an implementation-status truth table (backend × frontend, incl. "couldn't add") to `dev-team-plans.md`; published the cross-product frontend component audit (`docs/audit/frontend-components-2026-09-06.md`); added the Loop-CRM model-ERD convention (`django_extensions` + `make erd`/`erd-all`, `projects/loop-crm/docs/erd/README.md`), rendering per-team PNGs including the marketing and sales (crm) domain graphs; implemented the Formint Pro create/edit modals that the audit flagged (suppliers, HR roles/schedules/payroll, admin notes, kitchen recipes/ingredients); and verified them — stale `*_name` display bindings replaced with client-side FK resolution, new Vitest payload contract tests (`vitest` 86/86, `astro check` 0/0), backend suite deferred to the product image (`libs/django-bolt` absent from this checkout).
- **2026-09-10** — Completed the remaining Formint Pro list pages + ops/shifts flow: pos/products, pos/inventory and pos/transactions gained delete confirmations and FK-name resolution; crm/contacts, crm/deals, crm/activities and crm/notes now resolve company/contact/stage/deal names from fetched reference lists and their modals send the real FK ids; ops/shifts got its broken script repaired with unique-open-shift enforcement (client + server 409) and auto-computed expected cash. Backend: fixed the non-existent `models.crm_models` imports (all `/crm/*` GETs 500'd), added CRM write views/URLs and shift create/close/detail endpoints, and extended the server persist suite with four shift tests (`vitest` 93/93, `astro check` 0/0; backend suite host-Docker-only).
- **2026-09-05** — Completed the Anytype schema in `mono-repo/`: 15 object type definitions + 20 per-type directories (projects, editions, sprints, releases, integrations, apis, components, tools, pipelines, styles, diagrams, reports, dashboards, data-pipelines, methodologies, insights, recommendations, repositories, modules, documentation) with content tied to the real repo (87 files); all `_prompts.md` workflows marked complete.
- **2026-09-05** — De-duplicated the top-level docs, fixed dangling mono-repo image refs, and added the **diagrams package** (`diagrams/`) with rendered SVG images (API request UML, Django/Rust ERDs, Blinko SurrealDB) + the `render-agenda-diagrams.mjs` pipeline (59 SVGs).
- **2026-09-05** — Added `CONTENT_MODEL.md` (Anytype glossary, 4-package object/markdown separation, plans → milestones reference contract). Added the finished-plans closeout process: completed plans are deleted from `docs/plans/` and recorded as ✅ Shipped milestones in `feature-tracking.md`.
- **2026-08-31** — Created the agenda system: feature tracking, case studies, task board, team notes, meeting templates, completion checklist. Anytype object model (Objects / Types / Properties / Links) inspired the structure.

<!-- AI-generated: review needed -->