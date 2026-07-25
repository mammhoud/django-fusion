import { test, expect } from '../../fixtures/auth';
import type { Page } from '@playwright/test';

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
        !e.includes('favicon')
    );
}

// ── Test config ──────────────────────────────────────────────────────

interface DashboardPage {
  path: string;
  name: string;
  expectedClasses: string[];
  forbiddenClasses: string[];
  role: 'student' | 'instructor' | 'admin';
}

const DASHBOARD_PAGES: DashboardPage[] = [
  {
    path: '/dashboard',
    name: 'Main Dashboard',
    expectedClasses: ['btn-primary'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/courses',
    name: 'Courses List',
    expectedClasses: ['btn-primary', 'card'],
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
    expectedClasses: ['btn-primary'],
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
    expectedClasses: ['btn-primary'],
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
    expectedClasses: ['btn-primary'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'student',
  },
  {
    path: '/dashboard/student-manage',
    name: 'Student Management',
    expectedClasses: ['btn-primary'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/withdraw',
    name: 'Withdraw',
    expectedClasses: ['btn-primary', 'input-field'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/announcement',
    name: 'Announcement',
    expectedClasses: ['btn-primary'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/assignment',
    name: 'Assignment',
    expectedClasses: ['btn-primary'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'instructor',
  },
  {
    path: '/dashboard/admin/withdrawals',
    name: 'Admin Withdrawals',
    expectedClasses: ['btn-primary'],
    forbiddenClasses: FORBIDDEN_CLASSES,
    role: 'admin',
  },
];

// ── Tests ────────────────────────────────────────────────────────────

for (const pageConfig of DASHBOARD_PAGES) {
  const fixtureName =
    pageConfig.role === 'admin' ? 'adminPage' :
    pageConfig.role === 'instructor' ? 'instructorPage' :
    'studentPage';

  test.describe(`${pageConfig.name} (${pageConfig.path}) — CTC Teal Theme`, () => {
    test(`renders with CTC teal theme (role: ${pageConfig.role})`, async ({
      [fixtureName]: page,
    }: Record<string, Page>) => {
      const getErrors = captureConsoleErrors(page);

      // Navigate with auth mocked
      const response = await page.goto(pageConfig.path, {
        waitUntil: 'networkidle',
        timeout: 15000,
      });

      // Assertion 1: HTTP 200
      expect(response?.status(), `${pageConfig.name} should return 200`).toBe(200);

      // Wait for any loading skeletons to disappear
      await page.waitForTimeout(1000);

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
  });
}

// ── Cross-page consistency ──────────────────────────────────────────

test.describe('Cross-page CTC Theme Consistency', () => {
  test('CTC primary CSS variables are defined', async ({ studentPage }) => {
    await studentPage.goto('/dashboard', { waitUntil: 'networkidle' });

    const ctcPrimary = await studentPage.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue('--ctc-primary').trim()
    );
    const ctcPrimaryDark = await studentPage.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue('--ctc-primary-dark').trim()
    );

    expect(ctcPrimary).toBe('0 161 179');
    expect(ctcPrimaryDark).toBe('0 122 136');
  });

  test('btn-primary renders with CTC teal background', async ({ studentPage }) => {
    await studentPage.goto('/dashboard', { waitUntil: 'networkidle' });

    const btn = studentPage.locator('.btn-primary').first();
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

const FORBIDDEN_CLASSES = ['indigo-', 'purple-'];



const PUBLIC_PAGES: PublicPage[] = [
  { path: '/', name: 'Homepage', expectedClasses: ['btn-primary', 'card'] },
  { path: '/login', name: 'Login', expectedClasses: ['btn-primary', 'input-field'] },
  { path: '/registration', name: 'Registration', expectedClasses: ['btn-primary', 'input-field'] },
  { path: '/courses', name: 'Courses', expectedClasses: ['btn-primary', 'card'] },
  { path: '/about-us', name: 'About Us', expectedClasses: ['btn-primary', 'card'] },
  { path: '/contact', name: 'Contact', expectedClasses: ['btn-primary', 'input-field'] },
  { path: '/faq', name: 'FAQ', expectedClasses: ['btn-primary', 'card'] },
  { path: '/instructors', name: 'Instructors', expectedClasses: ['card'] },
  { path: '/cart', name: 'Cart', expectedClasses: ['btn-primary', 'card'] },
  { path: '/blog', name: 'Blog', expectedClasses: ['btn-primary', 'card'] },
  { path: '/shop', name: 'Shop', expectedClasses: ['btn-primary', 'card'] },
  { path: '/privacy', name: 'Privacy', expectedClasses: ['card'] },
  { path: '/events', name: 'Events', expectedClasses: ['btn-primary', 'card'] },
];

test.describe('Public Pages — CTC Teal Theme', () => {
  for (const pageConfig of PUBLIC_PAGES) {
    test(`${pageConfig.name} (${pageConfig.path}) renders with CTC teal theme`, async ({ page }) => {
      const getErrors = captureConsoleErrors(page);

      // Navigate (no auth needed for public pages)
      const response = await page.goto(pageConfig.path, {
        waitUntil: 'networkidle',
        timeout: 15000,
      });

      // Assertion 1: HTTP 200
      expect(response?.status(), `${pageConfig.name} should return 200`).toBe(200);

      await page.waitForTimeout(1000);

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
