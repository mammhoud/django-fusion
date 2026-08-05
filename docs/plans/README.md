# Structa Cloud — Plans Index

> **Last updated:** 2026-08-04 | **Branch:** `generic`
> **Lifecycle policy:** [`document-lifecycle.md`](document-lifecycle.md)
> **Marketing claims register:** [`marketing-claims.md`](marketing-claims.md)

All active, migrated, and historical repository plans live below this directory.
`docs/Anytype/plans/` remains a separate Anytype knowledge graph and is not
part of this index.

This directory consolidates all implementation plans for the Structa Cloud monorepo, organized by project. Each plan includes a status indicator showing whether the work is completed, in progress, or not started.

---

## Plan Status Summary

| Plan | Status | Completion | Remarks |
|------|:------:|:----------:|---------|
| **cepter-ai cleanup** (fusion) | ✅ Done | 100% | 0 imports across all 6 projects |
| **ctc-research ceptor-ai migration** | ✅ Done | 100% | ~90 files, phases 1-4 complete; project archived |
| **cypercloud ceptor-ai stubs** | ✅ Done | 100% | 6 AI/MCP/chat imports → local stubs |
| **cms-fusion migration** | ✅ Done | 100% | django-fusion + project-owned API + Next.js; 113 tests |
| **lms-fusion migration** | ✅ Done | 100% | django-fusion + project-owned API + Next.js; 113 tests |
| **landing-fusion migration** | 🟡 In Progress | 70% | Astro + AHA frontend (Phases 0-1 + dark mode) + Django/Wagtail backend; blog/auth/Docker pending |
| **fusion-assets-templates-cleanup** | ✅ Done | 100% | Phases 0-7 complete; Phase 8 deferred (deployment) |
| **django-fusion-webpack-integration** | ✅ Done | 100% | SCSS pipeline configured |
| **fix-deploy-webpack-cleanup** | ✅ Done | 100% | Deployment fixes applied |
| **legacy-cleanup** | 🟡 Partial | 25% | Only ctc-research archived; 5 candidates remain |
| **merge-cleanup** | 🟡 Partial | 20% | File inventory done; actual cleanup not started |
| **migration-cleanup-master** | 🟡 Partial | 70% | Fusion migrations done; legacy sites + cleanup remain |
| **worker-consolidation** | ⬜ Not Started | 0% | Worker task module consolidation |
| **cms-fusion frontend-enhancement-master** | ⬜ Not Started | 0% | UI enhancement umbrella plan |
| **cms-fusion flyonui-integration** | ⬜ Not Started | 0% | FlyonUI component integration |
| **cms-fusion component-pages** | ⬜ Not Started | 0% | Component page structure |
| **cms-fusion responsive-layout** | ⬜ Not Started | 0% | Responsive layout plan |
| **cms-fusion frontend-improvements** | ⬜ Not Started | 0% | Frontend improvements plan |
| **cms-fusion dashboard-migration** | ⬜ Not Started | 0% | Dashboard migration to fusion |
| **cms-fusion fragment-redux-integration** | ⬜ Not Started | 0% | Fragment Redux integration |
| **Forge POS parity plan** | 🟡 Migration source | Gate-based | Keep until Formint transfer evidence passes; do not market as a product |
| **Forge POS enhancement/UI plans** | 🗄️ Archived | Completed source | Retain in `legacy/pos/` as rollback and design evidence |
| **Formint POS Professional Edition** | 🟡 Current | Phase 1 started | Canonical product plan; foundation created at `projects/pos/formint-pos/`; legacy POS sources preserved |
| **pos-solo enhancement** | 🗄️ Historical | — | Working file removed; migration evidence is preserved by the Formint/Forge plans and deletion manifest |
| **pos cloud plan** | 🟡 Planned | Gate-based | Cloud-only transport and multi-branch architecture |
| **pos django-fusion-enhancements** | ⬜ Not Started | 0% | Django-fusion component and sync enhancements |

---

## Directory Layout

```
docs/plans/
├── README.md                              # This file — plan index with status
├── ceptor-ai-cleanup.md                   # Remove ceptor-ai from fusion projects
├── ctc-research-ceptor-ai-migration.md    # ~80 file migration plan
├── django-fusion-webpack-integration-plan.md
├── fix-deploy-webpack-cleanup.md
├── worker-consolidation.md
├── migration-cleanup-master.md
├── fusion-assets-templates-cleanup.md
├── cms-fusion/
│   ├── migration-plan.md
│   ├── dashboard-migration.md
│   ├── fragment-redux-integration.md
│   ├── frontend-improvements.md
│   ├── component-pages.md
│   ├── flyonui-integration.md
│   ├── responsive-layout.md
│   └── frontend-enhancement-master.md
├── lms-fusion/
│   └── migration-plan.md
├── landing-fusion/
│   ├── LANDING_FUSION_PLAN.md     # Build plan + backend↔frontend mapping
│   └── SHADCNBLOCKS_THEME.md      # Extracted shadcnblocks theme styles
├── pos/
│   ├── forge-pos-plan.md                  # Forge parity source and retirement gates
│   ├── (archived Forge status/design plans live in ../legacy/pos/)
│   ├── formint-pos-professional-plan.md  # Canonical Professional Edition plan
│   ├── pos-solo-enhancement.md           # Historical source removed; see deletion manifest
│   ├── tauri-plugins-enhancement-plan.md # Formint desktop plugin migration
│   ├── cloud-plan.md                     # Cloud-only transport and sync
│   └── django-fusion-enhancements.md
└── legacy/
    ├── legacy-cleanup.md
    └── merge-cleanup.md
```

