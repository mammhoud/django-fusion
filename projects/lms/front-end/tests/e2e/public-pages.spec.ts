import { test, expect } from '../fixtures/auth';
import type { Page } from '@playwright/test';

/**
 * Public Pages E2E Tests — LMS Front-End
 *
 * Tests all public-facing pages (no auth required):
 * - Homepage
 * - Courses listing
 * - Course details
 * - About us
 * - Contact
 * - FAQ
 * - Instructors
 * - Login / Registration
 * - Blog
 * - Shop
 *
 * These tests validate:
 * - Pages render without errors
 * - Key UI elements are present
 * - CTC teal theme is applied
 * - No console errors
 */

// ── Helpers ──────────────────────────────────────────────────────────

function captureErrors(page: Page) {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  return () =>
    errors.filter(
      (e) =>
        !e.includes('hydration') &&
        !e.includes('Warning:') &&
        !e.includes('next') &&
        !e.includes('favicon')
    );
}

// ── Public page config ───────────────────────────────────────────────

const PUBLIC_PAGES = [
  { path: '/', name: 'Homepage', minHeadingCount: 1, expectedClasses: ['btn-primary'] },
  { path: '/courses', name: 'Courses', minHeadingCount: 1, expectedClasses: ['card', 'btn-primary'] },
  { path: '/about-us', name: 'About Us', minHeadingCount: 1, expectedClasses: ['btn-primary'] },
  { path: '/contact', name: 'Contact', minHeadingCount: 1, expectedClasses: ['btn-primary', 'input-field'] },
  { path: '/faq', name: 'FAQ', minHeadingCount: 1, expectedClasses: ['btn-primary'] },
  { path: '/instructors', name: 'Instructors', minHeadingCount: 1, expectedClasses: ['card'] },
  { path: '/login', name: 'Login', minHeadingCount: 1, expectedClasses: ['btn-primary', 'input-field'] },
  { path: '/registration', name: 'Registration', minHeadingCount: 1, expectedClasses: ['btn-primary', 'input-field'] },
  { path: '/cart', name: 'Cart', minHeadingCount: 1, expectedClasses: ['btn-primary'] },
] as const;

// ── Tests ────────────────────────────────────────────────────────────

for (const { path, name, expectedClasses } of PUBLIC_PAGES) {
  test.describe(`${name} (${path})`, () => {
    test('renders without errors', async ({ page }) => {
      const getErrors = captureErrors(page);

      const response = await page.goto(path, {
        waitUntil: 'networkidle',
        timeout: 15000,
      });

      expect(response?.status(), `${name} should return 200`).toBe(200);

      // Should have page content
      const bodyText = await page.textContent('body');
      expect(bodyText?.length ?? 0, `${name} should have content`).toBeGreaterThan(50);

      // No 404
      expect(bodyText?.includes('404') && bodyText?.includes('Not Found'), `${name} should not be 404`).toBe(false);

      // No console errors
      expect(getErrors(), `${name} should have no console errors`).toHaveLength(0);
    });

    test('has CTC teal theme classes applied', async ({ page }) => {
      await page.goto(path, { waitUntil: 'networkidle', timeout: 15000 });
      const html = await page.content();

      for (const cls of expectedClasses) {
        expect(html.includes(cls), `${name} should contain CSS class "${cls}"`).toBe(true);
      }

      // No forbidden old-theme classes
      expect(html.includes('indigo-'), `${name} should NOT contain indigo-`).toBe(false);
      expect(html.includes('purple-'), `${name} should NOT contain purple-`).toBe(false);
    });

    test('has a visible heading', async ({ page }) => {
      await page.goto(path, { waitUntil: 'networkidle', timeout: 15000 });
      const headings = page.locator('h1');
      const count = await headings.count();
      expect(count, `${name} should have at least one h1`).toBeGreaterThanOrEqual(1);
    });
  });
}

// ── Specific page tests ──────────────────────────────────────────────

test.describe('Homepage', () => {
  test('has hero section with CTA', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle', timeout: 15000 });

    // Hero section should have a heading and CTA button
    const heroHeading = page.locator('h1').first();
    await expect(heroHeading).toBeVisible();
    expect(await heroHeading.textContent()).toBeTruthy();

    // At least one CTA link/button
    const ctaButton = page.locator('a[href*="/courses"], a[href*="/registration"]').first();
    await expect(ctaButton).toBeVisible();
  });

  test('has feature/service cards', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle', timeout: 15000 });

    const serviceCards = page.locator('.service-card, .stat-card, .card');
    const count = await serviceCards.count();
    expect(count).toBeGreaterThanOrEqual(2);
  });
});

test.describe('Courses Page', () => {
  test('displays course cards', async ({ page }) => {
    await page.goto('/courses', { waitUntil: 'networkidle', timeout: 15000 });

    const courseCards = page.locator('.card-hover, .card');
    const count = await courseCards.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });
});

test.describe('Login Page', () => {
  test('has email and password fields', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle', timeout: 15000 });

    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();

    const submitBtn = page.locator('button[type="submit"]');
    await expect(submitBtn).toBeVisible();
  });

  test('has link to registration page', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle', timeout: 15000 });

    const signUpLink = page.locator('a[href="/registration"]').first();
    await expect(signUpLink).toBeVisible();
  });
});

test.describe('Registration Page', () => {
  test('has role selection buttons', async ({ page }) => {
    await page.goto('/registration', { waitUntil: 'networkidle', timeout: 15000 });

    const studentBtn = page.getByRole('button', { name: /student/i });
    const instructorBtn = page.getByRole('button', { name: /instructor/i });

    const hasStudent = await studentBtn.isVisible().catch(() => false);
    const hasInstructor = await instructorBtn.isVisible().catch(() => false);
    expect(hasStudent || hasInstructor).toBe(true);
  });
});
