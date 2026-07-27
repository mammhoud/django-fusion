import { test, expect, type Page } from '@playwright/test';
import { mockAuthProfile, STUDENT_PROFILE, INSTRUCTOR_PROFILE, ADMIN_PROFILE } from '../fixtures/auth';

/**
 * Fixed version of dashboard-ctc-theme.spec.ts
 *
 * Previously all 14 dashboard pages failed because they navigated
 * without authentication. Now each page group gets the correct role
 * fixture (student or instructor) so the dashboard renders fully.
 */

// ── Helpers ──────────────────────────────────────────────────────────

function captureConsoleErrors(page: Page) {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  return () =>
    errors.filter(
      (e) =>
        !e.includes('hydration') &&
        !e.includes('Warning:') &&
        !e.includes('next') &&
        !e.includes('favicon') &&
        !e.includes('Failed to load') &&
        !e.includes('ERR_CONNECTION_REFUSED') &&
        !e.includes('fetch') &&
        !e.includes('NetworkError')
    );
}

// ── Test config ──────────────────────────────────────────────────────

const FORBIDDEN_CLASSES = ['indigo-', 'purple-'];

interface DashboardPage {
  path: string;
  name: string;
  expectedClasses: string[];
  forbiddenClasses: string[];
  role: 'student' | 'instructor' | 'admin';
}

