# 🗺️ Plans — Canonical Registry

> **Status:** Active registry
> **Last updated:** 2026-08-10
> **Branch:** `generic`

## Read this first

Start with [`../recommendations.md`](../recommendations.md) for the recommended work order. This directory is the single source of truth for engineering plans, implementation tasks, migrations, testing work, and deployment changes.

Do not create new plans in `docs/dev/plans/`, `docs/plans/migrated/`, or project-local directories. Active plans belong in the scope directory below. Historical material belongs in `legacy/` and must not be treated as current scope.

## Plan registry

| Scope | Entry point | What belongs here |
|---|---|---|
| Repository | [`repository/`](repository/) | Cross-project architecture, cleanup, migrations, and delivery |
| Formint/POS | [`pos/README.md`](pos/README.md) | Canonical product, desktop, cloud, sync, and migration plans |
| Formint editions | [`editions/README.md`](editions/README.md) | Community → Standard → Pro → Cloud → Client → SDK execution chain |
| CMS Fusion | [`cms-fusion/`](cms-fusion/) | CMS migration, frontend, dashboard, and component work (now merged into Precis/Landing-Fusion) |
| LMS Fusion | [`lms-fusion/`](lms-fusion/) | LMS migration and cleanup work (now Precis) |
| Landing-Fusion | [`landing-fusion/`](landing-fusion/) | Landing site architecture, content, and frontend work |
| django-fusion | [`django-fusion/`](django-fusion/) | Shared framework, tasks, MCP, asset/component work; submodule-owned plan |
| Formint Cloud | [`pos/cloud-plan.md`](pos/cloud-plan.md) | Cloud master: Channels, WebSocket sync, Bolt dashboard, Unfold admin |
| Lifecycle | [`document-lifecycle.md`](document-lifecycle.md) | Status, ownership, archive, deletion, and rollback policy |
| Claims | [`marketing-claims.md`](marketing-claims.md) | Evidence-backed product and marketing claims |
| Deletion register | [`deletion-manifest.md`](deletion-manifest.md) | Approval and rollback record for removals |
| Historical evidence | [`legacy/`](legacy/) | Read-only completed plans, snapshots, and migration evidence |
| External library plan | [`../../libs/django-fusion/docs/ENHANCEMENT_PLAN.md`](../../libs/django-fusion/docs/ENHANCEMENT_PLAN.md) | Maintained in the django-fusion submodule |

## Current recommendations

1. **Formint/POS vertical slice:** continue the canonical Professional plan and the edition chain in the order shown in [`editions/README.md`](editions/README.md). Formint-cloud is the current cloud master (renamed from `formintB`/`pos-cloud`).
2. **Landing-Fusion quality:** preserve the post-only code-rendering contract and run its backend/frontend checks before adding new content blocks.
3. **Precis LMS:** continue from the Precis backend with course system, profile, and content work.
4. **Repository cleanup:** use the lifecycle policy and deletion manifest. Archive evidence before deleting duplicates.
5. **Documentation maintenance:** update this index and the relevant scope README whenever a plan is added, moved, superseded, or completed.

## Active plan highlights

| Plan | Status | Canonical path |
|---|:---:|---|
| Formint POS Professional Edition | Current / Phase 1 started | [`pos/formint-pos-professional-plan.md`](pos/formint-pos-professional-plan.md) |
| Formint edition chain | Active | [`editions/README.md`](editions/README.md) |
| Formint Cloud architecture (formint-cloud) | Planned / gate-based | [`pos/cloud-plan.md`](pos/cloud-plan.md) |
| Tauri plugin migration | Current migration | [`pos/tauri-plugins-enhancement-plan.md`](pos/tauri-plugins-enhancement-plan.md) |
| CMS Fusion migration (merged → Precis/Landing-Fusion) | Core complete; merged | [`cms-fusion/`](cms-fusion/) |
| LMS Fusion migration (now Precis) | Core complete; cleanup tracked | [`lms-fusion/migration-plan.md`](lms-fusion/migration-plan.md) |
| Landing-Fusion | Active | [`landing-fusion/`](landing-fusion/) |
| Repository migration cleanup | Partial / gate-based | [`repository/migration-cleanup-master.md`](repository/migration-cleanup-master.md) |
| django-fusion Tasks & MCP | Planned | [`django-fusion/django-fusion-tasks-mcp-plan.md`](django-fusion/django-fusion-tasks-mcp-plan.md) |
| django-fusion LLM & AI MCP Enhancement | Planned / companion | [`django-fusion/django-fusion-llm-mcp-enhancement-plan.md`](django-fusion/django-fusion-llm-mcp-enhancement-plan.md) |
| django-fusion Webpack Enhancement | Active | [`django-fusion/django-fusion-webpack-enhancement-plan.md`](django-fusion/django-fusion-webpack-enhancement-plan.md) |
| django-fusion Analyzer + Skeleton + Asset APIs | Planned | [`django-fusion/django-fusion-analyzer-skeleton-assets-plan.md`](django-fusion/django-fusion-analyzer-skeleton-assets-plan.md) |
| Legacy evidence | Archived | [`legacy/`](legacy/) |

## Recent renames & updates

| Change | Date | Notes |
|---|---|---|
| `formintB` → `formint-cloud` | 2026-08-09 | Cloud master directory and all references updated |
| `pos-cloud` → `formint-cloud` | 2026-08-09 | Package name in editions.md, AGENTS.md, docs |
| `lms-fusion` alias → Precis | Active | Compatibility alias preserved; canonical is `projects/precis/` |
| `cypercloud` → `syntara` | Active | Runtime alias preserved for external contracts |
| Tasks & MCP plan created | 2026-08-10 | Celery replacement, unified task API, MCP tools for bg tasks |
| LLM & AI MCP enhancement plan created | 2026-08-10 | Provider-neutral routing, model levels, caching, streaming, secure AI component workflows |
| Webpack enhancement + env configs | 2026-08-10 | Project-customizable webpack, landing-fusion/precis .env.example, project workspace configs |

| Analyzer + Skeleton + Asset APIs plan created | 2026-08-10 | Dynamic skeleton loading, per-page ordered components, component-level asset APIs, Astro minimal JS bridge |

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
├── pos/                      # Formint product and migration plans
├── editions/                 # Formint edition execution chain
├── cms-fusion/               # CMS Fusion plans (merged → Precis/Landing-Fusion)
├── lms-fusion/               # LMS Fusion plans (now Precis)
├── landing-fusion/           # Landing-Fusion plans
├── django-fusion/            # Shared framework plans
├── legacy/                   # Read-only historical evidence
├── migrated/                 # Migrated plan archives
├── document-lifecycle.md
├── deletion-manifest.md
├── marketing-claims.md
├── ASSETS_MIGRATION_INVENTORY.md
├── CODEBASE_AUDIT_AND_MIGRATION_PLAN.md
├── DJANGO_BOLT_FUSION_CASE_STUDY.md
└── FUSION_LMS_CMS_DESIGN.md
```

## Related documentation

- [`../README.md`](../README.md) — main documentation hub
- [`../recommendations.md`](../recommendations.md) — recommendations first
- [`../overview.md`](../overview.md) — repo overview with name migration reference
- [`../../AGENTS.md`](../../AGENTS.md) — repository-wide agent instructions
