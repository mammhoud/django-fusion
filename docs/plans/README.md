# 🗺️ Plans — Canonical Registry

> **Status:** Active registry
> **Last updated:** 2026-08-14
> **Branch:** `generic`

## Read this first

Start with [`../recommendations.md`](../recommendations.md) for the recommended work order. This directory is the single source of truth for engineering plans, implementation tasks, migrations, testing work, and deployment changes.

Do not create new plans in `docs/dev/plans/`, `docs/plans/migrated/`, or project-local directories. Active plans belong in the scope directory below. Historical material belongs in `legacy/` and must not be treated as current scope.

## Plan registry

| Scope | Entry point | What belongs here |
|---|---|---|
| Repository | [`repository/`](repository/) | Cross-project architecture, cleanup, migrations, and delivery |
| Active monorepo consolidation | [`repository/active-monorepo-consolidation-2026-08-14.md`](repository/active-monorepo-consolidation-2026-08-14.md) | Shared Dramatiq, LMS aggregate exclusion, Nx, dev-workspace, and AppFlowy |
| **Formint** (canonical) | [`editions/README.md`](editions/README.md) | Community → Standard → Pro → Cloud → Client → SDK execution chain — the main, latest product + edition plans |
| Formint/POS (legacy index) | [`pos/README.md`](pos/README.md) | Retired `projects/pos/` product scope, cloud, and migration evidence; superseded by Formints |
| CMS Fusion | [`cms-fusion/`](cms-fusion/) | Superseded migration evidence; active work is in Precis/Landing-Fusion |
| LMS Fusion | [`lms-fusion/`](lms-fusion/) | Superseded migration evidence; active LMS work is in Precis |
| Landing-Fusion | [`landing-fusion/`](landing-fusion/) | Landing site architecture, content, and frontend work |
| Loop-CRM | [`loop-crm/merge-plan.md`](loop-crm/merge-plan.md) | Unified CRM + social scheduling (Twenty + Postiz merge) |
| django-fusion | [`django-fusion/`](django-fusion/) | Shared framework, tasks, MCP, asset/component work; submodule-owned plan |
| Formint Cloud | [`pos/cloud-plan.md`](pos/cloud-plan.md) | Cloud master: Channels, WebSocket sync, Bolt dashboard, Unfold admin |
| Lifecycle | [`document-lifecycle.md`](document-lifecycle.md) | Status, ownership, archive, deletion, and rollback policy |
| Claims | [`marketing-claims.md`](marketing-claims.md) | Evidence-backed product and marketing claims |
| Deletion register | [`deletion-manifest.md`](deletion-manifest.md) | Approval and rollback record for removals |
| Historical evidence | [`legacy/`](legacy/) | Read-only completed plans, snapshots, and migration evidence |
| External library plan | [`../../libs/django-fusion/docs/ENHANCEMENT_PLAN.md`](../../libs/django-fusion/docs/ENHANCEMENT_PLAN.md) | Maintained in the django-fusion submodule |

## Current recommendations

0. **Monorepo runtime baseline:** follow [`repository/active-monorepo-consolidation-2026-08-14.md`](repository/active-monorepo-consolidation-2026-08-14.md) before adding new worker or Coder services. Precis/LMS is explicit-only for maintenance and is excluded from aggregate deploy/check commands.

1. **Formints vertical slice:** Formints is the canonical product; continue the edition chain in the order shown in [`editions/README.md`](editions/README.md). `formint-cloud` is the current cloud master (renamed from `formintB`/`pos-cloud`), `formint-pro` is the merged Professional (from `pos-full` + `pos-solo`), and the legacy `projects/pos/` plans are migration evidence only.
2. **Landing-Fusion quality:** preserve the post-only code-rendering contract and run its backend/frontend checks before adding new content blocks.
3. **Precis LMS:** continue from the Precis backend with course system, profile, and content work.
4. **Repository cleanup:** use the lifecycle policy and deletion manifest. Archive evidence before deleting duplicates.
5. **Documentation maintenance:** update this index and the relevant scope README whenever a plan is added, moved, superseded, or completed.

## Active plan highlights

