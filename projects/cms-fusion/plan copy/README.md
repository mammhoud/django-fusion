# LMS — Master Plan Index

> **Last updated:** 2026-07-25 | **Branch:** `generic`
> **Plan directory:** `projects/lms/plan/` + `projects/lms/front-end/plan/`

---

## Plan Inventory

| # | Plan File | Scope | Status | Progress |
|---|-----------|-------|:------:|:--------:|
| 1 | `FRONTEND_ENHANCEMENT_MASTER_PLAN.md` | LMS Front-End: FlyonUI, dropdowns, background, responsive, homepage, docs | 🟡 In Progress | 5% |
| 2 | `FLYONUI_INTEGRATION_PLAN.md` | FlyonUI installation, config, component migration | ⬜ Not Started | 0% |
| 3 | `RESPONSIVE_LAYOUT_PLAN.md` | Mobile/desktop/web layout variants, breakpoints, navigation | ⬜ Not Started | 0% |
| 4 | `COMPONENT_PAGES_PLAN.md` | Component/pages architecture, extendable pages, build targets | ⬜ Not Started | 0% |

---

## Related Plans (from `docs/` — unfinished items carried forward)

### From `DASHBOARD_MIGRATION_PLAN.md` (✅ 100% complete)

| Unfinished Item | Carried To | Priority |
|-----------------|-----------|:--------:|
| 12 non-dashboard lms/lms pages still indigo/purple | lms/lms project (separate) | Low |
| CMS backend: announcements/assignments/quiz/withdrawals APIs | Phase 6 — new API endpoints | Medium |
| Django dev server needs `migrate` | Infrastructure — out of scope | Low |
| POS projects fragment rendering audit | POS plan — out of scope | Low |

### From `FRAGMENT_REDUX_INTEGRATION_PLAN.md` (🟡 70% complete)

| Unfinished Item | Carried To | Priority |
|-----------------|-----------|:--------:|
| Migrate `about-us`, `faq`, `contact` pages to FusionPage middleware | Phase 6 — `components/pages/` | Medium |
| POS frontend `FusionStore` wiring + Tauri `FusionProxy`/`FusionPage` | POS plan — out of scope | Medium |
| Frontend tests for FusionMiddleware/FusionProxy/FusionPage | Phase 8 — testing guide | Medium |
| `RobynFusionChecker` unit tests | POS plan — out of scope | Medium |

### From `front-end/docs/IMPROVEMENTS_PLAN.md` (🟡 30% complete)

| Unfinished Item | Carried To | Priority |
|-----------------|-----------|:--------:|
| Public page smoke tests (`public-pages.spec.ts`) | Phase 8 — testing guide | Medium |
| Extend CTC theme E2E to public pages | Phase 8 — testing guide | Medium |
| Auth flow E2E tests | Phase 8 — testing guide | Medium |
| Unit tests for Header, Footer, LoadingSkeleton, ErrorState, EmptyState | Phase 6 — shared components | High |
| Unit tests for dashboard sub-pages | Phase 6 — dashboard components | High |
| Standardize API error handling (`extractErrorMessage` utility) | Phase 6 — shared utilities | Medium |
| Storybook setup | Phase 8 — documentation | Low |
| CI pipeline additions | ✅ Already done (`js-test.yml`) | — |

---

## Cross-Project Dependencies

```
LMS Front-End (Next.js 14 + React 18 + Tailwind CSS 3)
  ├── FlyonUI v1.x (to be installed)
  ├── framer-motion ^11.0.0 (already installed)
  ├── RTK Query (already installed)
  └── Playwright + Vitest (already installed)

LMS Backend (Django + Wagtail)
  └── django-fusion (fragment rendering, APIs)
```

---

## Progress Legend

| Symbol | Meaning |
|:------:|---------|
| ✅ | Complete |
| 🟡 | In Progress |
| ⬜ | Not Started |
| ❌ | Blocked |
| 🔄 | Needs Review |

---
