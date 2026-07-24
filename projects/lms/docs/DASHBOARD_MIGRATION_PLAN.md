# Dashboard Migration Plan — Role-Based Unified Dashboard

## Current State Summary

### ✅ COMPLETED

#### Frontend: lms/front-end (Next.js 14)

| Feature | Status | Details |
|---------|--------|---------|
| Role-based `/dashboard` entry | ✅ | `page.tsx` checks `profile.role` → renders `InstructorDashboard` or `StudentDashboard` |
| Dashboard layout + sidebar | ✅ | Role-aware sidebar: 5 instructor links, 4 student links |
| 25 dashboard page files | ✅ | 12 routes: courses, quiz, review, enrolled-courses, student-manage, history, attempts, profile, withdraw, announcement, assignment + courses/new, courses/[id]/edit |
| DashboardRedirect component | ✅ | Redirects old `/instructor-dashboard/*` and `/student-dashboard/*` to `/dashboard/*` |
| Old-path redirect pages | ✅ | 39 redirect pages (15 instructor + 7 student sub-pages) |
| CTC Research teal theme | ✅ | 56 CTC references, 0 indigo/purple across all dashboard pages |
| FusionPage/FusionProxy/FusionMiddleware | ✅ | Server-side fragment rendering support |
| API endpoints (RTK Query) | ✅ | instructors, students, courses, auth (profile with role), pages, blog, events, shop, contact |
| Frontend tests | ✅ | 92/92 pass (vitest) |
| Fusion e2e roundtrip test | ✅ | `tests/fusion-decoder-roundtrip.test.mjs` |

#### Backend: lms/cms (Django + Wagtail)

| Feature | Status | Details |
|---------|--------|---------|
| Instructor API | ✅ | `www/api/instructors.py` — list, detail, dashboard, courses, reviews |
| Student API | ✅ | `www/api/students.py` — list, detail, dashboard, enrollments, progress |
| Course API | ✅ | `www/api/courses.py` + `www/api/data/courses.py` |
| Auth API | ✅ | Login, register, logout, profile (with role field) |
| Fusion health endpoint | ✅ | `www/api/fusion_health.py` |
| Page fragment endpoints | ✅ | `www/api/pages.py` — page_detail, page_fragment, page_data |
| CMS content models | ✅ | `www/content/models/` — 26 models (snippets + pages + settings) |
| CMS initial migration | ✅ | `www/content/migrations/0001_initial.py` |
| Course fixtures | ✅ | `plugins/lms/management/commands/load_course_fixtures.py` |
| Seed pages command | ✅ | `plugins/pages/management/commands/seed_pages_from_static.py` |
| Backend tests | ✅ | 80/80 pass (pytest) |

#### Infrastructure

| Feature | Status | Details |
|---------|--------|---------|
| Import migration (canonical paths) | ✅ | 102 project files + 6 ceptor-ai files → `django_fusion.models.base` |
| Compat shim removed | ✅ | `django_fusion/core/models.py` deleted |
| manage.py path fix | ✅ | `parents[1]→[2]` for correct repo_root |
| settings.py path ordering fix | ✅ | `reversed()` so `SITE_DIR` before `SITE_APP_DIR` |

---

### ❌ INCOMPLETE / GAPS

#### A. lms/lms (Original Next.js Project) — NOT YET MIGRATED

| Gap | Priority | Effort |
|-----|----------|--------|
| Still uses old route structure: `instructor-dashboard/*`, `student-dashboard/*` | HIGH | Medium |
| Still uses indigo/purple theme (NOT CTC teal) | HIGH | Medium |
| Has different sidebar links (8 instructor, 7 student vs 5/4 in new) | MEDIUM | Low |
| No FusionPage/FusionProxy integration yet | LOW | Medium |
| No dashboard migration redirects | HIGH | Low |

Old `lms/lms` sidebar links NOT in new `lms/front-end`:
- Instructor: Assignments, Student Attempts, Announcements, History
- Student: History, Attempts

#### B. lms/front-end Sidebar — Missing Links

The sidebar in the new dashboard only shows 5 instructor / 4 student links, but the pages exist:

| Page exists? | In sidebar? | Route |
|-------------|-------------|-------|
| ✅ | ✅ | `/dashboard` (Overview) |
| ✅ | ✅ | `/dashboard/courses` |
| ✅ | ✅ | `/dashboard/quiz` |
| ✅ | ✅ | `/dashboard/review` (instructor only) |
| ✅ | ✅ | `/dashboard/enrolled-courses` |
| ✅ | ✅ | `/dashboard/profile` (student only) |
| ✅ | ❌ | `/dashboard/announcement` |
| ✅ | ❌ | `/dashboard/assignment` |
| ✅ | ❌ | `/dashboard/student-manage` |
| ✅ | ❌ | `/dashboard/history` |
| ✅ | ❌ | `/dashboard/attempts` |
| ✅ | ❌ | `/dashboard/withdraw` |

#### C. Dispatcher Pages — Need Role-Aware Routing

These pages have `page.tsx` dispatchers but need role-specific sub-pages:

| Route | Current State | Needed |
|-------|--------------|--------|
| `/dashboard/quiz` | `page.tsx` dispatcher → `instructor.tsx` / `student.tsx` | ✅ Complete |
| `/dashboard/enrolled-courses` | `page.tsx` dispatcher → `instructor.tsx` / `student.tsx` | ✅ Complete |
| `/dashboard/history` | `page.tsx` dispatcher → `instructor.tsx` / `student.tsx` | ✅ Complete |
| `/dashboard/attempts` | `page.tsx` dispatcher → `instructor.tsx` / `student.tsx` | ✅ Complete |
| `/dashboard/profile` | `page.tsx` dispatcher → `instructor.tsx` / `student.tsx` | ✅ Complete |

