# 🗺️ Plans — Canonical Registry

> **Status:** Active registry
> **Last updated:** 2026-09-17
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
| Precis Landing | [`precis-landing.md`](precis-landing.md) | Landing site architecture, content, and frontend work |
| Loop-CRM | [`loop-crm/merge-plan.md`](loop-crm/merge-plan.md) | Unified CRM + social scheduling (Twenty + Postiz merge) |
| Loop-CRM Wagtail landing + billing + webapp | [`loop-crm/wagtail-landing-plan.md`](loop-crm/wagtail-landing-plan.md) | Wagtail-managed public landing (precis-landing pattern), Stripe subscriptions, sidenav/guided UX, employees + report catalog, shared-locale i18n, license removal |
| **Workspace CRM program** | [`workspace-crm/README.md`](workspace-crm/README.md) | Six milestone plans extending Loop-CRM: schema-per-tenant domains + methodology, unified workspace session via proxy middleware, Unfold + Wagtail admin, landing subscriptions, per-project theme files, 20 landing samples, ThemeForest pack |
| django-fusion | [`django-fusion/`](django-fusion/) | Shared framework, tasks, MCP, asset/component work; submodule-owned plan |
| Blinko runtime | [`blinko/graph-enhancement-plan.md`](blinko/graph-enhancement-plan.md) · [`blinko/appearance-design-system-plan.md`](blinko/appearance-design-system-plan.md) | Anytype-aligned graph physics/inspection/filters plan + appearance token-system expansion (both IMPLEMENTED with review records 2026-09-17) |
| Config cascade (all Django products) | [`django-fusion/config-cascade-plan.md`](django-fusion/config-cascade-plan.md) | Layered config cascade (`config.project`), project `configs/` dirs (Precis Main/CTC, Loop-CRM, Syntara, Formint Cloud), base-URL priority resolution, Docker env cascade, static-files read/output/deploy reference |
| Startup docs enhancement | [`repository/startup-docs-enhancement-plan.md`](repository/startup-docs-enhancement-plan.md) | Progressive plan folding the 14-doc startup pack into `docs/startup/` — gap analysis, added/not-added remarks, phased linking |
| Lifecycle | [`document-lifecycle.md`](document-lifecycle.md) | Status, ownership, archive, deletion, and rollback policy |
| Claims | [`marketing-claims.md`](marketing-claims.md) | Evidence-backed product and marketing claims |
| Theme directory strategy | [`THEME_DIRECTORY_STRATEGY.md`](THEME_DIRECTORY_STRATEGY.md) | Repo-wide `theme/` layout + named design-variation contract |
| Deletion register | [`deletion-manifest.md`](deletion-manifest.md) | Approval and rollback record for removals |
| External library plan | [`../../libs/django-fusion/docs/ENHANCEMENT_PLAN.md`](../../libs/django-fusion/docs/ENHANCEMENT_PLAN.md) | Maintained in the django-fusion submodule |
| Precis Main Fusion render flow | [`repository/precis-main-render-flow.md`](repository/precis-main-render-flow.md) | Accepted local/production Compose, Fusion roads, and Nx command contract |
| Blinko Prisma → SurrealDB (M1 auth-first) — **RETIRED 2026-09-17** | [`repository/blinko-surrealdb-migration.md`](repository/blinko-surrealdb-migration.md) | Historical: vendored-checkout migration (`application/tools/blinko/blinko/`). That tree is gone — the product is a SurrealDB-native runtime at `application/tools/planing/runtime/`. Retained for the ID-mapping decision and engine notes |
| Blinko Prisma → SurrealDB (M2 content graph) — **RETIRED 2026-09-17** | [`repository/blinko-surrealdb-migration-m2.md`](repository/blinko-surrealdb-migration-m2.md) | Historical: notes/attachments/tags/comments adapters + router swaps. No Prisma content graph remains to mirror |
| Blinko Prisma → SurrealDB (M3 query engine) — **RETIRED 2026-09-17** | [`repository/blinko-surrealdb-migration-m3.md`](repository/blinko-surrealdb-migration-m3.md) | Historical: where-builder port + Prisma↔Surreal parity harness. Kept as a checklist of list surfaces |
| Blinko Prisma → SurrealDB (M4 final cutover) — **RETIRED 2026-09-17** | [`repository/blinko-surrealdb-migration-m4.md`](repository/blinko-surrealdb-migration-m4.md) | Superseded, never needed: the shipped runtime is SurrealDB-only, so there was no Prisma fallback to drop |

