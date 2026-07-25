# LMS Front-End E2E Testing Guide

Comprehensive Playwright E2E test suite for the LMS platform front-end, covering both **render-first** (browser) and **bolt-pattern** (API) testing strategies.

## Quick Start

```bash
cd projects/lms/front-end

# Install (if not already done)
npm install
npx playwright install chromium

# Run all E2E tests
npm run test:e2e

# Run only browser tests
npx playwright test tests/e2e/

# Run only API tests (bolt pattern)
npx playwright test tests/api/

# Interactive debug mode
npm run test:e2e:ui

# View HTML report
npm run test:e2e:report

# Run everything: unit tests + E2E
npm run test:all
```

## Architecture

```
tests/
├── fixtures/
│   └── auth.ts              # Shared auth fixture (mocks /apis/auth/profile/)
├── e2e/                     # Browser-based tests (render first)
│   ├── public-pages.spec.ts         # All public pages (home, courses, about, etc.)
│   ├── auth-flows.spec.ts           # Login, register, password toggle
│   ├── dashboard-ctc-theme.spec.ts  # CTC teal theme on all dashboard pages
│   ├── dashboard-ctc-theme.fixed.spec.ts  # FIXED: with auth mocks per role
│   ├── dashboard-core-flows.spec.ts # Core dashboard interactions
│   ├── withdrawal-flow.spec.ts      # Instructor withdrawal flow
│   └── admin-withdrawals.spec.ts    # Admin approval UI
└── api/                     # API-only tests (bolt pattern)
    └── backend-api.spec.ts          # Django backend auth, courses, instructors
```

## Two Testing Strategies

### 1. Render First (Browser E2E)

Tests navigate pages in Chromium. Use these for:
- Page rendering and layout
- User interaction flows
- Theme/visual consistency
- Cross-page navigation

```ts
import { test, expect } from '../fixtures/auth';

test('dashboard renders for instructor', async ({ instructorPage }) => {
  await instructorPage.goto('/dashboard/courses');
  await expect(instructorPage.locator('h1')).toContainText('My Courses');
});
```

### 2. Bolt Pattern (API E2E)

Tests call the Django backend API directly. Use these for:
- Fast backend validation
- Auth token flows
- CRUD operations
- Error handling (401, 403, 404)

```ts
test('courses endpoint returns data', async () => {
  const { status, body } = await apiGet('/apis/courses/');
  expect(status).toBe(200);
  expect(body.results).toBeDefined();
});
```

## Auth Mocking

Dashboard pages require authentication. The shared fixture in `tests/fixtures/auth.ts` mocks `GET /apis/auth/profile/` to return the appropriate role:

```ts
// Available fixtures:
test('student view', async ({ studentPage }) => { ... });
test('instructor view', async ({ instructorPage }) => { ... });
test('admin view', async ({ adminPage }) => { ... });
```

**Important:** Match the fixture role to the page being tested:
- `/dashboard/enrolled-courses`, `/dashboard/history`, `/dashboard/profile` → `studentPage`
- `/dashboard/courses`, `/dashboard/courses/new`, `/dashboard/withdraw` → `instructorPage`
- `/dashboard/admin/withdrawals` → `adminPage`
- Public pages (`/`, `/courses`, `/login`) → standard `page` (no auth needed)

## Test Files

### Public Pages (`public-pages.spec.ts`)
9 public pages tested: homepage, courses, about, contact, FAQ, instructors, login, registration, cart.

### Auth Flows (`auth-flows.spec.ts`)
Login form, registration validation, password toggle, page navigation between auth pages.

### CTC Theme (`dashboard-ctc-theme.spec.ts` + `dashboard-ctc-theme.fixed.spec.ts`)
- **Original**: Navigates 14 dashboard pages without auth (most fail)
- **Fixed**: Uses per-role auth fixtures so pages render fully

### Dashboard Core Flows (`dashboard-core-flows.spec.ts`)
37 tests covering login, registration, student dashboard, enrolled courses, history, reviews, wishlist interactions.

### Withdrawal Flow (`withdrawal-flow.spec.ts`)
15 tests for instructor withdrawal creation and tracking.

### Admin Withdrawals (`admin-withdrawals.spec.ts`)
11 tests for admin withdrawal approval/rejection UI.

### Backend API (`backend-api.spec.ts`)
Django API tests: health check, auth (login/register), courses listing, instructors, error handling.

## Adding a New Test

1. Determine if it needs auth: use the shared fixture or standard `page`
2. Match the role to the page being tested
3. Follow existing patterns for console error capture and assertions

```ts
import { test, expect } from '../fixtures/auth';

test('new feature', async ({ instructorPage }) => {
  await instructorPage.goto('/dashboard/new-feature');
  await expect(instructorPage.locator('h1')).toBeVisible();
});
```

## CI Integration

```yaml
- name: Run E2E tests
  run: |
    cd projects/lms/front-end
    npx playwright test --reporter=list
```

The Playwright config auto-starts the Next.js dev server on port 3457. No separate setup needed.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tests fail with missing CSS classes | Use `dashboard-ctc-theme.fixed.spec.ts` which includes auth mocks |
| `useCreateCourseMutation` import error | Fixed: now imported from `endpoints/courses` not `endpoints/instructors` |
| `deleteCourse` naming conflict | Fixed: renamed to `deleteInstructorCourse` in instructors endpoint |
| Strict mode violations (multiple elements) | Use `page.getByRole()` or `.first()` instead of generic selectors |
| Timeout on `networkidle` | Pages may not settle without auth. Add auth fixture or increase timeout |
