# Dashboard Migration Plan — Role-Based Unified Dashboard

> **Last updated:** 2026-07-24 | **Branch:** `generic` | **Tests:** 251/251 passing

---

## ✅ COMPLETED (Phase 1 — Migration)

### lms/front-end (Next.js 14)

| Feature | Status | Details |
|---------|--------|---------|
| Role-based `/dashboard` entry | ✅ | `page.tsx` checks `profile.role` → `InstructorDashboard`/`StudentDashboard` |
| Dashboard layout + sidebar | ✅ | 11 instructor links, 7 student links with CTC teal active states |
| 25 dashboard page files | ✅ | 12 routes + dispatcher pages with role-specific sub-pages |
| DashboardRedirect component | ✅ | Client-side redirect with loading state |
| Old-path redirect pages | ✅ | 39 redirect pages covering all old routes |
| Fusion CMS teal theme | ✅ | 56 CTC refs, 0 indigo/purple |
| API endpoints (RTK Query) | ✅ | instructors, students, courses, auth, pages, blog, events, shop, contact |
| Frontend tests | ✅ | 92/92 pass (vitest) |

### lms/lms (Original Next.js Project)

| Feature | Status | Details |
|---------|--------|---------|
| Fusion CMS teal theme (dashboards) | ✅ | 22 dashboard files converted, 0 indigo/purple |
| CTS/globals.css update | ✅ | Teal CSS vars + `card-gradient`, `section-hero`, `progress-fill/track` |
| DashboardRedirect component | ✅ | `src/components/DashboardRedirect.tsx` |
| Dashboard redirect pages | ✅ | 20 pages (13 instructor + 5 student + 2 root) |
| Frontend tests | ✅ | 79/79 pass (vitest) |

### Backend: lms/cms (Django + Wagtail)

| Feature | Status | Details |
|---------|--------|---------|
| Instructor API | ✅ | List, detail, dashboard, courses, reviews |
| Student API | ✅ | List, detail, dashboard, enrollments, progress |
| Course API | ✅ | Full CRUD with categories, featured |
| Auth API | ✅ | Login, register, logout, profile (role: student/instructor/admin) |
| Fusion health | ✅ | `/apis/fusion/health` |
| Page fragments | ✅ | `page_detail`, `page_fragment`, `page_data` with FusionCodec |
| CMS content models | ✅ | 26 models (snippets + pages + settings) |
| CMS initial migration | ✅ | `www/content/migrations/0001_initial.py` |
| Course fixtures | ✅ | `load_course_fixtures` management command |
| Seed pages command | ✅ | `seed_pages_from_static` + tests |
| Backend tests | ✅ | 80/80 pass (pytest) |

### Infrastructure

| Feature | Status | Details |
|---------|--------|---------|
| Import migration | ✅ | 102 project + 6 ceptor-ai files → canonical `django_fusion.models.*` paths |
| Compat shims deleted | ✅ | 4 shim directories removed; all imports fixed at source |
| manage.py path fix | ✅ | `parents[1]→[2]` — correct repo_root resolution |
| settings.py path ordering | ✅ | `reversed()` applied to all 5 site settings files |
| django-fusion core stubs | ✅ | `managers.py`, `cache.py`, `handlers/emails.py`, `middlewares.py`, `forms.py`, `services.py`, `models/datatoken.py` |
| ceptor-ai fixes | ✅ | `cli.py` import, `enums.py` try/except, 6 handler imports |
| Django dev server | ✅ | Framework loads (needs `migrate` for full DB) |

### Docs

| Document | Status |
|----------|--------|
| `projects/lms/docs/DASHBOARD_MIGRATION_PLAN.md` | ✅ This file |
| `projects/lms/docs/DJANGO_FUSION_ENHANCEMENTS_PLAN.md` | ✅ (POS docs) |

---

## ❌ REMAINING (Phase 2+)

### A. Non-dashboard lms/lms pages — Still indigo/purple

| Page | Status |
|------|--------|
| `/` (homepage) | ❌ Still indigo/purple |
| `/courses` | ❌ Still indigo/purple |
| `/shop` | ❌ Still indigo/purple |
| `/cart` | ❌ Still indigo/purple |
| `/lesson` | ❌ Still indigo/purple |
| `/login` | ❌ Still indigo/purple |
| `/registration` | ❌ Still indigo/purple |
| `/about-us` | ❌ Still indigo/purple |
| `/faq` | ❌ Still indigo/purple |
| `/blog-details` | ❌ Still indigo/purple |
| `/privacy` | ❌ Still indigo/purple |
| `/shop-details/[...id]` | ❌ Still indigo/purple |

### B. CMS Backend Coverage Gaps

| Endpoint | Status |
|----------|--------|
| `POST/GET /apis/announcements/` | ❌ |
| `POST/GET /apis/assignments/` | ❌ |
| `POST/GET /apis/quiz/` | ❌ |
| `POST /apis/withdrawals/` | ❌ |

### C. Django Dev Server — Needs DB Migration

| Issue | Status |
|-------|--------|
| All imports resolve | ✅ |
| `www.content` migration applied | ❌ (run `python manage.py migrate`) |

### D. POS Projects

| Project | Status |
|---------|--------|
| `pos/pos-full` — Fragment rendering | ❌ Needs audit |
| `pos/pos-solo` — Fragment rendering | ❌ Needs audit |

---

## 📊 Test Summary

| Suite | Tests | Status |
|-------|-------|--------|
| Backend (lms/cms) | 80 | ✅ |
| lms/front-end | 92 | ✅ |
| lms/lms | 79 | ✅ |
| **Total** | **251** | **✅ All passing** |

---

## 🔮 Phases (Future)

### Phase 2: Rich Features (MEDIUM)
- Analytics & charts for instructor dashboard
- Quiz builder (create/edit, MCQ/true-false/essay)
- Notification system with read/unread status
- Assignment grading flow

### Phase 3: CMS Integration (MEDIUM)
- Wagtail-managed dashboard content (counters, features, announcements)
- CMS-backed page data for all routes
- Multi-language support

### Phase 4: Testing & Polish (LOW)
- E2E tests for full dashboard flow
- Accessibility audit
- Performance optimization
