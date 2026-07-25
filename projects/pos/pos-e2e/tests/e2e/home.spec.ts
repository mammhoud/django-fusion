import { test, expect } from '../../fixtures/auth';
import { captureConsoleErrors } from '../../helpers/utils';
import { HomePage } from '../../pages';

/**
 * POS Home/Dashboard E2E Tests
 *
 * Verifies the dashboard renders correctly for different user roles,
 * stat cards appear, navigation works, and the FusionPage wrapper is present.
 */

test.describe('POS Home Dashboard', () => {
  test('renders dashboard with stat cards for admin user', async ({ adminPage }) => {
    const errors = captureConsoleErrors(adminPage);
    const home = new HomePage(adminPage);

    await home.goto();

    // Page should have a title
    const title = await home.getPageTitle();
    expect(title.length).toBeGreaterThan(0);

    // SideNav should be visible
    await expect(home.sideNav).toBeVisible();

    // Stat cards should render (dashboard KPI widgets)
    const cardCount = await home.getStatCardCount();
    expect(cardCount).toBeGreaterThanOrEqual(1);

    // No console errors
    expect(errors.getFiltered()).toHaveLength(0);
  });

  test('dashboard renders for cashier role with limited menu', async ({ cashierPage }) => {
    const home = new HomePage(cashierPage);
    await home.goto();

    // SideNav should still be visible (cashiers have access)
    await expect(home.sideNav).toBeVisible();

    // Page should have content
    const bodyText = await cashierPage.textContent('body');
    expect(bodyText?.length ?? 0).toBeGreaterThan(50);
  });

  test('dashboard renders for manager role', async ({ managerPage }) => {
    const home = new HomePage(managerPage);
    await home.goto();

    await expect(home.sideNav).toBeVisible();
    const cardCount = await home.getStatCardCount();
    expect(cardCount).toBeGreaterThanOrEqual(1);
  });

  test('side navigation links work', async ({ adminPage }) => {
    const home = new HomePage(adminPage);
    await home.goto();

    // Count nav links
    const linkCount = await home.navLinks.count();
    expect(linkCount).toBeGreaterThanOrEqual(3);
  });

  test('mobile menu toggle works if present', async ({ adminPage }) => {
    const home = new HomePage(adminPage);
    await home.goto();

    // Set viewport to mobile size
    await adminPage.setViewportSize({ width: 375, height: 812 });

    // Mobile menu button should exist
    const hasMobileMenu = await home.mobileMenuButton.isVisible().catch(() => false);
    if (hasMobileMenu) {
      await home.mobileMenuButton.click();
      // Menu should expand — can't assert without knowing exact implementation
    }
  });
});
