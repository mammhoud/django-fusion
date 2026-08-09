# Structa Cloud — Canonical plans

> **Status:** Active registry
> **Last updated:** 2026-08-09
> **Branch:** `generic`

## Read this first

Start with [`../recommendations.md`](../recommendations.md) for the recommended work order. This directory is the single source of truth for engineering plans, implementation tasks, migrations, testing work, and deployment changes.

Do not create new plans in `docs/dev/plans/`, `docs/plans/migrated/`, or project-local `docs/superpowers/plans/` directories. Active plans belong in the scope directory below. Historical material belongs in `legacy/` and must not be treated as current scope.

## Plan registry

| Scope | Entry point | What belongs here |
|---|---|---|
| Repository | [`repository/`](repository/) | Cross-project architecture, cleanup, migrations, and delivery |
| Formint/POS | [`pos/README.md`](pos/README.md) | Canonical product, desktop, cloud, sync, and migration plans |
| Formint editions | [`editions/README.md`](editions/README.md) | Community → Standard → Pro → Cloud execution chain and SDK work |
| CMS Fusion | [`cms-fusion/`](cms-fusion/) | CMS migration, frontend, dashboard, and component work |
| LMS Fusion | [`lms-fusion/`](lms-fusion/) | LMS migration and cleanup work |
| Landing Fusion | [`landing-fusion/`](landing-fusion/) | Landing site architecture, content, and frontend work |
| django-fusion | [`django-fusion/`](django-fusion/) | Shared framework and asset/component work; submodule-owned plan is linked below |
| Lifecycle | [`document-lifecycle.md`](document-lifecycle.md) | Status, ownership, archive, deletion, and rollback policy |
| Claims | [`marketing-claims.md`](marketing-claims.md) | Evidence-backed product and marketing claims |
| Deletion register | [`deletion-manifest.md`](deletion-manifest.md) | Approval and rollback record for removals |
| Historical evidence | [`legacy/`](legacy/) | Read-only completed plans, snapshots, and migration evidence |
| External library plan | [`libs/django-fusion/docs/ENHANCEMENT_PLAN.md`](../../libs/django-fusion/docs/ENHANCEMENT_PLAN.md) | Maintained in the django-fusion submodule; not moved into the parent repo |

## Current recommendations

1. **Formint/POS vertical slice:** continue the canonical Professional plan and the edition chain in the order shown in [`editions/README.md`](editions/README.md). Keep old POS implementations as compatibility sources until parity gates pass.
2. **Landing Fusion quality:** preserve the post-only code-rendering contract and run its backend/frontend checks before adding new content blocks.
3. **CMS/LMS Fusion:** choose one owned frontend or deployment task from the project plan, assign an owner, and verify it with the command named in the plan.
4. **Repository cleanup:** use the lifecycle policy and deletion manifest. Archive evidence before deleting duplicates; do not use a status snapshot as proof that a replacement is complete.
5. **Documentation maintenance:** update this index and the relevant scope README whenever a plan is added, moved, superseded, or completed.

## Active plan highlights

| Plan | Status | Canonical path |
|---|:---:|---|
| Formint POS Professional Edition | Current / Phase 1 started | [`pos/formint-pos-professional-plan.md`](pos/formint-pos-professional-plan.md) |
| Formint edition chain | Active | [`editions/README.md`](editions/README.md) |
| POS Cloud architecture | Planned / gate-based | [`pos/cloud-plan.md`](pos/cloud-plan.md) |
| Tauri plugin migration | Current migration | [`pos/tauri-plugins-enhancement-plan.md`](pos/tauri-plugins-enhancement-plan.md) |
| CMS Fusion migration and frontend | Mixed: complete core, planned enhancements | [`cms-fusion/`](cms-fusion/) |
| LMS Fusion migration | Core complete; cleanup tracked | [`lms-fusion/migration-plan.md`](lms-fusion/migration-plan.md) |
| Landing Fusion | Active | [`landing-fusion/`](landing-fusion/) |
| Repository migration cleanup | Partial / gate-based | [`repository/migration-cleanup-master.md`](repository/migration-cleanup-master.md) |
| Legacy evidence | Archived | [`legacy/`](legacy/) |

## Lifecycle rules

- **Current / Active:** authoritative, owned, and linked from this registry.
- **Planned:** approved direction without implementation evidence.
- **Superseded:** replaced by a named current document; keep a redirect or archive note.
- **Archived:** read-only evidence with a reason and replacement.
- **Deletion candidate:** no removal until references, archive, hash, owner approval, and restore checks are recorded.

See [`document-lifecycle.md`](document-lifecycle.md) for the full policy. Record proposed removals in [`deletion-manifest.md`](deletion-manifest.md).

## Layout

```text
docs/plans/
├── README.md                 # This canonical registry
├── ../recommendations.md     # Recommended priorities
├── repository/               # Cross-repository plans
├── pos/                      # POS product and migration plans
├── editions/                 # Formint edition execution chain
├── cms-fusion/               # CMS Fusion plans
├── lms-fusion/               # LMS Fusion plans
├── landing-fusion/           # Landing Fusion plans
├── django-fusion/            # Shared framework plans
├── legacy/                   # Read-only historical evidence
├── document-lifecycle.md
├── deletion-manifest.md
└── marketing-claims.md
```

## Related documentation

- [`../README.md`](../README.md) — main documentation hub
- [`../recommendations.md`](../recommendations.md) — recommendations first
- [`../Anytype/`](../Anytype/) — product decisions and knowledge graph (separate from engineering plans)
- [`../../CHANGELOG.md`](../../CHANGELOG.md) — repository change history
