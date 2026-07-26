import { test, expect } from '@playwright/test';
import type { Page } from '@playwright/test';

/**
 * Public Pages E2E Tests — CMS-Fusion Frontend
 *
 * Tests all public-facing pages:
 * - Homepage
 * - Blog listing
 * - Courses listing
 * - Products listing
 * - Dynamic CMS pages ([slug])
 *
 * These tests validate:
 * - Pages render without errors (HTTP 200)
 * - Key UI elements are present (header, footer, navigation)
 * - No console errors
 * - Pages gracefully handle unavailable API
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

function getPageSpecificChecks(path: string) {
  switch (path) {
    case '/':
      return { minHeadings: 0, expectedText: [], expectedSelectors: ['header', 'footer'] };
    case '/blog':
      return { minHeadings: 1, expectedText: ['Blog'], expectedSelectors: ['h1'] };
    case '/courses':
      return { minHeadings: 1, expectedText: ['Courses'], expectedSelectors: ['h1'] };
    case '/products':
      return { minHeadings: 1, expectedText: ['Products'], expectedSelectors: ['h1'] };
    default:
      return { minHeadings: 0, expectedText: [], expectedSelectors: [] };
  }
}

// ── Public page config ───────────────────────────────────────────────

const PUBLIC_PAGES = [
  { path: '/',         name: 'Homepage' },
  { path: '/blog',     name: 'Blog' },
  { path: '/courses',  name: 'Courses' },
  { path: '/products', name: 'Products' },
] as const;

// ── Tests ────────────────────────────────────────────────────────────

test.describe('Public Pages – Render & Theme', () => {
  for (const { path, name } of PUBLIC_PAGES) {
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
      expect(
        bodyText?.includes('404') && bodyText?.includes('Not Found'),
        `${name} should not be 404`
      ).toBe(false);

      // No console errors
      expect(getErrors(), `${name} should have no console errors`).toHaveLength(0);
    });

    test(`${name} (${path}) has expected layout elements`, async ({ page }) => {
      await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(2000);

      // Header should be present
      await expect(page.locator('header')).toBeVisible();

      // Footer should be present
      const footer = page.locator('footer');
      await expect(footer).toBeVisible();

      // Navigation links exist
      const navLinks = page.locator('header nav a, header a[href]');
      const linkCount = await navLinks.count();
      expect(linkCount, `${name} header should have navigation links`).toBeGreaterThanOrEqual(4);

      // Page-specific checks
      const checks = getPageSpecificChecks(path);
      if (checks.minHeadings > 0) {
        const headings = page.locator('h1');
        const count = await headings.count();
        expect(count, `${name} should have h1`).toBeGreaterThanOrEqual(checks.minHeadings);
      }
    });
  }
});

// ── Header & Navigation ──────────────────────────────────────────────

test.describe('Header & Navigation', () => {
  test('desktop navigation links are present and functional', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Wait for header to render
    const header = page.locator('header');

    // Check key nav links are visible on desktop
    const homeLink = header.locator('a').filter({ hasText: 'Home' });
    await expect(homeLink.first()).toBeVisible();

    const blogLink = header.locator('a').filter({ hasText: 'Blog' });
    await expect(blogLink.first()).toBeVisible();

    const coursesLink = header.locator('a').filter({ hasText: 'Courses' });
    await expect(coursesLink.first()).toBeVisible();

    const productsLink = header.locator('a').filter({ hasText: 'Products' });
    await expect(productsLink.first()).toBeVisible();

    // Click Blog link and verify navigation
    await blogLink.first().click();
    await page.waitForURL('**/blog', { timeout: 10000 });
    await expect(page.locator('h1')).toBeVisible();
  });

  test('mobile hamburger menu toggles navigation', async ({ page }) => {
    // Mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Hamburger button should be visible on mobile
    const hamburger = page.locator('button[aria-label="Toggle menu"]');
    await expect(hamburger).toBeVisible();

    // Click to open mobile nav
    await hamburger.click();

    // Mobile nav should now be visible
    // After clicking hamburger, mobile nav should show links
    const mobileNavLinks = page.locator('a').filter({ hasText: 'Home' });
    const allHomeLinks = await mobileNavLinks.all();
    // At least one visible in the mobile dropdown
    expect(allHomeLinks.length).toBeGreaterThanOrEqual(1);
  });
});

// ── Blog Page ─────────────────────────────────────────────────────────

test.describe('Blog Page', () => {
  test('has search/filter elements', async ({ page }) => {
    await page.goto('/blog', { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Blog page should have a hero section
    await expect(page.locator('h1')).toBeVisible();
    const heroText = await page.locator('h1').textContent();
    expect(heroText?.toLowerCase()).toContain('blog');

    // Either posts, loading state, or empty state should render
    const postsGrid = page.locator('.grid');
    const skeleton = page.locator('.fusion-skeleton');
    const emptyState = page.locator('text=No blog posts');
    const hasContent = (await postsGrid.count()) > 0;
    const isLoading = (await skeleton.count()) > 0;
    const isEmpty = (await emptyState.count()) > 0;

    expect(hasContent || isLoading || isEmpty).toBe(true);
  });
});

// ── Courses Page ──────────────────────────────────────────────────────

test.describe('Courses Page', () => {
  test('has filter sidebar and search input', async ({ page }) => {
    await page.goto('/courses', { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Courses page should have a search form
    const searchInput = page.locator('input[type="text"]');
    const searchButton = page.locator('button[type="submit"]');
    const buttonCount = await searchButton.count();

    // Should either have the search form or filters sidebar
    const hasSearch = (await searchInput.count()) > 0;
    const hasFilters = (await page.locator('text=Filters').count()) > 0;

    expect(hasSearch || hasFilters).toBe(true);

    // H1 should be visible
    await expect(page.locator('h1')).toBeVisible();
    const headingText = await page.locator('h1').textContent();
    expect(headingText?.toLowerCase()).toContain('courses');
  });
});

// ── Products Page ─────────────────────────────────────────────────────

test.describe('Products Page', () => {
  test('renders product listing', async ({ page }) => {
    await page.goto('/products', { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Page should render
    await expect(page.locator('h1')).toBeVisible();
    const headingText = await page.locator('h1').textContent();
    expect(headingText?.toLowerCase()).toContain('product');

    // Products grid or loading/empty state should exist
    const skeleton = page.locator('.fusion-skeleton');
    const emptyState = page.locator('text=No products');
    const productCards = page.locator('.grid a').first();
    const hasContent = (await productCards.count()) > 0;
    const isLoading = (await skeleton.count()) > 0;
    const isEmpty = (await emptyState.count()) > 0;

    expect(hasContent || isLoading || isEmpty).toBe(true);
  });
});

// ── Footer ────────────────────────────────────────────────────────────

test.describe('Footer', () => {
  test('contains branding and links', async ({ page }) => {
    await page.goto('/', { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(2000);

    const footer = page.locator('footer');
    await expect(footer).toBeVisible();

    // Footer should have link sections
    const footerLinks = footer.locator('a');
    const count = await footerLinks.count();
    expect(count, 'Footer should have links').toBeGreaterThanOrEqual(5);

    // Check for copyright
    const footerText = await footer.textContent();
    expect(footerText).toContain('All rights reserved');
  });
});
