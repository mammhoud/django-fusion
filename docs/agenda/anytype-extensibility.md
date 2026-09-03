---
title: Anytype Extensibility Research
description: Research on the Anytype object model (anytype-ts + doc.anytype.io) and concrete extensibility + project-separation enhancements mapped to the Structa Cloud agenda/mono-repo docs
navigation:
  title: Anytype Extensibility
  icon: i-lucide-git-branch
object:
  type: "plan"
  id: "agenda.anytype-extensibility"
attributes:
  source_path: "agenda/anytype-extensibility.md"
  canonical_route: "/docs/en/agenda/anytype-extensibility"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "proposed"
tags:
  - structa-cloud
  - anytype
  - knowledge-graph
  - extensibility
  - project-separation
  - research
links:
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "Mono-repo Anytype hub"
    to: "/agenda/INDEX"
    icon: "i-lucide-list"
---

# 🔬 Anytype Extensibility Research — Enhancements for the Agenda & Project Separation

> **Purpose:** Record what Anytype (the local-first knowledge OS) actually offers — from its open client repo `anyproto/anytype-ts` and its docs — and translate it into concrete extensibility + project-separation enhancements for the Structa Cloud agenda docs (`docs/agenda/`, `docs/agenda/mono-repo/`) and the product boundaries in the monorepo.
> **Created:** 2026-09-03
> **Status:** Proposed — implement in follow-up passes; each item is independently shippable

---

## 🧠 What Anytype Actually Is (source: repo + docs)

Researched 2026-09-03 against:

