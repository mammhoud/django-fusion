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

- **2026-09-06** — Recorded the un-tracked Loop-CRM AI-hub/locale/connectors work as a ✅ Shipped milestone; added an implementation-status truth table (backend × frontend, incl. "couldn't add") to `dev-team-plans.md`; published the cross-product frontend component audit (`docs/audit/frontend-components-2026-09-06.md`); added the Loop-CRM model-ERD convention (`django_extensions` + `make erd`/`erd-all`, `projects/loop-crm/docs/erd/README.md`), rendering per-team PNGs including the marketing and sales (crm) domain graphs; implemented the Formint Pro create/edit modals that the audit flagged (suppliers, HR roles/schedules/payroll, admin notes, kitchen recipes/ingredients); and verified them — stale `*_name` display bindings replaced with client-side FK resolution, new Vitest payload contract tests (`vitest` 86/86, `astro check` 0/0), backend suite deferred to the product image (`libs/django-bolt` absent from this checkout).
- **2026-09-05** — Completed the Anytype schema in `mono-repo/`: 15 object type definitions + 20 per-type directories (projects, editions, sprints, releases, integrations, apis, components, tools, pipelines, styles, diagrams, reports, dashboards, data-pipelines, methodologies, insights, recommendations, repositories, modules, documentation) with content tied to the real repo (87 files); all `_prompts.md` workflows marked complete.
- **2026-09-05** — De-duplicated the top-level docs, fixed dangling mono-repo image refs, and added the **diagrams package** (`diagrams/`) with rendered SVG images (API request UML, Django/Rust ERDs, Blinko SurrealDB) + the `render-agenda-diagrams.mjs` pipeline (59 SVGs).
- **2026-09-05** — Added `CONTENT_MODEL.md` (Anytype glossary, 4-package object/markdown separation, plans → milestones reference contract). Added the finished-plans closeout process: completed plans are deleted from `docs/plans/` and recorded as ✅ Shipped milestones in `feature-tracking.md`.
- **2026-08-31** — Created the agenda system: feature tracking, case studies, task board, team notes, meeting templates, completion checklist. Anytype object model (Objects / Types / Properties / Links) inspired the structure.

<!-- AI-generated: review needed -->