# 📋 docs/agenda/ — Project Agenda System

> **English:** Team tracking, milestones, sales-ready pricing, marketing
> claims, and project closeout for Structa Cloud products — organized as a
> business star schema (facts you count, dimensions you slice by).
>
> **العربية:** تتبّع الفريق، والمعالم المنجزة، والتسعير الجاهز للبيع،
> والادعاءات التسويقية، وإغلاق المشاريع لمنتجات Structa Cloud — منظّمة كـ
> مخطط نجمي للأعمال (حقائق تُحتسب، وأبعاد تُقطّع بها).
>
> **Last updated:** 2026-09-10

## What's in this directory

**English.** The complete inventory — every file grouped by business role:

| Group | Files | Role |
|---|---|---|
| **Definition** | [`CONTENT_MODEL.md`](./CONTENT_MODEL.md) ⭐, [`MAIN.md`](./MAIN.md), [`README.md`](./README.md), [`SUMMARY.md`](./SUMMARY.md), [`INDEX.md`](./INDEX.md) | The contract + hubs/indexes. Read CONTENT_MODEL first. |
| **Delivery facts** | [`feature-tracking.md`](./feature-tracking.md), [`task-tracking.md`](./task-tracking.md), [`sales-pipeline.md`](./sales-pipeline.md), [`team-notes.md`](./team-notes.md) | Milestones (Proposed → Shipped), sprint task board, leads & deals, decision log |
| **Business dimensions** | [`dev-team-plans.md`](./dev-team-plans.md), [`pricing-plans.md`](./pricing-plans.md), [`marketing-plans.md`](./marketing-plans.md), [`data-analyst-plans.md`](./data-analyst-plans.md), [`startup-story.md`](./startup-story.md) | What engineering builds; revenue targets; positioning & campaigns; metrics & evidence; founder journey |
| **Rhythm & gates** | [`meeting-agenda.md`](./meeting-agenda.md), [`completion-checklist.md`](./completion-checklist.md) | 6 meeting templates; definition-of-done + sign-off |
| **Evidence & memory** | [`case-studies.md`](./case-studies.md) + [`case-studies/`](./case-studies/INDEX.md), [`diagrams/`](./diagrams/README.md), [`anytype-extensibility.md`](./anytype-extensibility.md), [`tools-auth-dashboard.md`](./tools-auth-dashboard.md) | Implementation stories with diagrams; rendered SVG package; knowledge-graph proposal; internal tools portal guide |
| **Knowledge graph (Package B)** | [`.mono-repo/`](./.mono-repo/README.md) | Anytype object types + per-type business objects (products, editions, projects, goals, stories) |

**العربية.** القائمة الكاملة — كل ملف مجمّعاً حسب دوره:

| المجموعة | الملفات | الدور |
|---|---|---|
| **التعريف** | `CONTENT_MODEL.md` ⭐، `MAIN.md`، `README.md`، `SUMMARY.md`، `INDEX.md` | العقد + المراكز والفهارس. اقرأ CONTENT_MODEL أولاً. |
| **حقائق التنفيذ** | `feature-tracking.md`، `task-tracking.md`، `sales-pipeline.md`، `team-notes.md` | المعالم المنجزة، ولوحة مهام السباق، والعملاء المحتملون والصفقات، وسجل القرارات |
| **أبعاد الأعمال** | `dev-team-plans.md`، `pricing-plans.md`، `marketing-plans.md`، `data-analyst-plans.md`، `startup-story.md` | ما يبنيه فريق التطوير؛ أهداف الإيرادات؛ التموضع والحملات؛ المقاييس والأدلة؛ رحلة المؤسس |
| **الإيقاع والبوابات** | `meeting-agenda.md`، `completion-checklist.md` | ٦ قوالب اجتماعات؛ تعريف الاكتمال والتوقيع |
| **الأدلة والذاكرة** | `case-studies.md` + `case-studies/`، `diagrams/`، `anytype-extensibility.md`، `tools-auth-dashboard.md` | قصص التنفيذ مع المخططات؛ حزمة SVG المصيّرة؛ مقترح الرسم المعرفي؛ دليل بوابة الأدوات |
| **الرسم المعرفي (الحزمة B)** | `.mono-repo/` | أنواع الكائنات وكائنات الأعمال لكل نوع (المنتجات، الإصدارات، المشاريع، الأهداف، القصص) |

