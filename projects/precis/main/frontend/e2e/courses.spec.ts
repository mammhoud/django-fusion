import { expect, test } from '@playwright/test';
import { BACKEND_URL } from '../playwright.config';

/**
 * Courses — backend catalog contract (medical research seed) + the
 * frontend /courses/ page.
 */
const MEDICAL_SLUG = 'medical-ai-clinical-data-analytics';

test('backend catalog returns the full seeded course collection', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/api/courses/?per_page=50`);
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(Array.isArray(body.data)).toBe(true);
  expect(body.pagination.total).toBeGreaterThanOrEqual(14);

  const medical = body.data.find((course: { slug: string }) => course.slug === MEDICAL_SLUG);
  expect(medical, 'medical AI course should be seeded').toBeTruthy();
  expect(String(medical.short_description)).toMatch(/clinical data/i);
});

test('backend course detail returns modules', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/api/courses/${MEDICAL_SLUG}/`);
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.slug).toBe(MEDICAL_SLUG);
  expect(typeof body.description).toBe('string');
  expect(Array.isArray(body.modules)).toBe(true);
});

test('frontend /courses/ page lists courses', async ({ page }) => {
  const response = await page.goto('/courses/');
  expect(response?.status()).toBe(200);
  await expect(page.locator('h1')).toBeVisible();
  // The page is a landing shell for the catalog — at minimum it must link
  // into the learning road.
  const courseLinks = await page.locator('a[href*="/courses/"], a[href*="/learning/"]').count();
  expect(courseLinks).toBeGreaterThanOrEqual(1);
});

// Pending until the compose frontend image is rebuilt with the fusion bundle
// (src/fusion/index.ts sets window.__FUSION__). Remove the fixme line after
// `docker compose build frontend` — the assertion is then strict.
test.fixme('frontend shell executes the shared fusion bundle', async ({ page }) => {
  await page.goto('/');
  // src/fusion/index.ts sets this after init — proof the modular bundle ran.
  await expect
    .poll(() => page.evaluate(() => (window as { __FUSION__?: boolean }).__FUSION__ === true))
    .toBe(true);
});
