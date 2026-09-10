---
title: Agenda Content Model
description: The definition of the agenda content system — Anytype concept glossary, object/markdown packaging, and the team-wide reference rules that route every link through plans and milestones
navigation:
  title: Content Model
  icon: i-lucide-database
object:
  type: "guide"
  id: "agenda.content-model"
attributes:
  source_path: "agenda/CONTENT_MODEL.md"
  canonical_route: "/docs/en/agenda/content-model"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - agenda
  - content-model
  - anytype
  - knowledge-graph
  - team-reference
links:
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "Plans Registry"
    to: "/plans"
    icon: "i-lucide-folder"
  - label: "Anytype Extensibility"
    to: "/agenda/anytype-extensibility"
    icon: "i-lucide-git-branch"
---

# 📐 Agenda Content Model — Definition & Team Reference

> **Purpose:** Define what lives in the agenda, how agenda content is packaged
> (object types ↔ markdown files), and the reference rules that keep the whole
> team on one map. Every link in the agenda resolves through **plans** (what we
> agreed to build) and **milestones** (what we finished) — this document is the
> contract that makes that true.
> **Last updated:** 2026-09-05
> **Owner:** Workspace / Product leads

---

## 1. What the Agenda Is

The agenda (`docs/agenda/`) is the team's **working memory and delivery map**:
features, tasks, meeting notes, case studies, completion checklists, and the
finished-work milestone log. It is *not* a second engineering plan source —
plans stay in `docs/plans/`, and the agenda references them.

| Question | Answer |
|---|---|
| Where do engineering plans live? | `docs/plans/` (canonical registry: `docs/plans/README.md`) |
| Where do finished plans get recorded? | `docs/agenda/feature-tracking.md` § ✅ Shipped milestones + `team-notes.md` |
| Where does day-to-day delivery get tracked? | `docs/agenda/` (features, tasks, sprints, notes, case studies) |
| Where does the Anytype object schema live? | `docs/agenda/.mono-repo/objects/` (`_object-types.md`, `_relations.md`, `_tags.md`, `_templates.md`) |
| Where is the team reference contract? | **This file** — `CONTENT_MODEL.md` |

---

## 2. Anytype Concept Glossary (from doc.anytype.io)

Researched 2026-09-05 against `doc.anytype.io` (Objects, Types, Properties,
Views, Queries, Collections). The agenda applies these concepts conceptually —
markdown files are the objects, frontmatter is the property panel.

### 2.1 Object

> "Everything you create is an Object… Objects ask 'what does this relate
> to?', not 'where does this go?'" — [Anytype Docs: Objects](https://doc.anytype.io/anytype/create/objects)

Every agenda entry is a first-class object: a feature, a task, a milestone, a
meeting note, a case study, a plan pointer. Objects link to each other; they
are never duplicated into folders.

**Agenda rule:** one markdown file = one object. A file may appear in many
indexes (collections), but the content lives in exactly one file.

### 2.2 Type

> "If an Object is a cookie, then the Type is the cookie cutter… Every Type
> has Properties, Views, and Templates." — [Anytype Docs: Types](https://doc.anytype.io/anytype/organize/types)

A type is a blueprint: what properties every object of that kind carries.
The agenda's canonical types are defined in
[`mono-repo/objects/_object-types.md`](mono-repo/objects/_object-types.md):
Workspace, Project, Plan, Goal, Milestone, Task, Sprint, Product, Edition,
Feature, Release, Team, Person, Decision, and the rest.

**Agenda rule:** every content file declares its `Object type` in frontmatter,
and its structure follows the type's template in
[`mono-repo/objects/_templates.md`](mono-repo/objects/_templates.md).

### 2.3 Property

> "Properties are the details you attach to an Object — its due date, status,
> priority, tags… Properties serve two functions: Describe Objects and Connect
> Objects." — [Anytype Docs: Properties](https://doc.anytype.io/anytype/organize/properties)

Properties are the typed fields: Status, Priority, Due Date, Owner, Tags, and
the `Related *` relations. They let you filter and sort any collection of
objects without moving files.

**Agenda rule:** frontmatter is the property panel. Minimum contract for every
content object: `Object type`, `Tags`, `Status` + the type's required
properties (see the compact table in `_templates.md`).

### 2.4 View

> "Views are visual lenses… Layouts, Filters, and Sorts — you never need to
> duplicate content." — [Anytype Docs: Views](https://doc.anytype.io/anytype/organize/views)

A view is a saved combination of layout + filters + sort over a type. The
agenda's tracking tables (`feature-tracking.md`, `task-tracking.md`) are views
— every table is a lens over one object type.

**Agenda rule:** a tracking table is a view, not a new object. When a filter
set is used repeatedly, define it once as the type's default view in
`_object-types.md` instead of restating it in every file.

### 2.5 Query vs Collection

