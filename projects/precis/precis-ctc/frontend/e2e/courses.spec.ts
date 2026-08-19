import { expect, test, type APIRequestContext } from '@playwright/test';
import { BACKEND_URL } from '../playwright.config';

/**
 * Courses — backend catalog contract plus the Astro catalog/detail surfaces.
 * The backend may expose translated slugs, so detail coverage follows the
 * first published course returned by the current catalog instead of assuming
 * one historical seed slug.
 */

async function fetchCatalog(request: APIRequestContext) {
  const response = await request.get(`${BACKEND_URL}/api/courses/?per_page=50`);
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(Array.isArray(body.data)).toBe(true);
  expect(body.data.length).toBeGreaterThan(0);
  return body;
}

test('backend catalog returns the published course collection', async ({ request }) => {
  const body = await fetchCatalog(request);
  expect(body.pagination.total).toBeGreaterThanOrEqual(body.data.length);
  for (const course of body.data.slice(0, 6)) {
    expect(String(course.slug)).toMatch(/^[a-z0-9][a-z0-9-]*$/);
    expect(String(course.title).length).toBeGreaterThan(5);
    expect(String(course.short_description).length).toBeGreaterThan(10);
  }
});

test('backend course detail returns modules for a published course', async ({ request }) => {
  const catalog = await fetchCatalog(request);
  const slug = catalog.data[0].slug;
  const response = await request.get(`${BACKEND_URL}/api/courses/${slug}/`);
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body.slug).toBe(slug);
  expect(typeof body.description).toBe('string');
  expect(Array.isArray(body.modules)).toBe(true);
});

test('frontend /courses/ page lists courses', async ({ page }) => {
  const response = await page.goto('/courses/');
  expect(response?.status()).toBe(200);
  await expect(page.locator('h1')).toContainText(/build evidence|course/i);
  const courseLinks = await page.locator('a[href*="/courses/"], a[href*="/learning/"]').count();
  expect(courseLinks).toBeGreaterThanOrEqual(1);
});

test('frontend course detail renders the live learning path and enrollment facts', async ({ page, request }) => {
  const catalog = await fetchCatalog(request);
  const course = catalog.data[0];
  const response = await page.goto(`/courses/${course.slug}/`);
  expect(response?.status()).toBe(200);
  await expect(page.locator('h1')).toContainText(new RegExp(String(course.title).split(/\s+/).slice(0, 2).join('|'), 'i'));
  await expect(page.getByText('course overview', { exact: true })).toBeVisible();
  await expect(page.getByText('learning path', { exact: true })).toBeVisible();
  expect(await page.locator('.syllabus-accordion__item').count()).toBeGreaterThan(0);
});

test.fixme('frontend shell executes the shared fusion bundle', async ({ page }) => {
  await page.goto('/');
  await expect
    .poll(() => page.evaluate(() => (window as { __FUSION__?: boolean }).__FUSION__ === true))
    .toBe(true);
});