#### D. Django Dev Server — Partially Fixed

| Issue | Status |
|-------|--------|
| `manage.py` path resolution (`parents[1]→[2]`) | ✅ Fixed |
| `settings.py` path ordering (`reversed()`) | ✅ Fixed |
| `www.core` import error | ✅ Resolved |
| `django_fusion.site.enums` missing | ❌ Needs shim |
| Other site settings.py (cms/lms-full, cms/cms-full, portfolio, www) | ❌ Need same `reversed()` fix |

#### E. CMS Backend Coverage Gaps

| API Endpoint | Status | Frontend use |
|-------------|--------|-------------|
| `GET /apis/instructors/<id>/dashboard/` | ✅ | Dashboard stats |
| `GET /apis/instructors/<id>/courses/` | ✅ | Course list |
| `GET /apis/instructors/<id>/reviews/` | ✅ | Review list |
| `GET /apis/students/<id>/dashboard/` | ✅ | Dashboard stats |
| `GET /apis/students/<id>/enrollments/` | ✅ | Enrolled courses |
| `POST /apis/enrollments/<id>/progress/` | ✅ | Progress tracking |
| `POST /apis/announcements/` | ❌ | Create announcement |
| `GET /apis/announcements/` | ❌ | List announcements |
| `POST /apis/assignments/` | ❌ | Create assignment |
| `GET /apis/assignments/` | ❌ | List assignments |
| `POST /apis/quiz/` | ❌ | Create/submit quiz |
| `GET /apis/quiz/<id>/` | ❌ | Get quiz details |
| `POST /apis/withdrawals/` | ❌ | Process withdrawal |

---

### 🔮 POTENTIAL ENHANCEMENTS

#### Phase 1: Complete the Migration (HIGH priority)

1. **Migrate lms/lms to `/dashboard` routes**
   - Add DashboardRedirect pages for all old `instructor-dashboard/*` and `student-dashboard/*` paths
   - Convert all indigo/purple references to CTC teal
   - Add FusionPage/FusionProxy integration

2. **Expand sidebar links**
   - Add Announcements, Assignments, Student Manage, History, Attempts, Withdraw to role-appropriate sidebar

3. **Fix Django dev server**
   - Create `django_fusion.site.enums` compatibility shim
   - Apply `reversed()` fix to other 4 site settings files
   - Test full Django startup

4. **Create needed CMS API endpoints**
   - Announcements CRUD (`/apis/announcements/`)
   - Assignments CRUD (`/apis/assignments/`)
   - Quiz endpoints (`/apis/quiz/`)
   - Withdrawals endpoint (`/apis/withdrawals/`)

#### Phase 2: Rich Dashboard Features (MEDIUM priority)

5. **Analytics & Charts**
   - Instructor: Monthly earnings chart, enrollment trends, course completion rates
   - Student: Learning time chart, progress over time, skill radar

6. **Quiz Builder**
   - Instructor: Create/edit quizzes with question types (MCQ, true/false, essay)
   - Student: Timed quiz interface with flagging, review after submission

7. **Notification System**
   - Announcements with read/unread status
   - Assignment due date reminders
   - Enrollment confirmation notifications

8. **Assignment Grading Flow**
   - Instructor: Grade submissions, leave feedback
   - Student: Submit assignments, view grades and feedback

9. **Payment & Withdrawal**
   - Instructor: Revenue dashboard, withdrawal request, payment history
   - Student: Purchase history, invoice downloads

#### Phase 3: CMS Integration (MEDIUM priority)

10. **Wagtail-managed dashboard content**
    - Dashboard counters as Wagtail snippets (already modeled: `DashboardCounter`)
    - Announcement templates as Wagtail snippets
    - Feature highlights as Wagtail snippets (already modeled: `Feature`)

11. **CMS-backed page data for all routes**
    - Replace remaining static data with Wagtail CMS queries
    - Multi-language support on all dashboard pages

#### Phase 4: Testing & Polish (LOWER priority)

12. **E2E tests for full dashboard flow**
    - Login → dashboard → courses → enroll → progress → complete
    - Instructor: login → dashboard → create course → add quiz → grade

13. **Accessibility audit**
    - ARIA labels, keyboard navigation, screen reader support

14. **Performance optimization**
    - API response caching, skeleton loading states, code splitting

---

### 📋 IMMEDIATE ACTION PLAN (Next Steps)

| # | Task | Priority | Files | Effort |
|---|------|----------|-------|--------|
| 1 | Add missing sidebar links in layout.tsx | HIGH | 1 | Low |
| 2 | Create `django_fusion.site.enums` compat shim | HIGH | 1 | Low |
| 3 | Apply `reversed()` fix to other 4 settings.py | HIGH | 4 | Low |
| 4 | Migrate lms/lms indigo/purple → CTC teal | HIGH | ~15 | Medium |
| 5 | Add DashboardRedirect pages to lms/lms | HIGH | ~22 | Medium |
| 6 | Migrate lms/lms instructor/student dashboards to /dashboard | HIGH | ~10 | Medium |
| 7 | Create CMS announcement API endpoint | MEDIUM | 2 | Medium |
| 8 | Create CMS assignment API endpoint | MEDIUM | 2 | Medium |
| 9 | Create CMS quiz API endpoint | MEDIUM | 2 | Medium |
| 10 | Instructor analytics/charts | MEDIUM | 2 | Medium |
| 11 | Notification system (announcements read status) | LOW | 3 | Medium |
| 12 | E2E tests for dashboard flow | LOW | 2 | Large |
