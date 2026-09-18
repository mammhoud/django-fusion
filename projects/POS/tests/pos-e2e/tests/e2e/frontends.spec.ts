import { test, expect } from '@playwright/test';

/**
 * Cross-edition frontend smoke + interaction. One spec, one Playwright project
 * per edition — each project boots its own dev server and points `baseURL` at
 * it, so `page.goto('/')` visits that edition's home route.
 *
 * Deeper per-edition flow tests stay in each edition's own `test:e2e` suite;
 * this shared spec asserts every edition boots and serves an interactive home
 * screen, and captures a screenshot for the docs.
 */

const SHOTS = '../../docs/screenshots';

test('home renders and captures a screenshot', async ({ page }, testInfo) => {
  const project = testInfo.project.name;

  const resp = await page.goto('/');
  // Dev servers return 200 for the SPA/MPA entry; a hard failure (500) is a
  // real regression. Some static shells may return 404 for a missing route,
  // which is also a failure here.
  expect(resp && resp.status() < 400).toBeTruthy();

  // Every edition renders a visible shell (app root, header, or body content).
  await expect(page.locator('body')).toBeVisible();
  await page.waitForTimeout(500);

  await page.screenshot({ path: `${SHOTS}/frontend/${project}-home.png`, fullPage: true });

  // Light interaction: if there is a *visible* nav link, click it and confirm
  // the page still serves without a hard error. This exercises the MPA/SPA
  // router. Some editions render off-canvas/desktop-only links, so filter to
  // visible elements before clicking.
  const navLink = page.locator('header a[href], nav a[href]').filter({ visible: true }).first();
  if ((await navLink.count()) > 0 && (await navLink.isVisible().catch(() => false))) {
    await navLink.click();
    await expect(page.locator('body')).toBeVisible();
    await page.screenshot({ path: `${SHOTS}/frontend/${project}-nav.png`, fullPage: true });
  }
});
