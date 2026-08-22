import { expect, test, type APIRequestContext } from '@playwright/test';
import { BACKEND_URL } from '../playwright.config';

/**
 * Scroll-reveal regression — the course detail `.reveal-up` sections.
 *
 * Guards against the CSS specificity bug where the hidden rule
 * `.js .reveal-up` (two classes) out-specified the single-class visible
 * rule `.reveal-up--visible`, leaving every section at `opacity: 0` even
 * after the IntersectionObserver added the visible class. The visible rule
 * must now be `.js .reveal-up.reveal-up--visible` (three classes).
 *
 * The assertion checks the *computed* opacity rather than Playwright's
 * visibility: `toBeVisible()` ignores `opacity`, so a stuck element would
 * pass a visibility check but fail here.
 */

async function fetchCourseSlug(request: APIRequestContext): Promise<string> {
  const response = await request.get(`${BACKEND_URL}/api/courses/?per_page=50`);
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(Array.isArray(body.data)).toBe(true);
  expect(body.data.length).toBeGreaterThan(0);
  return body.data[0].slug as string;
}

test('course detail reveal sections reach full opacity when scrolled into view', async ({ page, request }) => {
  const slug = await fetchCourseSlug(request);
  const response = await page.goto(`/courses/${slug}/`, {
    waitUntil: 'commit',
    timeout: 60_000,
  });
  expect(response?.status()).toBe(200);

  const count = await page.locator('.reveal-up').count();
  expect(count, 'the course page should render at least one reveal section').toBeGreaterThan(0);

  for (let i = 0; i < count; i++) {
    const section = page.locator('.reveal-up').nth(i);
    // Center the section in the viewport: `scrollIntoViewIfNeeded` stops as
    // soon as the element touches the viewport edge, which can leave it in
    // the observer's `rootMargin: -40px` dead zone where it never intersects
    // and therefore never reveals.
    await section.evaluate((node) => node.scrollIntoView({ block: 'center' }));
    await expect
      .poll(
        () => section.evaluate((node) => getComputedStyle(node).opacity),
        { timeout: 10_000, message: `reveal section ${i + 1}/${count} should reach opacity 1` },
      )
      .toBe('1');
  }
});
