import { expect, test } from '@playwright/test';

/**
 * Site shell — home, header/footer, theme toggle, 404 road.
 * Runs against the compose frontend (default :3001).
 */

test('home renders the hero, header nav and footer', async ({ page }) => {
  const response = await page.goto('/');
  expect(response?.status()).toBe(200);

  await expect(page.locator('h1').first()).toBeVisible();
  await expect(page.locator('header nav a').first()).toBeVisible();
  const footerCount = await page.locator('footer').count();
  expect(footerCount).toBeGreaterThanOrEqual(1);
  const navLinkCount = await page.locator('header nav a').count();
  expect(navLinkCount).toBeGreaterThan(3);
  await expect(page.locator('[data-testid="home-slider"]')).toBeVisible();
  // Wagtail-driven slider: at least 2 seeded slides — editors may add or
  // remove slides in the CMS, so assert a minimum rather than a fixed count.
  expect(await page.locator('[data-testid="home-slide"]').count()).toBeGreaterThanOrEqual(2);
});

test('home slider advances through content and keeps controls accessible', async ({ page }) => {
  await page.goto('/');
  const slider = page.locator('[data-testid="home-slider"]');
  const firstTitle = await slider.locator('[data-testid="home-slide"]').first().locator('h3').textContent();
  await slider.getByRole('button', { name: 'Next research slide' }).click();
  await expect.poll(() => slider.locator('.home-slider__track').evaluate((node) => getComputedStyle(node).transform)).not.toBe('none');
  const activeDot = slider.locator('.home-slider__dot[aria-current="true"]');
  await expect(activeDot).toHaveCount(1);
  expect(firstTitle?.trim()).toBeTruthy();
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
  // Choice persists to localStorage.
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

test('backend-driven marketing routes render Wagtail content', async ({ page }) => {
  // Each static route is powered by a seeded Wagtail MarketingPage — the
  // baked page must render real backend copy, not an empty section.
  const routes = [
    { path: '/faq/', expect: 'Do I need a medical background to join a course?' },
    { path: '/pricing/', expect: 'Explorer' },
    { path: '/features/', expect: 'Evidence Methods Support' },
    { path: '/projects/', expect: 'Systematic Review Studio' },
    { path: '/products/', expect: 'Research Methods Library' },
  ];
  for (const route of routes) {
    const response = await page.goto(route.path, { waitUntil: 'domcontentloaded' });
    expect(response?.status(), `${route.path} should be 200`).toBe(200);
    await expect(page.locator('body')).toContainText(route.expect);
  }
});