## Current recommendations

0. **Monorepo runtime baseline:** follow [`repository/active-monorepo-consolidation-2026-08-14.md`](repository/active-monorepo-consolidation-2026-08-14.md) before adding new worker or Coder services. Precis/LMS is explicit-only for maintenance and is excluded from aggregate deploy/check commands.

1. **Formints vertical slice:** Formints is the canonical product; continue the edition chain in the order shown in [`editions/README.md`](editions/README.md). `formint-cloud` is the current cloud master (renamed from `formintB`/`pos-cloud`), `formint-pro` is the merged Professional (from `pos-full` + `pos-solo`).
2. **Precis Landing quality:** preserve the post-only code-rendering contract and run its backend/frontend checks before adding new content blocks.
4. **Repository cleanup:** use the lifecycle policy and deletion manifest. Archive evidence before deleting duplicates.
5. **Documentation maintenance:** update this index and the relevant scope README whenever a plan is added, moved, superseded, or completed.

## Active plan highlights

| Plan | Status | Canonical path |
|---|:---:|---|
| Formint edition chain (canonical, latest) | Active | [`editions/README.md`](editions/README.md) |
| Formint cross-edition audit & reconciliation | Proposed — audit dated 2026-08-22 | [`editions/10-formint-audit-and-reconciliation-2026-08-22.md`](editions/10-formint-audit-and-reconciliation-2026-08-22.md) |
| Precis Landing | Active | [`precis-landing.md`](precis-landing.md) |
| Loop-CRM merge | Foundation + tenancy/auth + tenant-scoped CRUD + channels + allauth + real screens shipped; AI hub & remaining adapters next | [`loop-crm/merge-plan.md`](loop-crm/merge-plan.md) |
| Precis Dev multi-tenant platform | Proposed | [`repository/precis-dev-multitenant.md`](repository/precis-dev-multitenant.md) |
| Workspace CRM program (M1–M6) | Proposed | [`workspace-crm/README.md`](workspace-crm/README.md) |
| CTC Research publish | Active | [`repository/ctc-research-publish-2026-08-18.md`](repository/ctc-research-publish-2026-08-18.md) |
| Precis Dev multi-tenant | [`repository/precis-dev-multitenant.md`](repository/precis-dev-multitenant.md) | Schema-per-tenant via django-tenants, role-based auth (LMS/CRM manager), per-tenant Wagtail CMS landing pages, Dramatiq lifecycle workflows |
| CTC Research MCP + django-fusion Integration | Proposed | [`repository/precis-ctc-mcp-django-fusion-integration.md`](repository/precis-ctc-mcp-django-fusion-integration.md) |
| CTC Research cross-module workflows | Proposed | [`repository/precis-ctc-workflows.md`](repository/precis-ctc-workflows.md) |
| Active project closeout | Audit complete | [`repository/active-project-closeout-2026-08-11.md`](repository/active-project-closeout-2026-08-11.md) |
| Repository migration cleanup | Partial / gate-based | [`repository/migration-cleanup-master.md`](repository/migration-cleanup-master.md) |
| django-fusion Tasks & MCP | Baseline implemented; MCP/production hardening remaining | [`django-fusion/django-fusion-tasks-mcp-plan.md`](django-fusion/django-fusion-tasks-mcp-plan.md) |
| Active monorepo consolidation | In progress / baseline landed | [`repository/active-monorepo-consolidation-2026-08-14.md`](repository/active-monorepo-consolidation-2026-08-14.md) |
| django-fusion LLM & AI MCP Enhancement | Planned / companion | [`django-fusion/django-fusion-llm-mcp-enhancement-plan.md`](django-fusion/django-fusion-llm-mcp-enhancement-plan.md) |
| django-fusion Webpack Enhancement | Active | [`django-fusion/django-fusion-webpack-enhancement-plan.md`](django-fusion/django-fusion-webpack-enhancement-plan.md) |
| django-fusion Analyzer + Skeleton + Asset APIs | Planned | [`django-fusion/django-fusion-analyzer-skeleton-assets-plan.md`](django-fusion/django-fusion-analyzer-skeleton-assets-plan.md) |
| Config cascade + project configs dirs | Active — baseline implemented | [`django-fusion/config-cascade-plan.md`](django-fusion/config-cascade-plan.md) |
| Startup docs enhancement | Active — P1–P3 landed | [`repository/startup-docs-enhancement-plan.md`](repository/startup-docs-enhancement-plan.md) |
| Precis Main Fusion render flow | Accepted — project Makefile, Nx bridge, and HTML reference added 2026-09-15 | [`repository/precis-main-render-flow.md`](repository/precis-main-render-flow.md) |
| Blinko SurrealDB workspace enhancements | Implemented — Phase 1, Phase 2 closeout (retention/purge), first Phase 4 slices (transactions, query telemetry); live queries deferred with reason. Verified 2026-09-17 | [`repository/blinko-surrealdb-enhancements.md`](repository/blinko-surrealdb-enhancements.md) |
| Blinko graph G1–G3 (force/inspect/filters/timeline/heatmap) | Implemented — review 2026-09-17 | [`blinko/graph-enhancement-plan.md`](blinko/graph-enhancement-plan.md) |
| Blinko appearance: Tier 1 + variants/element-styles/presets/categorized panel | Implemented — review 2026-09-17 | [`blinko/appearance-design-system-plan.md`](blinko/appearance-design-system-plan.md) |
| Loop-CRM Tauri multi-platform (desktop/cloud/mobile) | DRAFT — review notes added 2026-09-17 | [`loop-crm/tauri-multi-platform-plan.md`](loop-crm/tauri-multi-platform-plan.md) |
| SurrealDB migration (Formints + Loop CRM) | DRAFT — review notes added 2026-09-17 | [`loop-crm/surrealdb-migration-plan.md`](loop-crm/surrealdb-migration-plan.md) |
| Blinko Prisma → SurrealDB (auth-first) | **Retired 2026-09-17** — vendored tree removed; superseded by the enhancements plan | [`repository/blinko-surrealdb-migration.md`](repository/blinko-surrealdb-migration.md) |
| Blinko Prisma → SurrealDB (content graph) | **Retired 2026-09-17** — was Implemented (M2 commits `b919d921`+`b8c3de01`) in the vendored tree | [`repository/blinko-surrealdb-migration-m2.md`](repository/blinko-surrealdb-migration-m2.md) |
| Blinko Prisma → SurrealDB (query engine) | **Retired 2026-09-17** — was Implemented (parity harness green, `586b5bf3`) | [`repository/blinko-surrealdb-migration-m3.md`](repository/blinko-surrealdb-migration-m3.md) |
| Blinko Prisma → SurrealDB (final cutover) | **Retired 2026-09-17** — never needed; runtime is SurrealDB-only | [`repository/blinko-surrealdb-migration-m4.md`](repository/blinko-surrealdb-migration-m4.md) |