---

## Recent Completed Work (July 30, 2026)

### ceptor-ai migration (all projects)
- **ctc-research**: 44 ceptor_ai imports → 0. Local models created for Company, Contact, Organization, Team, Workspace, middleware, services. Project archived to `archives/ctc-research/`.
- **cms-fusion / lms-fusion**: Already clean. Newsletter native from start.
- **cypercloud**: 6 AI/MCP/chat imports → `ceptor_stubs.py`.

### Enhanced testing (cms-fusion + lms-fusion)
- 113 tests each, 0 failures
- 27 new enhanced tests: CORS, HTMX, error handling, trailing slashes, branding, Content-Type

### Documentation
- 25 plan files consolidated to `docs/plans/`
- Per-project CHANGELOGs: `cms-fusion/CHANGELOG.md`, `lms-fusion/CHANGELOG.md`
- Root `CHANGELOG.md` updated

---

## Legend

| Symbol | Meaning |
|:------:|---------|
| ✅ | Complete |
| 🟡 | In Progress |
| ⬜ | Not Started |
| ❌ | Blocked |

### Tag Reference

Each plan file is tagged at the top with relevant project tags. Use these to filter/search plans:

| Tag | Scope |
|-----|-------|
| `#cms-fusion` | CMS Fusion project (Next.js frontend) |
| `#lms-fusion` | LMS Fusion project (Next.js frontend) |
| `#landing` | Landing site (landing-fusion) |
| `#astro` | Astro framework work |
| `#aha-stack` | Astro + HTMX + Alpine.js architecture |
| `#fusion` | Both CMS + LMS fusion projects |
| `#pos` | Point of Sale desktop app |
| `#forge-pos` | Forge POS edition (Tauri + Rust) |
| `#pos-solo` | POS Solo edition / migration source |
| `#formint-pos` | Formint POS canonical product |
| `#professional` | Professional commercial edition |
| `#tauri` | Tauri 2 desktop framework |
| `#frontend` | Frontend/React/TypeScript work |
| `#backend` | Backend/Django/Python work |
| `#ui` | UI/UX design and layout |
| `#enhancement` | Feature enhancement/improvement |
| `#planning` | High-level planning/roadmap |
| `#tasks` | Task tracking/status |
| `#cleanup` | Legacy cleanup/removal |
| `#migration` | Code/data migration |
| `#ceptor-ai` | ceptor-ai library removal |
| `#ctc-research` | CTC Research site |
| `#django-fusion` | django-fusion component framework |
| `#webpack` | Webpack build configuration |
| `#assets` | Static assets and templates |
| `#templates` | Django/Next.js templates |
| `#deploy` | Deployment and CI/CD |
| `#fix` | Bug fixes and hotfixes |
| `#worker` | Background worker/task system |
| `#celery` | Celery task queue |
| `#cloud` | Cloud CRM/infrastructure |
| `#infrastructure` | Docker, proxy, networking |
| `#legacy` | Legacy code removal |
| `#general` | Cross-cutting concerns |

---

## Recommendations (Next Priority)

1. **Formint POS Professional Edition** — Use [`pos/formint-pos-professional-plan.md`](pos/formint-pos-professional-plan.md) as the canonical scope. The Phase 1 boundary is [`projects/pos/formint-pos/`](../../projects/pos/formint-pos/); the verified backup record is [`pos/formint-backup-20260804.md`](pos/formint-backup-20260804.md). Start with the branch → order → KDS → sync → report vertical slice and keep POS Solo/Full available until parity gates pass.

2. **cms-fusion frontend plans** — All 6 frontend plans (flyonui, component-pages, responsive-layout, frontend-enhancement-master, dashboard-migration, fragment-redux) are not started. These should be prioritized independently of the POS consolidation.

3. **legacy cleanup** — Only ctc-research has been archived. The legacy-cleanup plan lists 5 candidate directories; none have been assessed for removal.

4. **forge-pos enhancement** — Port reusable UI, KDS, native I/O, and testing patterns into Formint; do not copy Forge's data layer as a second authority.

5. **worker consolidation** — The worker task module plan has not started and may simplify cloud sync and scheduled operations.

---

## Lifecycle and marketing

- [`document-lifecycle.md`](document-lifecycle.md) — Current/archive/delete/rollback policy
- [`marketing-claims.md`](marketing-claims.md) — Marketing evidence register

## Related

- [`../../CHANGELOG.md`](../../CHANGELOG.md) — root changelog
- [`../../projects/cms-fusion/CHANGELOG.md`](../../projects/cms-fusion/CHANGELOG.md)
- [`../../projects/lms-fusion/CHANGELOG.md`](../../projects/lms-fusion/CHANGELOG.md)
- [`django-fusion/fusion-assets-templates-cleanup.md`](django-fusion/fusion-assets-templates-cleanup.md) — detailed Phase 0-8 spec

### Duplicate Task Resolution

- **Notes, receipt templates, KDS, loyalty, combo/composite items, modifiers, and extras**: Their implementation source may exist in archived Forge/Solo material, but Formint Professional is now the canonical owner. They must pass Formint implementation and compatibility gates before any source removal.
- **Forge design/status evidence**: Archived copies live in [`legacy/pos/`](legacy/pos/); Formint is the current product owner.
- **FlyonUI integration**: CMS and POS references are separate concerns; confirm ownership before merging or deleting either plan.
