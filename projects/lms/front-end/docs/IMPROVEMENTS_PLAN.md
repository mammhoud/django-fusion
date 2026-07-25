# LMS Front-End — Improvements Plan

> **Version:** 1.0.0
> **Last Updated:** 2026-07-25
> **Scope:** `projects/lms/front-end` (Next.js 14 + React 18 + RTK Query + Tailwind CSS)
> **Goal:** Standardize component patterns, expand test coverage, and harden the LMS front-end for production readiness.

---

## 1. Executive Summary

The LMS front-end is a Next.js 14 application serving public pages (homepage, courses, login, registration, etc.) and dashboard pages (instructor, student). It uses RTK Query for API data fetching, Tailwind CSS for styling, and Playwright + Vitest for testing.

Key achievements to date:
- ✅ **CTC Teal theme** fully migrated — zero indigo/purple classes remain in source
- ✅ **15 Playwright E2E tests** for withdrawal flow (create, approve, cancel, lifecycle)
- ✅ **14 dashboard pages** verified for CTC theme compliance (`dashboard-ctc-theme.spec.ts`)
- ✅ **354 Vitest unit tests** passing in `projects/lms/front-end`

This plan identifies remaining gaps and proposes phased improvements.

---

## 2. Current State Assessment

### 2.1 Test Coverage

| Area | Status | Details |
|------|--------|---------|
| **Unit tests (Vitest)** | ✅ 354/354 passing | Covers Fusion middleware, checkout, quizzes, notifications, withdrawals, FAQ, contact |
| **E2E tests (Playwright)** | 🟡 Partial | 2 spec files: `dashboard-core-flows.spec.ts` (10 groups), `dashboard-ctc-theme.spec.ts` (14 pages + cross-page), `withdrawal-flow.spec.ts` (15 tests) |
| **Missing E2E** | ❌ | No public-page E2E tests (homepage, courses, login, registration) |
| **Missing unit tests** | ❌ | Header, Footer, LanguageSwitcher, dashboard sub-pages (quiz editor, assignments, announcement, student-manage) |
| **`projects/lms/lms`** | ⚠️ | Missing `@testing-library/user-event` dependency; `checkout-page.test.tsx` fails to load |

### 2.2 Public Pages (12)

| Page | Route | CTC Teal | E2E Tested |
|------|-------|:--------:|:----------:|
| Homepage | `/` | ✅ | ❌ |
| Courses | `/courses` | ✅ | ❌ |
| Course Details | `/course-details/[id]` | ✅ | ❌ |
| Login | `/login` | ✅ | ❌ |
| Registration | `/registration` | ✅ | ❌ |
| About Us | `/about-us` | ✅ | ❌ |
| Contact | `/contact` | ✅ | ❌ |
| FAQ | `/faq` | ✅ | ❌ |
| Instructors | `/instructors` | ✅ | ❌ |
| Instructor Details | `/instructor-details/[id]` | ✅ | ❌ |
| Cart | `/cart` | ✅ | ❌ |
| Checkout | `/check-out` | ✅ | ❌ |
| Shop | `/shop` | ✅ | ❌ |
| Lesson | `/lesson` | ✅ | ❌ |

### 2.3 Dashboard Pages (14)

| Page | Route | CTC Teal | E2E Tested |
|------|-------|:--------:|:----------:|
| Dashboard Home | `/dashboard` | ✅ | ✅ |
| Courses | `/dashboard/courses` | ✅ | ✅ |
| Course Edit | `/dashboard/courses/[id]/edit` | ✅ | ✅ |
| New Course | `/dashboard/courses/new` | ✅ | ✅ |
| Enrolled Courses | `/dashboard/enrolled-courses` | ✅ | ✅ |
| Quiz | `/dashboard/quiz` | ✅ | ✅ |
| Review | `/dashboard/review` | ✅ | ✅ |
| History | `/dashboard/history` | ✅ | ✅ |
| Profile | `/dashboard/profile` | ✅ | ✅ |
| Attempts | `/dashboard/attempts` | ✅ | ✅ |
| Student Manage | `/dashboard/student-manage` | ✅ | ✅ |
| Withdraw | `/dashboard/withdraw` | ✅ | ✅ |
| Announcement | `/dashboard/announcement` | ✅ | ✅ |
| Assignment | `/dashboard/assignment` | ✅ | ✅ |

### 2.4 Component Inventory