## External proposal intake (2026-09-17)

<!-- AI-generated: review needed -->
A consolidated platform proposal (roadmap phases, django-fusion view/mixin
taxonomy, Astro/React integration, CRM/POS/LMS feature lists, AI agents,
sprints) was reviewed **without creating new plan files** — every item maps to
existing owning plans:

| Proposal item | Owning plan / record |
|---|---|
| django-fusion BaseView/SmartView/ProxyView/DualView, mixins, component registry | [`django-fusion/django-fusion-enhancements.md`](django-fusion/django-fusion-enhancements.md) (ModelViewset/FragmentComponent/SearchableViewMixin already shipped; new view taxonomy = candidate items 1.x) + [`comp-htmx-fusionproxy-analysis.md`](django-fusion/comp-htmx-fusionproxy-analysis.md) |
| Django Ninja / JWT / OpenAPI | [`django-fusion/django-fusion-llm-mcp-enhancement-plan.md`](django-fusion/django-fusion-llm-mcp-enhancement-plan.md) companion scope; note the repo's dual-render contract (HTML/HTMX fragment/JSON) predates Ninja — evaluate only for the data-API road |
| Astro + HTMX + React-island integration | Product-level, already realized in `projects/structa.cloud/frontend` (Astro+HTMX+Alpine) and `projects/loop-crm/frontend` (React islands + HTMX) — see [`repository/precis-main-render-flow.md`](repository/precis-main-render-flow.md) |
| CRM leads/pipelines/finance/workflows | [`loop-crm/merge-plan.md`](loop-crm/merge-plan.md) + finance/workflow milestones in [`../../agenda/feature-tracking/loop-crm.md`](../agenda/feature-tracking/loop-crm.md) |
| POS features (restaurant/retail/branches/accounting) | Formints editions — `projects/formints/AGENTS.md`, [`django-fusion/django-fusion-enhancements.md`](django-fusion/django-fusion-enhancements.md) for sync/viewset gaps |
| LMS courses/certificates/tracking | structa.cloud (unified Precis) product scope — [`precis-landing.md`](precis-landing.md) + product docs |
| AI agents (coding/docs/CRM/LMS) | [`django-fusion/django-fusion-llm-mcp-enhancement-plan.md`](django-fusion/django-fusion-llm-mcp-enhancement-plan.md) + `.agents/mcp/` prompt catalog |
| Roadmap phases 4–5 (SaaS tenancy, billing, marketplace) | Not yet owned by any plan — flagged as candidate future scope for [`workspace-crm/README.md`](workspace-crm/README.md) (tenancy/billing already in scope there) and a potential future marketplace ADR; intentionally **no new plan created** per review instruction |
| Sprint 01–03 breakdown | Owned by sprint tracking, not plans/ — record in [`../../agenda/task-tracking.md`](../agenda/task-tracking.md) if adopted |

