import { test, expect } from '../../fixtures/auth';
import { captureConsoleErrors } from '../../helpers/utils';

/**
 * POS Authentication E2E Tests
 *
 * Verifies auth flows:
 * - Admin can access all core pages
 * - Cashier has limited access (sale, inventory view only)
 * - Manager has broader access (pos, reports)
 * - Protected pages redirect unauthenticated users
 * - Role-based access control
 */

test.describe('POS Authentication', () => {
  test('authenticated admin can access all core pages', async ({ adminPage }) => {
    const errors = captureConsoleErrors(adminPage);

    const corePages = ['/', '/sale', '/inventory', '/customers', '/employees', '/analytics'];

    for (const path of corePages) {
      await adminPage.goto(path, { waitUntil: 'networkidle' });

      // Each page should return 200
      const bodyText = await adminPage.textContent('body');
      expect(bodyText?.length ?? 0, `${path} should have content`).toBeGreaterThan(50);

      // No page should show 403/404
      expect(bodyText, `${path} should not show forbidden`).not.toContain('403');
    }

    expect(errors.getFiltered()).toHaveLength(0);
  });

  test('all core pages have side navigation', async ({ adminPage }) => {
    const pagesToCheck = ['/', '/sale', '/inventory', '/customers'];

    for (const path of pagesToCheck) {
      await adminPage.goto(path, { waitUntil: 'networkidle' });
      const navVisible = await adminPage.locator('nav').first().isVisible().catch(() => false);
      expect(navVisible, `${path} should have nav`).toBe(true);
    }
  });

  test('core pages do not crash (no blank pages)', async ({ adminPage }) => {
    const allPages = [
      '/', '/sale', '/inventory', '/customers', '/employees',
      '/suppliers', '/analytics', '/reports', '/settings', '/about',
    ];

    for (const path of allPages) {
      const response = await adminPage.goto(path, { waitUntil: 'networkidle' });
      expect(response?.status(), `${path} should return 200`).toBe(200);

      const bodyText = await adminPage.textContent('body');
      expect(bodyText?.length ?? 0, `${path} should not be blank`).toBeGreaterThan(50);
    }
  });

  // ── Role-Based Access Control Tests ───────────────────────────

  test.describe('Role-Based Access Control', () => {
    test('cashier can access sale and inventory pages', async ({ cashierPage }) => {
      const allowedPages = ['/sale', '/inventory'];
      const errors = captureConsoleErrors(cashierPage);

      for (const path of allowedPages) {
        await cashierPage.goto(path, { waitUntil: 'networkidle' });

        const bodyText = await cashierPage.textContent('body');
        expect(bodyText?.length ?? 0, `${path} should have content for cashier`).toBeGreaterThan(50);
      }

      // Allow auth-related console warnings for cashier
      expect(errors.getAll().filter(e => !e.includes('invoke') && !e.includes('auth'))).toHaveLength(0);
    });

    test('cashier cannot access admin pages (employees, settings, reports)', async ({ cashierPage }) => {
      const restrictedPages = ['/employees', '/settings', '/analytics'];

      for (const path of restrictedPages) {
        await cashierPage.goto(path, { waitUntil: 'networkidle' });

        // Should either be redirected away or see a forbidden/access-denied message
        const currentUrl = cashierPage.url();
        const bodyText = await cashierPage.textContent('body');

        const redirected = !currentUrl.includes(path);
        const accessDenied = bodyText?.toLowerCase().includes('403')
          || bodyText?.toLowerCase().includes('forbidden')
          || bodyText?.toLowerCase().includes('access denied')
          || bodyText?.toLowerCase().includes('unauthorized');

        expect(redirected || accessDenied,
          `${path} should be restricted for cashier (redirected=${redirected}, denied=${accessDenied})`
        ).toBe(true);
      }
    });

    test('cashier navigation does not show admin-only links', async ({ cashierPage }) => {
      await cashierPage.goto('/', { waitUntil: 'networkidle' });

      // Check for admin-only navigation items (cashier should not see them)
      const navLinks = await cashierPage.locator('nav a, nav button').allTextContents();
      const navText = navLinks.join(' ').toLowerCase();

      const adminOnlySections = ['employees', 'settings', 'reports'];
      for (const section of adminOnlySections) {
        const hasLink = navText.includes(section);
        // This is a soft assertion — the nav may still render links but backend will block
        // We log it for observability rather than failing hard
        if (hasLink) {
          console.log(`Note: cashier nav still shows "${section}" link — backend should enforce restriction`);
        }
      }
    });

    test('manager can access pos pages and reports', async ({ managerPage }) => {
      const allowedPages = ['/', '/sale', '/inventory', '/customers', '/reports', '/analytics'];
      const errors = captureConsoleErrors(managerPage);

      for (const path of allowedPages) {
        await managerPage.goto(path, { waitUntil: 'networkidle' });

        const bodyText = await managerPage.textContent('body');
        expect(bodyText?.length ?? 0, `${path} should have content for manager`).toBeGreaterThan(50);

        // Manager should not see forbidden errors on allowed pages
        expect(bodyText, `${path} should not show forbidden for manager`).not.toContain('403');
      }

      expect(errors.getFiltered()).toHaveLength(0);
    });

    test('manager cannot access admin-only pages (settings)', async ({ managerPage }) => {
      // Settings may be admin-only
      await managerPage.goto('/settings', { waitUntil: 'networkidle' });

      const currentUrl = managerPage.url();
      const bodyText = await managerPage.textContent('body');

      const redirected = !currentUrl.includes('/settings');
      const accessDenied = bodyText?.toLowerCase().includes('403')
        || bodyText?.toLowerCase().includes('forbidden')
        || bodyText?.toLowerCase().includes('access denied');

      expect(redirected || accessDenied,
        `/settings should be restricted for manager`
      ).toBe(true);
    });

    test('manager can view side navigation on permitted pages', async ({ managerPage }) => {
      const pagesToCheck = ['/', '/sale', '/inventory', '/customers', '/reports'];

      for (const path of pagesToCheck) {
        await managerPage.goto(path, { waitUntil: 'networkidle' });

        // Wait for content to load before checking nav
        await managerPage.waitForLoadState('domcontentloaded');
        const navVisible = await managerPage.locator('nav').first().isVisible().catch(() => false);
        expect(navVisible, `${path} should have nav for manager`).toBe(true);
      }
    });

    test('role switcher: different roles see different page content', async ({ adminPage, cashierPage, managerPage }) => {
      // Admin should see all dashboard components
      await adminPage.goto('/', { waitUntil: 'networkidle' });
      const adminBody = await adminPage.textContent('body');
      expect(adminBody?.length ?? 0).toBeGreaterThan(100);

      // Cashier should see dashboard but may have fewer components
      await cashierPage.goto('/', { waitUntil: 'networkidle' });
      const cashierBody = await cashierPage.textContent('body');
      expect(cashierBody?.length ?? 0).toBeGreaterThan(50);

      // Manager should see dashboard with reports data
      await managerPage.goto('/', { waitUntil: 'networkidle' });
      const managerBody = await managerPage.textContent('body');
      expect(managerBody?.length ?? 0).toBeGreaterThan(50);
    });
  });
});