| Component | Has Unit Tests | Has E2E Tests | Notes |
|-----------|:---:|:---:|-------|
| `Header` | ❌ | ❌ | Has CTC teal; needs tests |
| `Footer` | ❌ | ❌ | Has CTC teal; needs tests |
| `NotificationBell` | ✅ | ❌ | Unit tested |
| `NotificationDropdown` | ✅ | ❌ | Unit tested |
| `LanguageSwitcher` | ❌ | ❌ | Simple component, low priority |
| `FusionPage` | ✅ | ✅ | Core fusion bridge |
| `FusionProxy` | ✅ | ✅ | Core fusion bridge |
| `FusionMiddleware` | ✅ | ✅ | Core fusion bridge |
| `LoadingSkeleton` | ❌ | ❌ | Used across many pages |
| `ErrorState` | ❌ | ❌ | Used across many pages |
| `EmptyState` | ❌ | ❌ | Used across many pages |

---

## 3. Objectives

1. **Expand E2E test coverage** to public pages (homepage, courses, auth)
2. **Add unit tests** for untested components (Header, Footer, LoadingSkeleton, ErrorState, EmptyState)
3. **Fix `projects/lms/lms`** dependency issue and enable its test suite
4. **Standardize component patterns** — consistent prop interfaces, error/loading/empty states
5. **Performance audit** — bundle size, image optimization, code splitting
6. **Accessibility audit** — ARIA labels, keyboard navigation, screen reader support

---

## 4. Phase 1 — Expand E2E Test Coverage

### 4.1 Public Page Smoke Tests

Create `tests/e2e/public-pages.spec.ts` following the `dashboard-core-flows.spec.ts` pattern:

| Test Group | Pages | Assertions |
|------------|-------|------------|
| Auth Pages | `/login`, `/registration` | Renders without 404, has form elements, password toggle works |
| Content Pages | `/`, `/courses`, `/about-us`, `/contact`, `/faq` | Renders without 404, has h1, CTC teal classes present |
| Detail Pages | `/course-details/1`, `/instructor-details/1` | Renders without 404, has content |
| Commerce Pages | `/cart`, `/check-out`, `/shop` | Renders without 404 |

### 4.2 CTC Theme Extension

Extend `dashboard-ctc-theme.spec.ts` to also verify public pages:

```typescript
const PUBLIC_PAGES: DashboardPage[] = [
  { path: "/", name: "Homepage", expectedClasses: ["section-hero", "card-gradient"], forbiddenClasses: ["indigo-", "purple-"] },
  { path: "/login", name: "Login", expectedClasses: ["btn-primary", "input-field"], forbiddenClasses: ["indigo-", "purple-"] },
  // ... all 14 public pages
];
```

### 4.3 Auth Flow E2E Tests

```typescript
test.describe("Auth Flow", () => {
  test("login → redirect to dashboard based on role");
  test("registration → role selection → redirect");
  test("password reset flow");
  test("protected route redirects to login when unauthenticated");
});
```

---

## 5. Phase 2 — Unit Test Expansion

### 5.1 Shared Components

| Component | Priority | Test Coverage |
|-----------|:--------:|---------------|
| `Header.tsx` | High | Render, navigation links, mobile menu, CTC teal colors |
| `Footer.tsx` | High | Render, links, CTC teal colors |
| `LoadingSkeleton.tsx` | Medium | Each variant renders correct structure |
| `ErrorState.tsx` | Medium | Renders message, fullPage variant, action button |
| `EmptyState.tsx` | Medium | Renders icon and message, action link |

### 5.2 Dashboard Sub-Pages

| Page | Priority | Test Coverage |
|------|:--------:|---------------|
| Quiz Editor | High | CRUD operations, question management |
| Assignments | High | Create/edit assignment, submission flow |
| Announcements | Medium | Create/edit announcement, targeting |
| Student Management | Medium | Filter, search, enrollment status |

---

## 6. Phase 3 — Bug Fixes & Dependency Cleanup

### 6.1 Fix `projects/lms/lms` Test Suite

```bash
# Add missing dependency
cd projects/lms/lms
npm install --save-dev @testing-library/user-event
```

This fixes the `checkout-page.test.tsx` import error.

### 6.2 Standardize API Error Handling

Several pages catch errors with `(error as any)?.data?.detail` — standardize to a shared error extraction utility:

```typescript
// src/lib/api-errors.ts
export function extractErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'data' in error) {
    const data = (error as any).data;
    return data?.message || data?.detail || data?.error || 'An unexpected error occurred';
  }
  return 'An unexpected error occurred';
}
```

### 6.3 Remove Unused `ADMIN_PROFILE` Constant

Found in `tests/e2e/withdrawal-flow.spec.ts` — may be dead code after cleanup.

---

## 7. Phase 4 — Performance & Accessibility

### 7.1 Performance