> "With Collections, you're curating a group of Objects that don't change much
> over time. With Queries, you're filtering Objects that likely change over
> time." — [Anytype Docs: Collections](https://doc.anytype.io/anytype/organize/collections)

| Concept | Anytype definition | Agenda equivalent |
|---|---|---|
| **Query** | Rule-driven filter over a type/property, auto-updating | A tracking table or saved filter (e.g. "all features with Status = In Progress") |
| **Collection** | Hand-curated grouping independent of type | An index hub (e.g. `MAIN.md`, `INDEX.md`, the ✅ Shipped milestone section) |

**Agenda rule:** use queries (filters/tables) when membership is derivable
from a property; use collections (curated lists) when the group has no shared
property. `MAIN.md` and the "Shipped milestones" sections are collections;
tracking tables are queries.

### 2.6 Template

> "Templates — adds standards, such as all vacations having a photo album."
> — [Anytype Docs: Types](https://doc.anytype.io/anytype/organize/types)

A per-type starter structure. `meeting-agenda.md` is the meeting template set;
`case-studies.md` and `_templates.md` provide the feature/case-study/object
starter blocks.

---

## 3. Packaging — How Objects Map to Markdown Files

The agenda is split into **four packages**. Each package is one directory with
one job. Objects never migrate between packages except by lifecycle action.

```text
docs/
├── agenda/                      # PACKAGE A — team delivery & memory
│   ├── MAIN.md                  #   hub / collection
│   ├── README.md                #   overview / collection
│   ├── CONTENT_MODEL.md         #   THIS FILE — the contract
│   ├── feature-tracking.md      #   Query/View over Feature objects
│   ├── task-tracking.md         #   Query/View over Task objects
│   ├── team-notes.md            #   Note/Decision objects (dated log)
│   ├── meeting-agenda.md        #   Template collection
│   ├── completion-checklist.md  #   Gate checklist object
│   ├── case-studies.md          #   Case Study objects + template
│   ├── diagrams/                #   Diagram objects — rendered SVGs + mermaid sources
│   │   └── README.md            #     collection: API UML, Django/Rust ERDs, Blinko
│   ├── anytype-extensibility.md #   Research/proposal object
│   └── ...
├── agenda/mono-repo/            # PACKAGE B — Anytype import set (one Channel)
│   ├── objects/                 #   Schema: _object-types, _relations, _tags, _templates, _status + per-type files
│   ├── plans/ products/ features/ milestones/ tasks/ goals/ ...  #   Knowledge-graph objects
│   ├── projects/ editions/ sprints/ releases/ integrations/ apis/ ...  #   Type-home dirs (one per type)
│   ├── tools/ pipelines/ styles/ diagrams/ repositories/ modules/ documentation/ ...
│   ├── reports/ dashboards/ data-pipelines/ methodologies/ insights/ recommendations/ ...
│   └── guides/                  #   Import + writing method
└── plans/                       # PACKAGE C — canonical engineering plans
    └── README.md                #   registry (single source of truth)
```

### Package responsibilities

| Package | Path | Job | Object types | Lifecycle |
|---|---|---|---|---|
| **A — Team delivery & memory** | `docs/agenda/` | Day-to-day tracking: features, tasks, sprints, notes, case studies, milestones | Feature, Task, Sprint, Note, Decision, Case Study, Milestone | Active while work is in flight; shipped features become ✅ Shipped milestones |
| **B — Anytype import set** | `docs/agenda/mono-repo/` | The knowledge-graph schema + focused content import (one Anytype Channel) | All types in `objects/_object-types.md` | Schema is durable; content objects stay current or become Archived |
| **C — Engineering plans** | `docs/plans/` | What we agreed to build, how, and why (ADR-style) | Plan, Decision, Migration | Planned → Active → Completed → deleted (git history is archive) |
| **A.1 — Diagrams** (sub-package of A) | `docs/agenda/diagrams/` + `docs/public/agenda/diagrams/` | Rendered diagram images + editable mermaid sources (API request flows, Django/Rust ERDs, Blinko SurrealDB); `docs/scripts/render-agenda-diagrams.mjs` re-renders | Diagram | Re-render when the source changes; images are derived assets |
| **D — Product docs & guides** | `docs/loop-crm/`, `docs/precis/`, `docs/guides/`, … | Reader-facing product documentation | Guide, Reference, Product | Maintained per product |

### Separation rules

1. **One object type per home directory.** `features/`, `tasks/`, `plans/`,
   `milestones/` exist because the type exists — never create a directory for
   an ad-hoc type.
2. **No duplicate content across packages.** Package A links to Package C
   plans; it never re-states a plan. Package B imports knowledge-graph objects;
   it never re-states engineering detail (link, don't duplicate).
3. **Type dirs beat taxonomy.** An object belongs in the directory of its type;
   cross-cutting groupings are collections (index files), not new directories.
4. **Schema changes land in Package B first** (`mono-repo/objects/`), then the
   agenda's tracking tables are updated to match the type definition.

---

## 4. The Reference Contract — Every Link Goes Through Plans & Milestones

This is the **team-wide rule** the agenda enforces: any link from the agenda to
engineering work must resolve through **plans** (forward) and **milestones**
(backward).

### 4.1 Forward: work → plan

A feature, task, or case study that implements a plan links **to** the plan:

```markdown
**Notes:** Part of [`docs/plans/loop-crm/merge-plan.md`](../plans/loop-crm/merge-plan.md) § 12.
```

Rules:

- Every in-flight feature/task references its plan in `Notes` (or a `Related
  plan` frontmatter property).
- The plan registry (`docs/plans/README.md`) is the single source of truth for
  plan status — the agenda never invents plan status.
- If a feature has no plan, it is a proposal → add it to
  `feature-tracking.md` as `Proposed` and note "no plan yet".

### 4.2 Backward: finished plan → milestone

When a plan is completed, it is **deleted from `docs/plans/`** (git history is
the archive) and recorded as a ✅ Shipped milestone in the agenda:

1. Add a ✅ Shipped entry to `feature-tracking.md` § the product's "Finished
   Milestones" section.
2. Add a dated entry to `team-notes.md` recording the closeout decision.
3. Add ✅ Done rows to `task-tracking.md` for the closeout tasks.
4. Update every reference to the deleted plan (plans registry, reference maps,
   audit, other plans) to point at the milestone record instead.
5. Never leave a dangling link to a deleted plan file.

### 4.3 The milestone log

The finished-milestone log is the backward map of everything the team shipped.
Each entry carries: **Status ✅ Shipped**, **scope** (what was delivered),
**acceptance criteria**, and **notes** pointing at the archive record +
related notes/tasks. New work links to these milestones when it builds on
shipped capability.

---

## 5. First Meeting — Kickoff Reference

> **First meeting folder (Google Drive):**
> <https://drive.google.com/drive/folders/1-A0MxVvAUpaOc56Nr9t2672DkrvgILb0>

The first team meeting on the agenda system should walk through, in order:

1. **This file** — the content model: what the agenda is, the four packages,
   the reference contract.
2. **`MAIN.md`** — how the agenda documents connect (hub diagram).
3. **`meeting-agenda.md`** — the meeting templates to use from here on.
4. **The finished-milestone log** (`feature-tracking.md` § ✅ Shipped) — the
   plans already closed and recorded.
5. **Anytype concepts** (`anytype-extensibility.md` + this file § 2) — so the
   team shares the object vocabulary.
6. Assign owners for the action items in `task-tracking.md` and record the
   meeting in `team-notes.md`.

---

## 6. Maintenance

- **Owner:** Workspace / Product leads
- **Review cadence:** Per sprint + when a package boundary or reference rule
  changes
- **Update triggers:** New object type, package move, reference-contract
  change, first-meeting follow-ups
- **Archive policy:** Follow [`plans/document-lifecycle.md`](../plans/document-lifecycle.md)

---

## 🔗 Related

| Topic | Path |
|-------|------|
| Agenda hub | [`./MAIN.md`](./MAIN.md) |
| Agenda overview | [`./README.md`](./README.md) |
| Meeting templates | [`./meeting-agenda.md`](./meeting-agenda.md) |
| Feature lifecycle | [`./feature-tracking.md`](./feature-tracking.md) |
| Sprint tasks | [`./task-tracking.md`](./task-tracking.md) |
| Team notes | [`./team-notes.md`](./team-notes.md) |
| Anytype object types | [`./mono-repo/objects/_object-types.md`](./mono-repo/objects/_object-types.md) |
| Anytype relations | [`./mono-repo/objects/_relations.md`](./mono-repo/objects/_relations.md) |
| Object templates | [`./mono-repo/objects/_templates.md`](./mono-repo/objects/_templates.md) |
| Anytype extensibility research | [`./anytype-extensibility.md`](./anytype-extensibility.md) |
| Plans registry (canonical) | [`../plans/README.md`](../plans/README.md) |
| Document lifecycle | [`../plans/document-lifecycle.md`](../plans/document-lifecycle.md) |

---

## Remarks & Notes

- The agenda is a **working system**: if a template or a package boundary isn't
  serving the team, adapt it here first, then propagate the change.
- The Anytype concepts are applied **conceptually** — markdown + frontmatter
  are the objects and properties; no Anytype service is integrated.
- The reference contract (plans → milestones) is the highest-value rule in this
  file: it is what keeps the agenda truthful about what is planned vs shipped.
- Keep this file as the canonical definition; indexes link to it rather than
  restating the packaging rules.

<!-- AI-generated: review needed -->