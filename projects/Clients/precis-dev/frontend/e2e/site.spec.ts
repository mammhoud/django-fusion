import { expect, test } from '@playwright/test';

/**
 * Site shell — home, header/footer, theme toggle, 404 road.
 * Runs against the Astro dev server (default :3000, proxies to :8074).
 */

test('home renders hero, header nav and footer', async ({ page }) => {
  const response = await page.goto('/');
  expect(response?.status()).toBe(200);

  await expect(page.locator('h1').first()).toBeVisible();
  await expect(page.locator('header nav a').first()).toBeVisible();
  const footerCount = await page.locator('footer').count();
  expect(footerCount).toBeGreaterThanOrEqual(1);
  const navLinkCount = await page.locator('header nav a').count();
  expect(navLinkCount).toBeGreaterThan(3);
});

test('theme toggle flips the html dark/light class', async ({ page }) => {
  await page.goto('/');
  // Desktop + mobile headers both render the toggle — use the first.
  const toggle = page.locator('button[title="Toggle light / dark mode"]').first();
  await expect(toggle).toBeVisible();

  const before = await page.evaluate(() => document.documentElement.classList.contains('dark'));
  await toggle.click();
  await expect
    .poll(() => page.evaluate(() => document.documentElement.classList.contains('dark')))
    .not.toBe(before);
  const stored = await page.evaluate(() => localStorage.getItem('fusion-theme'));
  expect(stored).toBe(before ? 'light' : 'dark');
});

test('unknown routes return the 404 page', async ({ page }) => {
  const response = await page.goto('/this-page-does-not-exist-xyz/', { waitUntil: 'domcontentloaded' });
  expect(response?.status()).toBe(404);
});

test('header navigation links resolve', async ({ page }) => {
  await page.goto('/');
  const hrefs = await page.locator('header nav a[href]').evaluateAll((nodes) =>
    nodes.map((node) => (node as HTMLAnchorElement).getAttribute('href')).filter(Boolean) as string[],
  );
  expect(hrefs.length).toBeGreaterThan(3);
  for (const href of hrefs.slice(0, 6)) {
    const res = await page.request.get(href);
    expect(res.status(), `nav link ${href} should resolve`).toBeLessThan(500);
  }
});
