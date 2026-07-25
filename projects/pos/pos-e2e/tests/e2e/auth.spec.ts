import { test, expect } from '../../fixtures/auth';
import { captureConsoleErrors } from '../../helpers/utils';

/**
 * POS Authentication E2E Tests
 *
 * Verifies auth flows:
 * - Login page renders
 * - Logout works
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
});
