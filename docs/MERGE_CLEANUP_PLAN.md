# Fusion Projects — Merge, Cleanup & Refactoring Plan

> **Context:** `projects/lms-fusion/` + `projects/cms-fusion/`  
> **References:** [`docs/plans.md`](./plans.md), [`docs/ASSETS_MIGRATION_INVENTORY.md`](./ASSETS_MIGRATION_INVENTORY.md)  
> **Date:** 2026-07-26  
> **Status:** Planning phase

---

## Table of Contents

1. [Dead & Unused Code](#1-dead--unused-code)
2. [Incomplete / Unfinished Features](#2-incomplete--unfinished-features)
3. [Refactoring Opportunities](#3-refactoring-opportunities)
4. [Template & Asset Migration Status](#4-template--asset-migration-status)
5. [Phase-by-Phase Execution Plan](#5-phase-by-phase-execution-plan)

---

## 1. Dead & Unused Code

### 1.1 Frontend Components (Created but Not Integrated)

| Component | lms-fusion | cms-fusion | Status |
|-----------|:----------:|:----------:|--------|
| `LanguageSwitcher.tsx` | ✅ Created + integrated in Header | ✅ Created + integrated in Header | Live |
| `DashboardRedirect.tsx` | ✅ Created | ✅ Created | Live (requires routing setup) |
| `FusionWagtailPage.tsx` | ✅ Exists | ✅ Exists | Used |
| `PageNavigation.tsx` | ✅ Exists | ✅ Exists | Used |
| `FusionLayout.tsx` | ✅ Exists | ✅ Exists | Used |

**Old LMS (`lms/front-end/`) components NOT yet ported to either fusion project:**

| Component | Old LMS Location | Dependencies | Porting Priority |
|-----------|-----------------|--------------|:----------------:|
| `FusionMiddleware.tsx` | `lms/front-end/src/components/` | Redux store, fusion-decoder, sessionStorage | High |
| `AuthGuard.tsx` | `lms/front-end/src/components/` | RTK Query auth endpoint, LoadingSkeleton | High |
| `NotificationBell.tsx` | `lms/front-end/src/components/` | RTK Query notification endpoints, react-icons | Medium |
| `NotificationDropdown.tsx` | `lms/front-end/src/components/` | RTK Query notification endpoints | Medium |
| `LoadingSkeleton.tsx` | `lms/front-end/src/components/ui/` | None (pure UI) | High (dependency of AuthGuard) |

**All these remain in the old LMS tree — they are dead code in the context of the fusion projects.**

### 1.2 Silenced System Checks (Legacy Migration Artifacts)

Both fusion projects silence 7 Django system checks that exist solely because of legacy migration:

```python
SILENCED_SYSTEM_CHECKS = [
    "models.E028",  # legacy accounts/handlers shared service table
    "models.E030",  # legacy accounts/handlers shared indexes
    "models.E032",  # legacy accounts/handlers shared constraints
    "fields.E304",  # legacy duplicated profile reverse accessors
    "fields.E305",  # legacy duplicated profile reverse query names
    "fields.E340",  # legacy duplicated many-to-many intermediary tables
    "treebeard.E001",  # Wagtail Page/Collection managers (harmless until Treebeard 6)
]
```

**Action:** After the migration from old `accounts`/`handlers` shared models is complete and the old models are removed from `INSTALLED_APPS`, these silences should be removed. The `treebeard.E001` silence is a Wagtail compatibility issue.

### 1.3 Orphaned Test Files

The old LMS (`projects/lms/tests/`) has test files that test features not yet ported:

- `test_data_contact.py` — tests contact form API
- `test_data_events.py` — tests events API
- `test_data_shop.py` — tests shop/checkout API
- `test_data_adapter.py` — tests data adapter
- `test_data_courses.py` — tests courses API
- `test_data_blog.py` — tests blog API
- `test_data_auth.py` — tests auth API
- `test_data_students.py` — tests students API
- `test_data_instructors.py` — tests instructors API
- `test_data_withdrawals.py` — tests withdrawals API
- `test_notifications.py` — tests notifications

These test patterns should inform the development of fusion project tests but remain unported.

### 1.4 Legacy Projects (Not Updated)

These project trees exist but are **not actively maintained** — their purpose is either archived or superseded by fusion projects:

| Directory | Status | Notes |
|-----------|:------:|-------|
| `projects/cms/ctc-research.bak/` | 🔒 Archived | Backup of old ctc-research |
| `projects/cms/cms-full/` | ⏸️ Legacy | Superseded by `cms-fusion` |
| `projects/cms/lms-full/` | ⏸️ Legacy | Superseded by `lms-fusion` |
| `projects/lms/cms/` | ⏸️ Legacy | Old LMS Django app |
| `projects/lms/lms/` | ⏸️ Legacy | Old LMS Next.js app |
| `projects/lms/front-end/` | ⏸️ Legacy | Old LMS primary frontend |
| `projects/lms/plugins/` | ⏸️ Legacy | Old LMS plugins |
| `projects/cms/portfolio/` | 🟢 Active | Portfolio site (not fusion) |

### 1.5 Dummy/Seed Data

Both fusion projects have dummy fixture data in `backend/assets/fixtures/`:
- `auth/group_dummy.json` — sample user groups
- `auth/user_dummy.json` — sample users
- `seed/homepage_content.json` — sample homepage CMS content
- `production/` — production fixtures
- `by-model/INDEX.json` — fixture index

These are development scaffolding and may be unused in production.

---

## 2. Incomplete / Unfinished Features

### 2.1 Frontend Features

| Feature | Status | Notes |
|---------|:------:|-------|
| **Language switching** | ⚠️ Partial | `LanguageSwitcher` component merged + integrated. Backend endpoint `/apis/i18n/setlang/` is from old LMS — fusion projects may not expose this route. Needs fusion-native i18n endpoint. |
| **Authentication guard** | ❌ Missing | Old LMS has `AuthGuard.tsx` (RTK Query-based). Fusion projects have no auth protection on frontend routes. |
| **Notifications** | ❌ Missing | Old LMS has NotificationBell + NotificationDropdown + RTK Query endpoints. Fusion projects have zero notification UI. |
| **LoadingSkeleton** | ❌ Missing | Old LMS has `LoadingSkeleton` UI component. Fusion projects use inline `.fusion-skeleton` CSS classes instead. |
| **FusionMiddleware** | ❌ Missing | Old LMS has `FusionMiddleware` context provider for fusion mode + language. Fusion projects use `FusionStore` singleton class instead (different pattern). |
| **Redux store API layer** | ❌ Missing | Old LMS has extensive RTK Query endpoint definitions. Fusion projects use a custom `FusionApiClient` class with `fetch` directly. |
| **Playwright E2E tests** | ✅ Added | Both fusion projects have E2E test files + CI jobs. |
| **DashboardRedirect** | ✅ Merged | Component exists in both fusion projects. Requires dashboard routing to be configured. |

### 2.2 Backend Features

| Feature | Status | Notes |
|---------|:------:|-------|
| **Wishlist functionality** | ⚠️ TODO | `plugins/lms/views/courses.py` line 575: `# TODO: Implement wishlist functionality with custom user model` |
| **API schema models** | ❌ Missing | Old LMS has Pydantic schemas for courses, blog, auth, contact, enrollment, shop, etc. None ported to fusion projects. |
| **API endpoints** | ⚠️ Partial | Fusion projects have `fusion_health`, `pages`, `branding` endpoints. Old LMS has many more: courses CRUD, blog CRUD, auth, contact, shop, withdrawals, students, instructors, quiz, announcements. |
| **Wagtail RoutableComponent** | ⬜ Unchecked | Migration plan lists `Wagtail pages inherit from RoutableComponent` as unmarked. |
| **Django checks (step 4)** | ⬜ Unchecked | `make check WEBSITE=lms-fusion` passes but the migration plan checklist shows step 4 unchecked. |
| **Create superuser (step 5)** | ⬜ Unchecked | No automated superuser creation. |
| **Seed branding (step 6)** | ⬜ Unchecked | No automated branding seeding. |

### 2.3 CI / Infrastructure

| Feature | Status | Notes |
|---------|:------:|-------|
| **Fusion CI workflow** | ✅ Complete | All 8 jobs (backend, frontend, E2E for both projects) + deploy-staging job. |
| **Docker builds** | ❌ Broken | Backend build fails due to out-of-sync `package-lock.json` in `projects/assets/`. Frontend build fails because `assets/` not copied in Docker context. |
| **Deploy to staging** | ✅ Job defined | Manual `workflow_dispatch` trigger, gated on all checks. SQLite override for CI. |

### 2.4 Phase 0 — Discovery Gaps (from ASSETS_MIGRATION_INVENTORY)

- ❌ Runtime disconnect not yet run
- ❌ Diff matrix between fusion backends and legacy backends not yet generated
- ❌ Data-only / migration files not yet tagged

### 2.5 Phase 8 — Shared Media

The shared media server (`shared-media` Nginx) serves static/media for all sites. The fusion projects reference it in their docker-compose volumes but the shared-media deployment isn't configured for them yet.

---

## 3. Refactoring Opportunities

### 3.1 Duplicate Code Between lms-fusion and cms-fusion

The two fusion projects are virtually identical in structure. The following are **near-duplicates** that could be unified:

| Area | lms-fusion | cms-fusion | Refactor |
|------|-----------|------------|----------|
| **Settings** | `backend/settings.py` | `backend/settings.py` | 95% identical (branding colors, site name differ). Could share 80% via a base settings module. |
| **Plugins** | All plugins | All plugins | 100% identical plugin code. Only branding/pages models differ. |
| **Frontend components** | Header, Footer, etc. | Header, Footer, etc. | 80% identical. Only nav links and color scheme differ. |
| **www app** | Full copy | Full copy | 100% identical. Entire `www/` tree is duplicated. |
| **Templates** | Plugin templates | Plugin templates | 100% identical. Only `backend/templates/` site-root templates differ. |
| **Docker compose** | `docker-compose.yml` | `docker-compose.yml` | 95% identical. Only ports and env vars differ. |
| **Frontend pages** | Homepage + [slug] | Homepage + blog + courses + products + [slug] | cms-fusion has additional pages. |

**Refactor proposal:** Extract shared plugin code into `libs/django-fusion` or a new `libs/fusion-shared` library. The fusion projects would then only carry site-specific branding, templates, and frontend pages.

### 3.2 Template Organization

The template reorganization (Phase 2 of the cleanup plan) is **complete**:
- App-specific templates moved from `backend/templates/` → `plugins/<app>/templates/`
- Only site-root templates remain in `backend/templates/`

**Remaining template work:**
- Some templates in the old LMS tree (`lms/cms/templates/`) may have content worth porting
- Blog templates (20+ variants in old LMS blog directory) — unused by Next.js frontend
- Course/learning templates — the Next.js `/courses` page handles this

### 3.3 Frontend Build Pipeline

| Issue | Details |
|-------|---------|
| **Docker frontend Dockerfile** | Doesn't copy `assets/` directory, so `../assets/styles/fusion-theme.scss` is not found during build |
| **Shared assets npm lockfile** | `projects/assets/package-lock.json` is out of sync with `package.json` (missing `@vue/reactivity`) |
| **Build:theme path** | Uses `../` relative path from `frontend/` — works locally but breaks in Docker |

**Fix:** Update `projects/cms-fusion/compose/frontend/Dockerfile` (and lms-fusion's) to also copy the `assets/` directory into the build context.

### 3.4 ASGI/WSGI Mismatch

Both fusion projects default to ASGI mode in `server.py` but `WSGI_APPLICATION = "server.application"`. When `DEBUG=True` Django's `runserver` uses WSGI and calls the ASGI app with WSGI args, causing `application() missing 'send'` error.

**Fix in progress:** Use `DJANGO_SERVER_TYPE=wsgi` env var for `runserver`, or configure production ASGI server (uvicorn/daphne) separately.

### 3.5 www.worker Shadowing

The workspace `www/` package is shadowed by the site-local `www/` package, making `www.worker` unimportable in fusion projects. Currently worked around by removing `www.worker` from `INSTALLED_APPS`.

**Fix:** Create a shared-worker shim or namespace change.

---

## 4. Template & Asset Migration Status

Based on the master plan (`docs/plans.md`) and localized plans, here is the status of all phases:

| Phase | Description | Status |
|:----:|-------------|:------:|
| **0** | Discovery — inventory references, scan docs | ✅ Complete |
| **1** | Asset migration — move design assets to project-local | ⬜ Not started |
| **1b** | SCSS / branding pipeline | ✅ Complete |
| **2** | Template reorganization — move app templates to plugins | ✅ Complete |
| **3** | Legacy cleanup — delete duplicate files from old trees | ⬜ Not started |
| **4** | AGENTS.md cleanup — update references | ✅ Partial |
| **5** | Validation — checks, tests, template audit | ✅ Partial |
| **6** | Build pipeline — webpack, npm scripts | ✅ Complete |
| **7** | Docker-Compose & Proxy | ✅ Complete |
| **8** | Shared media — Nginx configuration | ⬜ Not started |

### 4.1 Files Needing AGENTS.md Updates

The following files still reference `projects/assets/` and need updating once the shared asset layer is relocated:

- `AGENTS.md` (root)
- `.github/AGENTS.md`
- `docs/ai/README.md`
- `docs/ai/agents.md`
- `docs/customization/customization-methods.md`
- `docs/design/README.md`
- `docs/projects/libs/templates-architecture.md`
- `docs/projects/lms/clone-guide.md`
- `docs/repo-overview.md`

---

## 5. Phase-by-Phase Execution Plan

### Phase A — Fix Dead Code & Build Pipeline

| # | Task | Project | Priority |
|:-:|------|:-------:|:--------:|
| A1 | Regenerate `projects/assets/package-lock.json` via `npm install --legacy-peer-deps` | Shared | 🔴 High |
| A2 | Fix frontend Dockerfiles to copy `assets/` directory during build | Both | 🔴 High |
| A3 | Remove silenced system checks after verifying legacy apps are gone | Both | 🟡 Medium |
| A4 | Delete or archive old LMS/CMS project trees (after verification) | Legacy | 🟢 Low |

### Phase B — Complete Unfinished Frontend Features

| # | Task | Project | Priority |
|:-:|------|:-------:|:--------:|
| B1 | Create `LoadingSkeleton.tsx` UI component (dependency for AuthGuard) | Both | 🔴 High |
| B2 | Port `AuthGuard.tsx` (adapt for fusion API, not RTK Query) | Both | 🔴 High |
| B3 | Implement wishlist endpoint (remove TODO in courses.py) | Both | 🟡 Medium |
| B4 | Create fusion-native i18n endpoint and wire LanguageSwitcher | Both | 🟡 Medium |
| B5 | Port `FusionMiddleware.tsx` context provider (or keep FusionStore pattern) | Both | 🟡 Medium |
| B6 | Port notification UI components | Both | 🟢 Low |

### Phase C — Merge API Endpoints from Old LMS

| # | Task | Project | Priority |
|:-:|------|:-------:|:--------:|
| C1 | Port Pydantic API schemas (`www/schemas/`) from old LMS | Both | 🟡 Medium |
| C2 | Port course CRUD API endpoints | Both | 🟡 Medium |
| C3 | Port blog CRUD API endpoints | Both | 🟡 Medium |
| C4 | Port auth/profile API endpoints | Both | 🟡 Medium |
| C5 | Port remaining API endpoints (contact, shop, withdrawals, etc.) | Both | 🟢 Low |

### Phase D — Complete Template & Asset Migration

| # | Task | Project | Priority |
|:-:|------|:-------:|:--------:|
| D1 | Generate diff matrices (fusion vs legacy) | Both | 🟡 Medium |
| D2 | Run runtime disconnect (drop `projects/assets/` from TEMPLATES['DIRS']) | Both | 🟡 Medium |
| D3 | Move design source assets into `<project>/assets/` | Both | 🟡 Medium |
| D4 | Delete confirmed duplicate files from legacy trees | Legacy | 🟢 Low |
| D5 | Update AGENTS.md files (19 references across repo) | Both | 🟢 Low |
| D6 | Configure shared-media Nginx for fusion sites | Infra | 🟢 Low |

### Phase E — Refactoring

| # | Task | Project | Priority |
|:-:|------|:-------:|:--------:|
| E1 | Extract shared plugin code into `libs/django-fusion` or `libs/fusion-shared` | Both | 🟡 Medium |
| E2 | Create base settings module for common fusion settings | Both | 🟡 Medium |
| E3 | Resolve `www.worker` shadowing issue | Both | 🟡 Medium |
| E4 | Standardize ASGI/WSGI server configuration | Both | 🟢 Low |

---

## Appendix: Feature Comparison Matrix

| Feature | Old LMS | Old CMS | lms-fusion | cms-fusion |
|---------|:-------:|:-------:|:----------:|:----------:|
| **Frontend pages** | Home, courses, blog, shop, auth, dashboard | Pages, blog, courses | Home, [slug] | Home, blog, courses, products, [slug] |
| **Auth system** | allauth + JWT | allauth + JWT | allauth + fusion | allauth + fusion |
| **Notifications** | RTK Query + real-time | RTK Query | ❌ | ❌ |
| **Language switch** | FusionMiddleware | None | Partial (component merged, endpoint missing) | Partial (same) |
| **Auth guard** | AuthGuard component | None | ❌ | ❌ |
| **Wishlist** | ✅ | ✅ | ❌ (TODO in code) | ❌ (TODO in code) |
| **E2E tests** | Extensive (7+ files) | None | ✅ (2 spec files) | ✅ (2 spec files) |
| **CI/CD** | js-test, pytest-core | None | ✅ fusion-ci.yml | ✅ fusion-ci.yml |
| **Docker deploy** | ✅ | ✅ | ❌ broken | ❌ broken |
| **API schemas** | Pydantic models | Pydantic models | ❌ | ❌ |
| **Loading skeleton** | `LoadingSkeleton.tsx` | None | CSS-only (`.fusion-skeleton`) | CSS-only |

---

**Next recommended action:** Begin with Phase A (fix Docker builds + package-lock) since those are blocking deployment, then move to Phase B (frontend features) which has the highest user-facing impact.