| Plan | Status | Canonical path |
|---|:---:|---|
| Formint edition chain (canonical, latest) | Active | [`editions/README.md`](editions/README.md) |
| Formint POS Professional Edition (legacy scope) | Superseded → editions 01–08 | [`pos/formint-pos-professional-plan.md`](pos/formint-pos-professional-plan.md) |
| Formint Cloud architecture (formint-cloud) | Planned / gate-based | [`pos/cloud-plan.md`](pos/cloud-plan.md) |
| Tauri plugin migration | Current migration | [`pos/tauri-plugins-enhancement-plan.md`](pos/tauri-plugins-enhancement-plan.md) |
| CMS Fusion migration (merged → Precis/Landing-Fusion) | Superseded; evidence retained | [`cms-fusion/migration-plan.md`](cms-fusion/migration-plan.md) |
| LMS Fusion migration (now Precis) | Superseded; evidence retained | [`lms-fusion/migration-plan.md`](lms-fusion/migration-plan.md) |
| Landing-Fusion | Active | [`landing-fusion/`](landing-fusion/) |
| Loop-CRM merge | Foundation + tenancy/auth + tenant-scoped CRUD + channels + allauth + real screens shipped; AI hub & remaining adapters next | [`loop-crm/merge-plan.md`](loop-crm/merge-plan.md) |
| Active project closeout | Audit complete | [`repository/active-project-closeout-2026-08-11.md`](repository/active-project-closeout-2026-08-11.md) |
| Repository migration cleanup | Partial / gate-based | [`repository/migration-cleanup-master.md`](repository/migration-cleanup-master.md) |
| django-fusion Tasks & MCP | Baseline implemented; MCP/production hardening remaining | [`django-fusion/django-fusion-tasks-mcp-plan.md`](django-fusion/django-fusion-tasks-mcp-plan.md) |
| Active monorepo consolidation | In progress / baseline landed | [`repository/active-monorepo-consolidation-2026-08-14.md`](repository/active-monorepo-consolidation-2026-08-14.md) |
| django-fusion LLM & AI MCP Enhancement | Planned / companion | [`django-fusion/django-fusion-llm-mcp-enhancement-plan.md`](django-fusion/django-fusion-llm-mcp-enhancement-plan.md) |
| django-fusion Webpack Enhancement | Active | [`django-fusion/django-fusion-webpack-enhancement-plan.md`](django-fusion/django-fusion-webpack-enhancement-plan.md) |
| django-fusion Analyzer + Skeleton + Asset APIs | Planned | [`django-fusion/django-fusion-analyzer-skeleton-assets-plan.md`](django-fusion/django-fusion-analyzer-skeleton-assets-plan.md) |
| Legacy evidence | Archived | [`legacy/`](legacy/) |

## Recent renames & updates

| Change | Date | Notes |
|---|---|---|
| `formintB` → `formint-cloud` | 2026-08-09 | Cloud master directory and all references updated |
| `pos-cloud` → `formint-cloud` | 2026-08-09 | Package name in editions.md, AGENTS.md, docs |
| `lms-fusion` alias → Precis | Active | Compatibility alias preserved; canonical is `projects/precis/main/` |
| `precis` → `precis/main`, `landing-fusion` → `precis/landi`, `ctc-research` → `precis/ctc-research` | 2026-08-14 | LMS, marketing, and research sites regrouped under `projects/precis/`; runtime identities (`lms-fusion`, `landing-fusion`, `ctc-research`) preserved |
| `osoul` → `components`, `rseal` → `site` | 2026-08-14 | Routable-component URL prefix `/osoul/` → `/components/`; `OSOUL_TEMPLATE_RENDERER` → `COMPONENT_TEMPLATE_RENDERER`; `django-rseal`/`rseal` app references → `domain.site` |
| `cypercloud` → `syntara` | Active | Runtime alias preserved for external contracts |
| Tasks & MCP plan created | 2026-08-10 | Unified task API and MCP follow-up; shared Dramatiq baseline is now implemented |
| LLM & AI MCP enhancement plan created | 2026-08-10 | Provider-neutral routing, model levels, caching, streaming, secure AI component workflows |
| Webpack enhancement + env configs | 2026-08-10 | Project-customizable webpack, landing-fusion/precis .env.example, project workspace configs |

| Analyzer + Skeleton + Asset APIs plan created | 2026-08-10 | Dynamic skeleton loading, per-page ordered components, component-level asset APIs, Astro minimal JS bridge |
| Loop-CRM tenancy + auth gating | 2026-08-14 | Workspace-scoped reads/mutations, login-gated pages/APIs, CSRF-protected kanban move, tenant-isolation tests |
| Loop-CRM CRUD + channels + allauth + real screens | 2026-08-14 | Tenant-scoped REST CRUD + msgspec schemas on both roads, Channels manager + Mastodon/Bluesky adapters, complete allauth flows, data-backed module tables, motion/design pass |

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
├── loop-crm/                 # Loop-CRM merge plan (Twenty + Postiz)
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
