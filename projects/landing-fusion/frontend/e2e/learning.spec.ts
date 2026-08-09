import { expect, test } from '@playwright/test';
import { BACKEND_URL } from '../playwright.config';

/**
 * Learning — catalog, course dossier (rating/reviews/resources) and the
 * auth-gated lesson reader, served by the Django backend road.
 */
const COURSE_PATH = '/learning/course/ship-django-products/';

test('catalog renders the hero and course cards', async ({ page }) => {
  const response = await page.goto('/learning/');
  expect(response?.status()).toBe(200);

  await expect(page.locator('.learning-hero__title')).toBeVisible();
  const cards = page.locator('.learning-course-card');
  await expect(cards.first()).toBeVisible();
  // Featured card links into the dossier road.
  const detailLink = page.locator('a[href*="/learning/course/"]').first();
  await expect(detailLink).toHaveAttribute('href', /\/learning\/course\//);
});

test('course dossier surfaces rating, resources and reviews', async ({ page }) => {
  const response = await page.goto(COURSE_PATH);
  expect(response?.status()).toBe(200);

  // Hero metric hooks from the enriched dossier.
  await expect(page.locator('[data-course-rating="5.0"]').first()).toBeVisible();
  const resources = await page
    .locator('[data-course-resources-count]')
    .first()
    .getAttribute('data-course-resources-count');
  expect(Number(resources)).toBeGreaterThanOrEqual(1);

  // Reviews section (published only).
  const reviewSection = page.locator('section:has-text("Course reviews"), .learning-reviews');
  await expect(reviewSection.first()).toBeVisible();
});

test('lesson reader is auth-gated and redirects to login', async ({ page, request }) => {
  // Anonymous access must NOT render the reader — the backend 302s to login.
  const direct = await request.get(`${BACKEND_URL}${COURSE_PATH}lesson/1/`, {
    maxRedirects: 0,
  });
  expect(direct.status()).toBe(302);
  const location = direct.headers()['location'] || '';
  expect(location).toContain('/accounts/login/');

  // Browser road follows the redirect to the allauth login page.
  await page.goto(`${COURSE_PATH}lesson/1/`);
  await page.waitForURL(/\/accounts\/login\//, { timeout: 10_000 });
  expect(page.url()).toContain('next=');
});

test('learning API course payload is typed and complete', async ({ request }) => {
  const response = await request.get(`${BACKEND_URL}/apis/courses/`);
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(Array.isArray(body.courses)).toBe(true);
  expect(body.courses.length).toBeGreaterThanOrEqual(1);

  const first = body.courses[0];
  for (const key of ['slug', 'title', 'price', 'duration_hours', 'difficulty', 'language']) {
    expect(first, `course payload should include ${key}`).toHaveProperty(key);
  }
  // Superset fields from the enriched serializer.
  for (const key of ['module_count', 'lesson_count', 'is_free', 'is_featured', 'has_certificate', 'href']) {
    expect(first, `course payload should include ${key}`).toHaveProperty(key);
  }
});