- [ ] Audit Next.js bundle with `@next/bundle-analyzer`
- [ ] Add `loading.tsx` files for route-level loading states
- [ ] Convert large page components to use `dynamic(() => import(...))` for code splitting
- [ ] Optimize images with `next/image` (check for raw `<img>` usage)
- [ ] Review RTK Query cache policies (some endpoints use `keepUnusedDataFor: 60`)

### 7.2 Accessibility

- [ ] Add `aria-label` to icon-only buttons (eye toggle, notification bell, language switcher)
- [ ] Ensure form inputs have associated `<label>` elements
- [ ] Add keyboard navigation support for dropdown menus
- [ ] Run `@axe-core/playwright` in E2E tests for automated a11y checks

---

## 8. Phase 5 — Developer Experience

### 8.1 Storybook / Component Library

- [ ] Set up Storybook for shared components (`Header`, `Footer`, cards, buttons, inputs)
- [ ] Document component API (props, variants, usage examples)

### 8.2 CI Pipeline

- [ ] Add Playwright E2E tests to CI
- [ ] Add Vitest unit tests to CI
- [ ] Add TypeScript type checking to CI (`tsc --noEmit`)
- [ ] Add bundle size tracking

### 8.3 Documentation

- [ ] Create `projects/lms/front-end/docs/COMPONENTS.md` with component inventory
- [ ] Create `projects/lms/front-end/docs/TESTING.md` with test conventions
- [ ] Document the CTC teal theme variables and usage patterns

---

## 9. Roadmap

**Legend:** ✅ Complete &nbsp; 🟡 In Progress &nbsp; ⬜ Not Started

| Phase | Deliverable | Status | Effort | Depends On |
|-------|-------------|--------|--------|------------|
| **1.1** | Public page smoke tests (`public-pages.spec.ts`) | ⬜ | Low | — |
| **1.2** | Extend CTC theme test to public pages | ⬜ | Low | 1.1 |
| **1.3** | Auth flow E2E tests | ⬜ | Medium | 1.1 |
| **2.1** | Unit tests for Header, Footer | ⬜ | Medium | — |
| **2.2** | Unit tests for LoadingSkeleton, ErrorState, EmptyState | ⬜ | Low | — |
| **2.3** | Unit tests for dashboard sub-pages | ⬜ | High | — |
| **3.1** | Fix `projects/lms/lms` missing dep | ⬜ | Low | — |
| **3.2** | Standardize API error handling | ⬜ | Low | — |
| **4.1** | Performance audit | ⬜ | Medium | — |
| **4.2** | Accessibility audit | ⬜ | Medium | — |
| **5.1** | Storybook setup | ⬜ | Medium | — |
| **5.2** | CI pipeline additions | ⬜ | Medium | 1.1, 2.1 |
| **5.3** | Documentation | ⬜ | Low | — |

---

## 10. Immediate Next Steps *(recommended)*

1. **Create `public-pages.spec.ts`** — Add smoke tests for all 14 public pages (Phase 1.1)
2. **Fix `projects/lms/lms` dependency** — Install `@testing-library/user-event` to unlock 42 more tests (Phase 3.1)
3. **Add unit tests for Header and Footer** — These are the most visible shared components (Phase 2.1)

---

## 11. Files Referenced

### E2E Tests
- `projects/lms/front-end/tests/e2e/dashboard-core-flows.spec.ts`
- `projects/lms/front-end/tests/e2e/dashboard-ctc-theme.spec.ts`
- `projects/lms/front-end/tests/e2e/withdrawal-flow.spec.ts`

### Unit Tests
- `projects/lms/front-end/src/test/` — 16 test files
- `projects/lms/lms/src/test/` — 5 test files
- `projects/lms/lms/src/__tests__/` — 3 test files

### Shared Components
- `projects/lms/front-end/src/components/Header.tsx`
- `projects/lms/front-end/src/components/Footer.tsx`
- `projects/lms/front-end/src/components/NotificationBell.tsx`
- `projects/lms/front-end/src/components/NotificationDropdown.tsx`
- `projects/lms/front-end/src/components/LanguageSwitcher.tsx`
- `projects/lms/front-end/src/components/ui/LoadingSkeleton.tsx`
- `projects/lms/front-end/src/components/ui/ErrorState.tsx`
- `projects/lms/front-end/src/components/ui/EmptyState.tsx`

### Theme
- `projects/lms/front-end/src/app/globals.css` — CTC teal CSS variables
- `projects/lms/front-end/tailwind.config.js` — CTC teal color definitions

---

*This plan is a living document. Prioritize phases based on business needs: E2E test coverage for public pages, component test coverage, and performance/accessibility hardening.*