**Verdict:** proposal adds a useful *view/mixin taxonomy* and *marketplace
phase* vocabulary, but no new owning plan is warranted today; the two DRAFT
Loop-CRM architecture plans above already own the multi-platform +
datastore future.

## Recent renames & updates

| Change | Date | Notes |
|---|---|---|
| `precis-main` → `structa.cloud` | 2026-09-17 | Moved to top-level `projects/structa.cloud/`; `WEBSITE=precis-main` stays a legacy alias; runtime identity (`precis-main-*` containers, `DJANGO_SITE`) preserved for volume/deploy validity |
| `formintB` → `formint-cloud` → `cloud` | 2026-08-09 | Cloud master directory renamed twice; canonical is now `projects/formints/formint-cloud/` |
| `pos-cloud` → `formint-cloud` → `cloud` | 2026-08-09 | Package name in editions.md, AGENTS.md, docs |
| `formintA`→`community`, `formint`→`pro`, `formintC`→`client`, `formint-standard`→`standard` | 2026-08-16 | POS editions renamed to short names under `projects/formints/` |
| `precis-lms` alias → Precis | Active | Compatibility alias preserved; canonical is `projects/structa.cloud/` |
| `precis` → `structa.cloud`, `precis-landing` → `precis/precis-landing`, `precis-ctc` → `precis/precis-ctc` | 2026-08-14 | LMS, marketing, and research sites regrouped under `projects/precis/`; runtime identities (`precis-lms`, `precis-landing`, `precis-ctc`) preserved |
| `osoul` → `components`, `rseal` → `site` | 2026-08-14 | Routable-component URL prefix `/osoul/` → `/components/`; `OSOUL_TEMPLATE_RENDERER` → `COMPONENT_TEMPLATE_RENDERER`; `django-rseal`/`rseal` app references → `domain.site` |
| Deleted retired plan dirs | 2026-08-14 | `pos/`, `migrated/`, `cms-fusion/`, `precis-lms/` removed — superseded by `editions/` and Precis/Precis Landing
| `cypercloud` → `syntara` | Active | Runtime alias preserved for external contracts |
| Tasks & MCP plan created | 2026-08-10 | Unified task API and MCP follow-up; shared Dramatiq baseline is now implemented |
| LLM & AI MCP enhancement plan created | 2026-08-10 | Provider-neutral routing, model levels, caching, streaming, secure AI component workflows |
| Webpack enhancement + env configs | 2026-08-10 | Project-customizable webpack, precis-landing/precis .env.example, project workspace configs |

