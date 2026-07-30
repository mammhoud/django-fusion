# Structa Cloud — Plans Index

> **Last updated:** 2026-07-30 | **Branch:** `generic`

This directory consolidates all implementation plans for the Structa Cloud monorepo, organized by project. Each plan includes a status indicator showing whether the work is completed, in progress, or not started.

---

## Plan Status Summary

| Plan | Status | Completion | Remarks |
|------|:------:|:----------:|---------|
| **cepter-ai cleanup** (fusion) | ✅ Done | 100% | 0 imports across all 6 projects |
| **ctc-research ceptor-ai migration** | ✅ Done | 100% | ~90 files, phases 1-4 complete; project archived |
| **cypercloud ceptor-ai stubs** | ✅ Done | 100% | 6 AI/MCP/chat imports → local stubs |
| **cms-fusion migration** | ✅ Done | 100% | django-fusion + bolt + Next.js; 113 tests |
| **lms-fusion migration** | ✅ Done | 100% | django-fusion + bolt + Next.js; 113 tests |
| **fusion-assets-templates-cleanup** | ✅ Done | 100% | Phases 0-7 complete; Phase 8 deferred (deployment) |
| **django-fusion-webpack-integration** | ✅ Done | 100% | SCSS pipeline configured |
| **fix-deploy-webpack-cleanup** | ✅ Done | 100% | Deployment fixes applied |
| **legacy-cleanup | 🟡 Partial | 25% | Only ctc-research archived; 5 candidates remain
| **merge-cleanup | 🟡 Partial | 20% | File inventory done; actual cleanup not started
| **migration-cleanup-master | 🟡 Partial | 70% | Fusion migrations done; legacy sites + cleanup remain
| **worker-consolidation** | ⬜ Not Started | 0% | Worker task module consolidation |
| **cms-fusion frontend-enhancement-master** | ⬜ Not Started | 0% | UI enhancement umbrella plan |
| **cms-fusion flyonui-integration** | ⬜ Not Started | 0% | FlyonUI component integration |
| **cms-fusion component-pages** | ⬜ Not Started | 0% | Component page structure |
| **cms-fusion responsive-layout** | ⬜ Not Started | 0% | Responsive layout plan |
| **cms-fusion frontend-improvements** | ⬜ Not Started | 0% | Frontend improvements plan |
| **cms-fusion dashboard-migration** | ⬜ Not Started | 0% | Dashboard migration to fusion |
| **cms-fusion fragment-redux-integration** | ⬜ Not Started | 0% | Fragment Redux integration |
| **forge-pos plan** | 🟡 In Progress | 60% | P0-P1 complete; P2 KDS + P3 pending |
| **forge-pos enhancement** | 🟡 In Progress | 20% | Component reorg / Rust / SQL migration pending |
| **forge-pos UI-enhancement-master** | 🟡 In Progress | 35% | Sections 1, 3, 4, 5, 7, 9, 12 done; 2, 6, 8, 10, 11 pending |
| **pos-solo enhancement** | ⬜ Not Started | 0% | Solo edition enhancement |
| **pos cloud plan** | ⬜ Not Started | 0% | Cloud CRM architecture plan |
| **pos django-fusion-enhancements** | ⬜ Not Started | 0% | Django fusion enhancements |

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
├── pos/
│   ├── forge-pos-plan.md
│   ├── forge-pos-enhancement.md
│   ├── forge-pos-tasks-status.md
│   ├── forge-pos-ui-enhancement-master.md
│   ├── pos-solo-enhancement.md
│   ├── cloud-plan.md
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
| `#fusion` | Both CMS + LMS fusion projects |
| `#pos` | Point of Sale desktop app |
| `#forge-pos` | Forge POS edition (Tauri + Rust) |
| `#pos-solo` | POS Solo edition |
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

1. **cms-fusion frontend plans** — All 6 frontend plans (flyonui, component-pages, responsive-layout, frontend-enhancement-master, dashboard-migration, fragment-redux) are not started. These should be the top priority since the backend is fully migrated and tested.

2. **legacy cleanup** — Only ctc-research has been archived. The legacy-cleanup plan lists 5 candidate directories; none have been assessed for removal.

3. **forge-pos enhancement** — Active work in progress (recent commits show branding rename, Roles.tsx work). Complete the enhancement plan.

4. **worker consolidation** — The worker task module plan hasn't been started; it would simplify the deployment architecture.

---

## Related

- [`../CHANGELOG.md`](../CHANGELOG.md) — root changelog
- [`projects/cms-fusion/CHANGELOG.md`](../../projects/cms-fusion/CHANGELOG.md)
- [`projects/lms-fusion/CHANGELOG.md`](../../projects/lms-fusion/CHANGELOG.md)
- [`fusion-assets-templates-cleanup.md`](fusion-assets-templates-cleanup.md) — detailed Phase 0-8 spec

### Duplicate Task Resolution

- **Notes page / receipt templates**: Originally in both `forge-pos-plan.md` (P4) and `forge-pos-ui-enhancement-master.md` (Section 6). Superseded by the comprehensive plan in the UI master plan.
- **Theme toggle → select box**: `forge-pos-tasks-status.md` records the current sliding-knob implementation as complete; `forge-pos-ui-enhancement-master.md` plans the select-box redesign (Section 3). No conflict — sequential work.
- **FlyonUI integration**: Referenced in `cms-fusion/frontend-enhancement-master.md`, detailed in `cms-fusion/flyonui-integration.md`, and referenced by `forge-pos-tasks-status.md`. These are separate project integrations (CMS vs POS) — not duplicates.
