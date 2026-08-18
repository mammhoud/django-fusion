# 🗺️ Plans — Canonical Registry

> **Status:** Active registry
> **Last updated:** 2026-08-14
> **Branch:** `generic`

## Read this first

Start with [`../recommendations.md`](../recommendations.md) for the recommended work order. This directory is the single source of truth for engineering plans, implementation tasks, migrations, testing work, and deployment changes.

Do not create new plans in `docs/dev/plans/`, `docs/plans/migrated/`, or project-local directories. Active plans belong in the scope directory below. Completed plans are deleted once superseded; git history is the archive.

## Plan registry

| Scope | Entry point | What belongs here |
|---|---|---|
| Repository | [`repository/`](repository/) | Cross-project architecture, cleanup, migrations, and delivery |
| Active monorepo consolidation | [`repository/active-monorepo-consolidation-2026-08-14.md`](repository/active-monorepo-consolidation-2026-08-14.md) | Shared Dramatiq, LMS aggregate exclusion, Nx, dev-workspace, and AppFlowy |
| **Formint** (canonical) | [`editions/README.md`](editions/README.md) | Community → Standard → Pro → Cloud → Client → SDK execution chain — the main, latest product + edition plans |
| Landing-Fusion | [`precis-landing/`](precis-landing/) | Landing site architecture, content, and frontend work |
| Loop-CRM | [`loop-crm/merge-plan.md`](loop-crm/merge-plan.md) | Unified CRM + social scheduling (Twenty + Postiz merge) |
| Precis LMS + Syntara merge | [`repository/precis-syntara-merge.md`](repository/precis-syntara-merge.md) | Fold Syntara (Cypercloud AI chat) into the Precis LMS main site as Precis Assistant |
| Loop-CRM finance + workflows + integrations | [`loop-crm/formint-integration-finance-workflows.md`](loop-crm/formint-integration-finance-workflows.md) | Formint POS financial data → Loop-CRM finance module; workflow + connector expansion |
| Loop-CRM Wagtail landing + billing + webapp | [`loop-crm/wagtail-landing-plan.md`](loop-crm/wagtail-landing-plan.md) | Wagtail-managed public landing (precis-landing pattern), Stripe subscriptions, sidenav/guided UX, employees + report catalog, shared-locale i18n, license removal |
| django-fusion | [`django-fusion/`](django-fusion/) | Shared framework, tasks, MCP, asset/component work; submodule-owned plan |
| Lifecycle | [`document-lifecycle.md`](document-lifecycle.md) | Status, ownership, archive, deletion, and rollback policy |
| Claims | [`marketing-claims.md`](marketing-claims.md) | Evidence-backed product and marketing claims |
| Deletion register | [`deletion-manifest.md`](deletion-manifest.md) | Approval and rollback record for removals |
| External library plan | [`../../libs/django-fusion/docs/ENHANCEMENT_PLAN.md`](../../libs/django-fusion/docs/ENHANCEMENT_PLAN.md) | Maintained in the django-fusion submodule |

## Current recommendations

0. **Monorepo runtime baseline:** follow [`repository/active-monorepo-consolidation-2026-08-14.md`](repository/active-monorepo-consolidation-2026-08-14.md) before adding new worker or Coder services. Precis/LMS is explicit-only for maintenance and is excluded from aggregate deploy/check commands.

1. **Formints vertical slice:** Formints is the canonical product; continue the edition chain in the order shown in [`editions/README.md`](editions/README.md). `formint-cloud` is the current cloud master (renamed from `formintB`/`pos-cloud`), `formint-pro` is the merged Professional (from `pos-full` + `pos-solo`).
2. **Landing-Fusion quality:** preserve the post-only code-rendering contract and run its backend/frontend checks before adding new content blocks.
3. **Precis LMS:** continue from the Precis backend with course system, profile, and content work.
4. **Repository cleanup:** use the lifecycle policy and deletion manifest. Archive evidence before deleting duplicates.
5. **Documentation maintenance:** update this index and the relevant scope README whenever a plan is added, moved, superseded, or completed.

## Active plan highlights