| Source | What it tells us |
|--------|------------------|
| [`anyproto/anytype-ts`](https://github.com/anyproto/anytype-ts) | Desktop client (Electron + TS), **local-first / offline-first**, optional P2P sync, zero-knowledge E2E encryption via any-sync, **composable blocks**, extensible via a **gRPC API** and AI *Agents* (AGENTS.md), open under Any Source Available License 1.0. |
| [`doc.anytype.io` — Types](https://doc.anytype.io/anytype/organize/types) | Every **Object** has exactly one **Type** (a "cookie cutter"). A Type bundles **Properties**, **Views**, and **Templates**. Types are per-space and can be changed on objects at any time; properties survive type changes. |
| [`doc.anytype.io` — Properties](https://doc.anytype.io/anytype/organize/properties) | Properties *describe* (status/priority/due) and *connect* (Object links). Formats: Text, Number, Date, Select, Multi-select, Email/Phone/URL, Checkbox, File & Media, **Object**. One property can be reused across many types. |
| [`doc.anytype.io` — Queries](https://doc.anytype.io/anytype/organize/queries) | **Queries** filter objects by type/property/value. Save filter combinations as **Views**, not new queries. |
| [`doc.anytype.io` — Collections](https://doc.anytype.io/anytype/organize/collections) | **Collections** = hand-curated containers (folder-like). Objects exist independently; removing from a collection never deletes. **Query = rules that update over time; Collection = curation that stays stable.** |

### The mental model in one table

| Anytype concept | Meaning | Already mirrored in our agenda? |
|-----------------|---------|-------------------------------|
| **Object** | Every entry is a first-class entity | ✅ `docs/agenda/mono-repo/objects/_object-types.md` defines ~30 types; each content doc is an object |
| **Type** | Blueprint: object type + property set | ✅ Object type + frontmatter per doc |
| **Property** | Typed field (Select/Multi-select/Object links…) | ✅ Status/Tags/Owner/Related-* properties in `_object-types.md` + `_relations.md` |
| **Relation** | Typed link between objects (source → target, cardinality) | ✅ `objects/_relations.md` (plural = many, singular = one) |
| **Query / View** | Saved filter+sort+layout over a type | ⚠️ Tables per tracking file, but no saved "views" registry |
| **Collection** | Hand-curated grouping independent of type | ⚠️ Ad-hoc hubs (MAIN.md, README.md) do this by hand |
| **Template** | Reusable per-type starter content | ⚠️ Meeting templates exist; feature/case-study templates are prose-only |
| **Space** | Encryption-scoped, isolated container | ⚠️ Only lightly modeled — see "project separation" below |
| **Graph** | Link-based navigation instead of folders | ✅ → links + Graph View connections described in `_relations.md` |

---

## 🚀 Extensibility Proposals for the Agenda Docs

Concrete, independent enhancements, derived directly from the Anytype model above. Each lists *what to build*, *where*, and *why it maps to Anytype*.

### 1. 📂 Collections — add a "Collections registry" (`objects/_collections.md`)

Anytype's sharpest distinction is **Queries (dynamic) vs Collections (curated)**. We have neither formalized — every hub table is hand-maintained prose.

**Build:** add `docs/agenda/mono-repo/objects/_collections.md` defining named collections with (a) a Query-style filter definition where one exists (type + status + tags) and (b) a curated link list. Start with 3 collections:
- `active-delivery` — filter: `Status = Active|In Development` across features/plans/tasks; curated additions for loose items.
- `q3-launch` — curated only (mixed types, no shared property → collection is correct).
- `backend-infra` — filter on `#backend` + `#architecture`.

**Why Anytype:** Collections keep loosely-related objects together *without* forcing a shared property — exactly the case our feature vs plan vs case-study docs hit today.

### 2. 🔍 Queries / Saved Views — document each type's "view" table

**Build:** extend `objects/_object-types.md` so every type that already has a tracking table documents its **default view** — column set + default filters + default sort — in one line. E.g. Task default view: `Status → Assignee → Due Date`, filter `Status != Archived`, sort `Due Date`.

**Why Anytype:** "Save filter combinations as Views, not new Queries." Our current tables re-state filters on every file; the view definition belongs on the type.

### 3. 🧩 Templates — per-type starter files (`objects/_templates.md`)

`_relations.md` already links to `_templates.md`, which **does not exist yet** (broken reference).

**Build:** create `docs/agenda/mono-repo/objects/_templates.md` with one short starter block per high-use type: Feature, Plan, Task, Case Study/Decision, Goal, Product. Each template = frontmatter skeleton + 3 bullet section skeleton. Reference the file from `_relations.md` (already points there).

**Why Anytype:** Templates = per-type standards ("all vacations have a photo album"). A starter block per type makes new docs consistent without copying a whole case-study file.

### 4. 🔗 Relation hygiene — cardinality + backlink checks in `_prompts.md`

**Build:** add to `docs/agenda/mono-repo/_prompts.md` "Knowledge graph operations":
- **Relation lint:** every `Related X`/`Owner`/`Depends On` value in a doc must be (a) a real path, (b) the correct direction per `_relations.md` cardinality.
- **Backlink pass:** after adding relation `A → B`, check whether `B` should list `A` (Anytype relations are bidirectional in graph view).

**Why Anytype:** Relations are typed and directional; graph navigation only works when both ends are truthful. Our `_prompts.md` graph-integrity section already checks forward links + orphans — this closes the backlink gap.

### 5. 📊 Type vs Folder — keep object dirs as *types*, not taxonomies

Anytype's rule: objects ask "what does this relate to?", not "where does this go?". Our dirs (`features/`, `plans/`, `tasks/`) are type-filters, which is correct — but `objects/_object-types.md` defines types (Changelog, Diagram, Release, Pipeline, Style, Component, API…) with **no empty directory yet** (`changelogs/` has 1 file, `milestones/` 1, `references/` 2, `schemas/` 1).

**Build:** enforce the README rule — *type dirs exist because the type exists, not the reverse* — and record the decision in `_prompts.md` so agents don't create new dirs for ad-hoc types.

**Why Anytype:** Deleting a type with objects prompts; empty dirs here should prompt a merge, not new taxonomy.

### 6. 🧭 Object header / frontmatter consistency — one "properties panel"

Anytype shows the most relevant properties in the object **header** (line/list layout).

**Build:** in `_prompts.md` quality checklist, define the canonical frontmatter order for content objects: `Object type` → `Tags` → `Status` → then type-specific `Related *` / `Owner` properties, matching `_object-types.md`. The mono-repo README already mandates frontmatter; this only pins the order so diffs are clean and scripts can parse.

**Why Anytype:** property layout is part of the type, not the individual object.

---

## 🧱 Project-Separation Proposals (Anytype "Spaces" → Monorepo Boundaries)

Anytype isolates content into **Spaces** (different encryption keys — types/relations cannot silently sync across spaces). The monorepo equivalent is *product boundaries*: shared rules stay shared, product code stays inside the owning product. Mapping:

| Anytype | Monorepo equivalent today | Gap found in this session |
|---------|---------------------------|---------------------------|
| Space = isolated container | Product root (`projects/precis/precis-ctc/`, `projects/precis/precis-main/`, `projects/syntara/`, `projects/formints/*/`) | Shared assets live in one monorepo tree (`projects/assets/`) mounted into each site's frontend+backend; **the "space" boundary is code, the shared dir is deliberate** |
| Space-scoped types | Per-product `AGENTS.md` + local app boundaries | ✅ good — root rules + nearest-file-wins |
| Shared relations across spaces | `libs/django-fusion/`, `projects/precis/configs/`, `projects/assets/` | CTC `MEDIA_ROOT` default drifted to a precis-local rendition tree instead of the canonical shared tree — **fixed this session** (see below) |

### Concrete separation actions (derived from the audit + Anytype model)

1. **Document the shared-assets contract once** — one "shared vs per-site assets" decision object so future edits stop at the right tree. The contract, verified live this session:
   - **Canonical media/static source** = monorepo shared `projects/assets/` (media per site under `projects/assets/media/<site>/`, static shared under `projects/assets/static/`).
   - **Per-site staticfiles** (collectstatic output) = `<site>/assets/staticfiles/`, bind-mounted into the site container and into `assets-proxy` as `/var/www/sites/<site>/static/`.
   - **Fallback chain** = per-host Nginx `$static_root`/`$media_root` maps default to the shared `/var/www/static` + `/var/www/media` roots when the per-site alias misses → this is the "fallback from the other side" (frontend Nginx layer falls back to the shared dir when the site-local file isn't loaded).
   - Home for the object: `docs/agenda/mono-repo/decisions/shared-assets-contract.md` or the assets guide `docs/guides/10-fusion-assets-health.md` (pick one; link from `_prompts.md`).
2. **Mirror "Types are per-Space"** — a product may override a shared default only inside its own settings module; the shared `configs/base/assets.py` stays the reference. CTC now does this correctly (settings default → canonical shared tree; env var wins in containers).
3. **Keep cross-product wiring in the "shared space"** — anything mounted into two products (assets-proxy, tasks stack worker/scheduler) belongs to `application/tools` / `projects/*.yml` compose, not inside one product. (Worker/scheduler now mount no asset data — see Workstream 1 below.)

---

## 📋 What Was Already Done This Session (evidence for the proposals)

1. **Worker/scheduler asset minimization** — shared tasks worker/scheduler and the CTC scheduler no longer bind the monorepo `projects/assets`/media trees; the CTC worker keeps media only where its content tasks write Wagtail media. Validated with `docker compose config -q`.
2. **Coder redeploy** — databases (Postgres/Redis) + Coder deployed on this host; Coder healthy; Precis scheduler restarted cleanly and registered both scheduled jobs.
3. **Shared-assets audit fixes** — CTC `MEDIA_ROOT` default corrected from the stray `projects/precis/assets/media/ctc-research` tree (380K rendition-only) to canonical `projects/assets/media/ctc-research`; `manage.py check` clean. `tests/test_shared_media.py` rewritten from the retired `application/proxy` shared-proxy topology to the live `application/tools` assets-proxy contract — **26/26 pass** including live container checks.
4. **This research** — Anytype repo/docs reviewed; proposals above recorded.

---

## 🔗 Related

| Topic | Path |
|-------|------|
| Agenda hub | [`./MAIN.md`](./MAIN.md) |
| Anytype object types (agenda) | [`./mono-repo/objects/_object-types.md`](./mono-repo/objects/_object-types.md) |
| Anytype relations (agenda) | [`./mono-repo/objects/_relations.md`](./mono-repo/objects/_relations.md) |
| Agent prompts for the graph | [`./mono-repo/_prompts.md`](./mono-repo/_prompts.md) |
| Fusion assets health guide | [`../guides/10-fusion-assets-health.md`](../guides/10-fusion-assets-health.md) |
| Shared media contract test | [`tests/test_shared_media.py`](../../tests/test_shared_media.py) |

---

## Remarks & Notes

- **This is a proposal, not a build order.** Each numbered item is independently shippable; start with #3 (`_templates.md`) since `_relations.md` already links to it, then #4 (relation lint in `_prompts.md`).
- Anytype's "Spaces don't sync shared types" is a *warning*, not a goal — in the monorepo the shared layer is deliberate and lives in `projects/assets`, `libs/django-fusion`, and `projects/precis/configs`.
- The agenda docs are markdown objects with Docus/Affine frontmatter (`object.type`, `tags`, `links`) — the "Anytype import" is conceptual; keep one source of truth per object.
- Anytype.io repo facts (local-first, P2P, E2E, gRPC, AI agents) are recorded here only as inspiration; no Anytype service is being integrated into the stack.

<!-- AI-generated: review needed -->
