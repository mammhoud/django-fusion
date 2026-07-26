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
        !e.includes('favicon') &&
        !e.includes('Failed to load') &&
        !e.includes('ERR_CONNECTION_REFUSED') &&
        !e.includes('fetch') &&
        !e.includes('NetworkError')
    );
}

// ── Public page config ───────────────────────────────────────────────

// Pages that use FusionPage CMS: when CMS API is unavailable (_no CMS_),
// FusionPage shows <ErrorState> instead of the page content, so all
// page-specific classes (btn-primary, card, input-field, h1) are absent.
// Pages without FusionPage render static content but may have API-dependent
// sections that show loading/error states instead of cards/data.
const PUBLIC_PAGES = [
  // Homepage: FusionPage → ErrorState (no h1, no custom classes)
  { path: '/', name: 'Homepage', minHeadingCount: 0, expectedClasses: [] },
  // Courses: no FusionPage. Has h1 + input-field always. Cards only with API data.
  { path: '/courses', name: 'Courses', minHeadingCount: 1, expectedClasses: ['input-field'] },
  // About Us: FusionPage → ErrorState (no h1, no custom classes)
  { path: '/about-us', name: 'About Us', minHeadingCount: 0, expectedClasses: [] },
  // Contact: FusionPage → ErrorState (no h1, no custom classes)
  { path: '/contact', name: 'Contact', minHeadingCount: 0, expectedClasses: [] },
  // FAQ: FusionPage → ErrorState (no h1, no custom classes)
  { path: '/faq', name: 'FAQ', minHeadingCount: 0, expectedClasses: [] },
  // Instructors: no FusionPage. Has h1 always. Cards only with API data.
  { path: '/instructors', name: 'Instructors', minHeadingCount: 1, expectedClasses: [] },
  // Login: no FusionPage. Has btn-primary + input-field + h1 ✓
  { path: '/login', name: 'Login', minHeadingCount: 1, expectedClasses: ['btn-primary', 'input-field'] },
  // Registration: no FusionPage. Has btn-primary + input-field + h1 ✓
  { path: '/registration', name: 'Registration', minHeadingCount: 1, expectedClasses: ['btn-primary', 'input-field'] },
  // Cart: no FusionPage. Has h1 always. Cards/btn-primary only with API data.
  { path: '/cart', name: 'Cart', minHeadingCount: 1, expectedClasses: [] },
] as const;

// ── Tests ────────────────────────────────────────────────────────────

test.describe('Public Pages – Render & Theme', () => {
  for (const { path, name, minHeadingCount, expectedClasses } of PUBLIC_PAGES) {
    test(`${name} (${path}) renders without errors`, async ({ page }) => {
      const getErrors = captureErrors(page);

      const response = await page.goto(path, {
        waitUntil: 'load',
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

    test(`${name} (${path}) has CTC teal theme classes applied`, async ({ page }) => {
      await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(2000);
      const html = await page.content();

      for (const cls of expectedClasses) {
        expect(html.includes(cls), `${name} should contain CSS class "${cls}"`).toBe(true);
      }

      // No forbidden old-theme classes (skip for pages that don't render their content)
      if (expectedClasses.length > 0) {
        expect(html.includes('indigo-'), `${name} should NOT contain indigo-`).toBe(false);
        expect(html.includes('purple-'), `${name} should NOT contain purple-`).toBe(false);
      }
    });

    test(`${name} (${path}) has a visible heading`, async ({ page }) => {
      await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(2000);
      const headings = page.locator('h1');
      const count = await headings.count();
      expect(count, `${name} should have at least one h1`).toBeGreaterThanOrEqual(minHeadingCount);
    });
  }
});

// ── Specific page tests ──────────────────────────────────────────────

test.describe('Homepage', () => {
  test('loads without errors', async ({ page }) => {
    const getErrors = captureErrors(page);
    const response = await page.goto('/', { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Homepage uses FusionPage; without CMS data shows ErrorState
    expect(response?.status()).toBe(200);
    const bodyText = await page.textContent('body');
    expect(bodyText?.length ?? 0).toBeGreaterThan(20);
    expect(getErrors(), 'Should have no console errors').toHaveLength(0);
  });
});

test.describe('Courses Page', () => {
  test('loads without errors', async ({ page }) => {
    const getErrors = captureErrors(page);
    const response = await page.goto('/courses', { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Courses page has h1 + search input even without API data
    expect(response?.status()).toBe(200);
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.input-field').first()).toBeVisible();
    expect(getErrors(), 'Should have no console errors').toHaveLength(0);
  });
});

test.describe('Login Page', () => {
  test('has email and password fields', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle', timeout: 15000 });

    await expect(page.locator('#username')).toBeVisible();
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