| Plan | Status | Canonical path |
|---|:---:|---|
| Formint edition chain (canonical, latest) | Active | [`editions/README.md`](editions/README.md) |
| Landing-Fusion | Active | [`precis-landing/`](precis-landing/) |
| Loop-CRM merge | Foundation + tenancy/auth + tenant-scoped CRUD + channels + allauth + real screens shipped; AI hub & remaining adapters next | [`loop-crm/merge-plan.md`](loop-crm/merge-plan.md) |
| Precis LMS + Syntara merge | Planned | [`repository/precis-syntara-merge.md`](repository/precis-syntara-merge.md) |
| Active project closeout | Audit complete | [`repository/active-project-closeout-2026-08-11.md`](repository/active-project-closeout-2026-08-11.md) |
| Repository migration cleanup | Partial / gate-based | [`repository/migration-cleanup-master.md`](repository/migration-cleanup-master.md) |
| django-fusion Tasks & MCP | Baseline implemented; MCP/production hardening remaining | [`django-fusion/django-fusion-tasks-mcp-plan.md`](django-fusion/django-fusion-tasks-mcp-plan.md) |
| Active monorepo consolidation | In progress / baseline landed | [`repository/active-monorepo-consolidation-2026-08-14.md`](repository/active-monorepo-consolidation-2026-08-14.md) |
| django-fusion LLM & AI MCP Enhancement | Planned / companion | [`django-fusion/django-fusion-llm-mcp-enhancement-plan.md`](django-fusion/django-fusion-llm-mcp-enhancement-plan.md) |
| django-fusion Webpack Enhancement | Active | [`django-fusion/django-fusion-webpack-enhancement-plan.md`](django-fusion/django-fusion-webpack-enhancement-plan.md) |
| django-fusion Analyzer + Skeleton + Asset APIs | Planned | [`django-fusion/django-fusion-analyzer-skeleton-assets-plan.md`](django-fusion/django-fusion-analyzer-skeleton-assets-plan.md) |

## Recent renames & updates

| Change | Date | Notes |
|---|---|---|
| `formintB` → `formint-cloud` → `cloud` | 2026-08-09 | Cloud master directory renamed twice; canonical is now `projects/formints/formint-cloud/` |
| `pos-cloud` → `formint-cloud` → `cloud` | 2026-08-09 | Package name in editions.md, AGENTS.md, docs |
| `formintA`→`community`, `formint`→`pro`, `formintC`→`client`, `formint-standard`→`standard` | 2026-08-16 | POS editions renamed to short names under `projects/formints/` |
| `precis-lms` alias → Precis | Active | Compatibility alias preserved; canonical is `projects/precis/precis-lms/` |
| `precis` → `precis/precis-lms`, `precis-landing` → `precis/precis-landing`, `precis-ctc` → `precis/precis-ctc` | 2026-08-14 | LMS, marketing, and research sites regrouped under `projects/precis/`; runtime identities (`precis-lms`, `precis-landing`, `precis-ctc`) preserved |
| `osoul` → `components`, `rseal` → `site` | 2026-08-14 | Routable-component URL prefix `/osoul/` → `/components/`; `OSOUL_TEMPLATE_RENDERER` → `COMPONENT_TEMPLATE_RENDERER`; `django-rseal`/`rseal` app references → `domain.site` |
| Deleted retired plan dirs | 2026-08-14 | `pos/`, `migrated/`, `cms-fusion/`, `precis-lms/` removed — superseded by `editions/` and Precis/Landing-Fusion
| `cypercloud` → `syntara` | Active | Runtime alias preserved for external contracts |
| Tasks & MCP plan created | 2026-08-10 | Unified task API and MCP follow-up; shared Dramatiq baseline is now implemented |
| LLM & AI MCP enhancement plan created | 2026-08-10 | Provider-neutral routing, model levels, caching, streaming, secure AI component workflows |
| Webpack enhancement + env configs | 2026-08-10 | Project-customizable webpack, precis-landing/precis .env.example, project workspace configs |

| Analyzer + Skeleton + Asset APIs plan created | 2026-08-10 | Dynamic skeleton loading, per-page ordered components, component-level asset APIs, Astro minimal JS bridge |
| Loop-CRM Wagtail landing + billing + shared locale plan | 2026-08-18 | Proposed — Wagtail landing (precis-landing pattern), Stripe billing, sidenav/guided UX, employees/reports, `projects/assets/locale` consolidation |
| Loop-CRM tenancy + auth gating | 2026-08-14 | Workspace-scoped reads/mutations, login-gated pages/APIs, CSRF-protected kanban move, tenant-isolation tests |
| Loop-CRM CRUD + channels + allauth + real screens | 2026-08-14 | Tenant-scoped REST CRUD + msgspec schemas on both roads, Channels manager + Mastodon/Bluesky adapters, complete allauth flows, data-backed module tables, motion/design pass |
| Loop-CRM finance + workflows + integrations plan | 2026-08-14 | Formint↔Loop-CRM integration audit; POS financial-data ingestion into the finance module; workflow action/template expansion; webhooks/email/Slack/social/export connectors |

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
├── repository/               # Cross-repository plans (incl. Precis LMS + Syntara merge)
├── editions/                 # Formint edition execution chain
├── precis-landing/           # Landing-Fusion plans
├── loop-crm/                 # Loop-CRM merge plan (Twenty + Postiz)
├── django-fusion/            # Shared framework plans
├── document-lifecycle.md
├── deletion-manifest.md
├── marketing-claims.md
├── DJANGO_BOLT_FUSION_CASE_STUDY.md
└── THEME_DIRECTORY_STRATEGY.md
```

## Related documentation

- [`../README.md`](../README.md) — main documentation hub
- [`../recommendations.md`](../recommendations.md) — recommendations first
- [`../overview.md`](../overview.md) — repo overview with name migration reference
- [`../../AGENTS.md`](../../AGENTS.md) — repository-wide agent instructions