> Note (2026-09-10): `backend-plans.md` was merged into `dev-team-plans.md`
> § Backend delivery workstreams and is now a pointer stub.
>
> ملاحظة: دُمج `backend-plans.md` في `dev-team-plans.md` وأصبح مؤشراً فقط.

## Quick start

```
New to the agenda?            → CONTENT_MODEL.md (definition, packages, reference contract)
Know the object schema?       → .mono-repo/README.md (object types + per-type content objects)
New feature?                  → feature-tracking.md
New task?                     → task-tracking.md
New lead / deal update?       → sales-pipeline.md
Need the price list?          → pricing-plans.md
Writing public claims?        → marketing-plans.md (+ data-analyst-plans.md evidence rules)
Meeting?                      → meeting-agenda.md (copy template) + team-notes.md (record notes)
Feature shipped?              → case-studies.md (write case study with diagram) + feature-tracking.md (update status)
Add an object to the graph?   → .mono-repo/objects/_object-types.md + per-type directory
Plan finished?                → CONTENT_MODEL.md § 4.2 (delete plan → record ✅ Shipped milestone)
Project done?                 → completion-checklist.md (run through it) + team-notes.md (record decision)
```

## How it connects to the rest of docs/

```
docs/agenda/MAIN.md
├── docs/agenda/feature-tracking.md ──→ docs/features/feature-roadmap.md
├── docs/agenda/case-studies.md ──────→ docs/plans/README.md
├── docs/agenda/task-tracking.md ─────→ docs/features/feature-roadmap.md
├── docs/agenda/team-notes.md ────────→ docs/plans/README.md (major decisions)
├── docs/agenda/dev-team-plans.md ────→ docs/plans/editions|django-fusion
├── docs/agenda/marketing-plans.md ───→ docs/plans/marketing-claims.md
├── docs/agenda/meeting-agenda.md ────→ docs/agenda/task-tracking.md
└── docs/agenda/completion-checklist.md ──→ feature-tracking → case-studies → plans
```

## Anytype inspiration

This agenda system was designed with Anytype's object-based knowledge model in
mind:

| Anytype concept | Agenda equivalent |
|----------------|-------------------|
| **Object** | A task, a feature, a case study, a meeting note |
| **Type** | Feature, Task, Case Study, Meeting Note — the category |
| **Properties** | Status, Assignee, Priority, Due Date, Sprint — the metadata |
| **Links** | Feature → Case Study, Task → Feature, Meeting → Decision |

Just like Anytype says: "Everything is an Object. Objects ask 'what does this
relate to?'" — our agenda entries are objects that link to each other, not
files stuffed into folders.

See: [Anytype Objects](https://doc.anytype.io/anytype/create/objects), [Anytype Types](https://doc.anytype.io/anytype/organize/types), [Anytype Properties](https://doc.anytype.io/anytype/organize/properties)

## Diagrams

All architecture and flow diagrams use mermaid, **rendered to SVG images** so
they are viewable everywhere (GitHub, Docus, Anytype import). See
[`diagrams/README.md`](./diagrams/README.md) — rendered assets live in
`docs/public/agenda/diagrams/` and mermaid sources are editable. Re-render with:

```bash
node docs/scripts/render-agenda-diagrams.mjs
```

Test diagrams with `npm run validate-content` in the docs pipeline.

## Maintenance

- **Owner:** Workspace / Product leads
- **Review cadence:** Per sprint + major release gates
- **Add entries when:** Features ship, tasks complete, meetings happen, decisions are made
- **Archive when:** Projects close (follow `docs/plans/document-lifecycle.md`)

---

## Remarks & Notes

- This is a working system, not a bureaucratic overhead — if a template isn't serving the team, adapt it
- The most valuable output is the case studies with mermaid diagrams — they're the team's institutional memory
- Link everything that relates to everything else — isolated entries lose their value
- Keep entries current — stale tracking is worse than no tracking
- Business-first rule: agenda tracking files describe outcomes, money, and ownership — implementation detail belongs in plans and case studies

<!-- AI-generated: review needed -->