| Analyzer + Skeleton + Asset APIs plan created | 2026-08-10 | Dynamic skeleton loading, per-page ordered components, component-level asset APIs, Astro minimal JS bridge |
| Loop-CRM Wagtail landing + billing + shared locale plan | 2026-08-18 | Proposed — Wagtail landing (precis-landing pattern), Stripe billing, sidenav/guided UX, employees/reports, `projects/assets/locale` consolidation |
| Workspace CRM program created | 2026-09-12 | Proposed — 6 milestone plans under `workspace-crm/`: multi-tenant domain schemas, workspace session + proxy middleware, Unfold/Wagtail admin + landing subscriptions, theme files + components, 20-sample landing library, theme guidelines + ThemeForest pack. Extends Loop-CRM; reuses `precis-dev-multitenant` and `THEME_DIRECTORY_STRATEGY` |
| Config cascade plan | 2026-08-20 | Active — `django_fusion.config.project` module (base-URL priority), `configs/` dirs for Precis Main/CTC, Loop-CRM, Syntara, Formint Cloud; frontend wire (`make config-front`), Docker override, `make config-show`/`config-check`, static-files read/output/deploy reference |
| Startup docs enhancement plan created | 2026-08-20 | Analyzed the 14-doc startup pack vs the monorepo; added `startup/company-profile.md`, `startup/product-profiles.md`, `startup/revenue-model.md`, `startup/presentation.md`, module price book (`PRICING.md` §6); declined the pack's fictional `fusion.*` django-fusion package guide |
| CTC Research publish plan | 2026-08-18 | Active — full content/component audit, es/sv/pt-br catalogs, media/bundles proxy, email parity + test, `make redeploy`, Nx, cross-module workflows |
| CTC Research workflow plan | 2026-08-18 | Proposed — 16 cross-module workflows with Dramatiq as the single publishing, refresh, analytics, and attribution boundary |
| Loop-CRM tenancy + auth gating | 2026-08-14 | Workspace-scoped reads/mutations, login-gated pages/APIs, CSRF-protected kanban move, tenant-isolation tests |
| Loop-CRM CRUD + channels + allauth + real screens | 2026-08-14 | Tenant-scoped REST CRUD + msgspec schemas on both roads, Channels manager + Mastodon/Bluesky adapters, complete allauth flows, data-backed module tables, motion/design pass |
| Loop-CRM finance + workflows + integrations | 2026-08-14 → completed 2026-09-05 | Formint↔Loop-CRM finance ingestion, workflow expansion, and connectors **completed** — recorded as a milestone in [`docs/agenda/feature-tracking/loop-crm.md`](../agenda/feature-tracking/loop-crm.md); the plan itself was deleted (git history is the archive) |

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
├── editions/                 # Formint edition execution chain
├── loop-crm/                 # Loop-CRM merge plan (Twenty + Postiz)
├── workspace-crm/            # Workspace CRM program (M1–M6: tenancy, session, admin, themes, samples, publish)
├── django-fusion/            # Shared framework plans
├── precis-landing.md         # Precis Landing plans (was `precis-landing/`)
├── document-lifecycle.md
├── deletion-manifest.md
├── marketing-claims.md
├── DJANGO_BOLT_FUSION_CASE_STUDY.md
└── THEME_DIRECTORY_STRATEGY.md

> `legacy-archive/` (dead-code audit, deployment-reports, dev-notes) was
> deleted 2026-08-19 — see [`deletion-manifest.md`](deletion-manifest.md) DOC-0024.
```

## Related documentation

- [`../README.md`](../README.md) — main documentation hub
- [`../recommendations.md`](../recommendations.md) — recommendations first
- [`../overview.md`](../overview.md) — repo overview with name migration reference
- [`../../AGENTS.md`](../../AGENTS.md) — repository-wide agent instructions