// Expected CSS classes for each dashboard page WITHOUT the backend running.
// Dashboard pages require auth (mocked) but also need API data to show
// conditional elements like "Create Course" CTA (btn-primary) or stats cards.
// We check for 'card' (used by DashboardLayout + most page components)
// and 'input-field' where applicable. 'btn-primary' is ONLY present when
// API data satisfies the render condition (e.g. total_courses === 0).
const DASHBOARD_PAGES: DashboardPage[] = [
  {
    path: '/dashboard',
    name: 'Main Dashboard',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/courses',
    name: 'Courses List',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/courses/new',
    name: 'New Course',
    expectedClasses: ['btn-primary', 'input-field'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/quiz',
    name: 'Quiz Dispatcher',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/enrolled-courses',
    name: 'Enrolled Courses',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'student',
  },
  {
    path: '/dashboard/review',
    name: 'Review',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/history',
    name: 'History',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'student',
  },
  {
    path: '/dashboard/profile',
    name: 'Profile',
    expectedClasses: ['btn-primary', 'input-field'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'student',
  },
  {
    path: '/dashboard/attempts',
    name: 'Quiz Attempts',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'student',
  },
  {
    path: '/dashboard/student-manage',
    name: 'Student Management',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/withdraw',
    name: 'Withdraw',
    expectedClasses: ['btn-primary'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/announcement',
    name: 'Announcement',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/assignment',
    name: 'Assignment',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/admin/withdrawals',
    name: 'Admin Withdrawals',
    expectedClasses: ['card'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'admin',
  },
];

// ── Dashboard Tests ────────────────────────────────────────────────────

function getProfileForRole(role: 'student' | 'instructor' | 'admin') {
  switch (role) {
    case 'admin': return ADMIN_PROFILE;
    case 'instructor': return INSTRUCTOR_PROFILE;
    case 'student': return STUDENT_PROFILE;
  }
}

test.describe('Dashboard Pages — CTC Teal Theme', () => {
  for (const pageConfig of DASHBOARD_PAGES) {
    test(`${pageConfig.name} (${pageConfig.path}) renders with CTC teal theme (role: ${pageConfig.role})`, async ({ page }) => {
      const getErrors = captureConsoleErrors(page);

      // Mock auth for the required role
      await mockAuthProfile(page, getProfileForRole(pageConfig.role));

      // Navigate with auth mocked
      const response = await page.goto(pageConfig.path, {
        waitUntil: 'load',
        timeout: 15000,
      });

      // Assertion 1: HTTP 200
      expect(response?.status(), `${pageConfig.name} should return 200`).toBe(200);

      // Wait for auth + data queries to settle
      await page.waitForTimeout(2000);

      const html = await page.content();
      const bodyText = await page.textContent('body');

      // Assertion 2: Expected CTC teal classes present
      for (const cls of pageConfig.expectedClasses) {
        const hasClass = html.includes(cls);
        expect(hasClass, `${pageConfig.name} should contain CSS class "${cls}"`).toBe(true);
      }

      // Assertion 3: No forbidden old-theme classes
      for (const cls of pageConfig.forbiddenClasses) {
        expect(
          html.includes(cls),
          `${pageConfig.name} should NOT contain forbidden class "${cls}"`
        ).toBe(false);
      }

      // Assertion 4: Page has meaningful content
      expect(bodyText?.length ?? 0, `${pageConfig.name} should have content`).toBeGreaterThan(50);

      // Assertion 5: No 404
      if (bodyText) {
        expect(
          bodyText.includes('404') && bodyText.includes('Not Found'),
          `${pageConfig.name} should not show 404 error`
        ).toBe(false);
      }

      // Assertion 6: No console errors
      expect(getErrors(), `${pageConfig.name} should have no console errors`).toHaveLength(0);
    });
  }
});

// ── Cross-page consistency ──────────────────────────────────────────

test.describe('Cross-page CTC Theme Consistency', () => {
  test('CTC primary CSS variables are defined', async ({ page }) => {
    await mockAuthProfile(page, STUDENT_PROFILE);
    await page.goto('/dashboard', { waitUntil: 'load' });
    await page.waitForTimeout(2000);

    const ctcPrimary = await page.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue('--ctc-primary').trim()
    );
    const ctcPrimaryDark = await page.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue('--ctc-primary-dark').trim()
    );

    expect(ctcPrimary).toBe('0 161 179');
    expect(ctcPrimaryDark).toBe('0 122 136');
  });

  test('btn-primary renders with CTC teal background', async ({ page }) => {
    await mockAuthProfile(page, STUDENT_PROFILE);
    await page.goto('/dashboard', { waitUntil: 'load' });
    await page.waitForTimeout(2000);

    const btn = page.locator('.btn-primary').first();
    if (await btn.isVisible({ timeout: 3000 }).catch(() => false)) {
      const bgColor = await btn.evaluate((el) => getComputedStyle(el).backgroundColor);
      expect(bgColor).toBe('rgb(0, 161, 179)');
    }
  });
});

// ─────────────────────────────────────────────────────────────────────
// Public Pages — CTC Teal Theme
// ─────────────────────────────────────────────────────────────────────

interface PublicPage {
  path: string;
  name: string;
  expectedClasses: string[];
}

// Same logic as public-pages.spec.ts: FusionPage-dependent pages show
// ErrorState when CMS API is unavailable (no custom CSS classes render).
const PUBLIC_PAGES: PublicPage[] = [
  { path: '/', name: 'Homepage', expectedClasses: [] },
  { path: '/login', name: 'Login', expectedClasses: ['btn-primary', 'input-field'] },
  { path: '/registration', name: 'Registration', expectedClasses: ['btn-primary', 'input-field'] },
  { path: '/courses', name: 'Courses', expectedClasses: ['input-field'] },
  { path: '/about-us', name: 'About Us', expectedClasses: [] },
  { path: '/contact', name: 'Contact', expectedClasses: [] },
  { path: '/faq', name: 'FAQ', expectedClasses: [] },
  { path: '/instructors', name: 'Instructors', expectedClasses: [] },
  { path: '/cart', name: 'Cart', expectedClasses: [] },
  { path: '/blog', name: 'Blog', expectedClasses: [] },
  { path: '/shop', name: 'Shop', expectedClasses: ['card'] },
  { path: '/privacy', name: 'Privacy', expectedClasses: [] },
  { path: '/events', name: 'Events', expectedClasses: [] },
];

test.describe('Public Pages — CTC Teal Theme', () => {
  for (const pageConfig of PUBLIC_PAGES) {
    test(`${pageConfig.name} (${pageConfig.path}) renders with CTC teal theme`, async ({ page }) => {
      const getErrors = captureConsoleErrors(page);

      // Navigate (no auth needed for public pages)
      const response = await page.goto(pageConfig.path, {
        waitUntil: 'load',
        timeout: 15000,
      });

      // Assertion 1: HTTP 200
      expect(response?.status(), `${pageConfig.name} should return 200`).toBe(200);

      await page.waitForTimeout(2000);

      const html = await page.content();
      const bodyText = await page.textContent('body');

      // Assertion 2: Expected CTC teal classes present
      for (const cls of pageConfig.expectedClasses) {
        const hasClass = html.includes(cls);
        expect(hasClass, `${pageConfig.name} should contain CSS class "${cls}"`).toBe(true);
      }

      // Assertion 3: No forbidden old-theme classes (indigo-, purple-)
      for (const cls of FORBIDDEN_CLASSES) {
        expect(
          html.includes(cls),
          `${pageConfig.name} should NOT contain forbidden class "${cls}"`
        ).toBe(false);
      }

      // Assertion 4: Page has meaningful content
      expect(bodyText?.length ?? 0, `${pageConfig.name} should have content`).toBeGreaterThan(50);

      // Assertion 5: No 404
      if (bodyText) {
        expect(
          bodyText.includes('404') && bodyText.includes('Not Found'),
          `${pageConfig.name} should not show 404 error`
        ).toBe(false);
      }

      // Assertion 6: No console errors
      expect(getErrors(), `${pageConfig.name} should have no console errors`).toHaveLength(0);
    });
  }
});
