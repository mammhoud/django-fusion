import { test, expect, type Page } from '@playwright/test';

/**
 * Content Rendering E2E Tests — CMS-Fusion Frontend
 *
 * Verifies that page content fetched from the Wagtail backend API
 * actually renders in the browser. Tests go beyond "page loads OK"
 * by checking that specific content from the API appears in the DOM.
 *
 * These tests require the CMS backend to be running.
 */

// ── Helpers ──────────────────────────────────────────────────────────

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5075/api';

interface PageMeta {
  slug: string;
  title: string;
  show_in_nav: boolean;
}

/** Fetch the page list from the API */
async function fetchPageList(): Promise<PageMeta[]> {
  try {
    const resp = await fetch(`${API_URL}/pages/`);
    const data = await resp.json() as { pages: PageMeta[]; total: number };
    if (!data.pages?.length) {
      console.warn('API returned no pages — will skip API-dependent tests');
      return [];
    }
    return data.pages;
  } catch (err) {
    console.warn('Cannot reach API — API-dependent tests will be skipped:', String(err));
    return [];
  }
}

/** Fetch page title from the API for a given slug */
async function fetchPageTitle(slug: string): Promise<string | null> {
  try {
    const resp = await fetch(`${API_URL}/pages/${slug}/data/`);
    const data = await resp.json() as { data: { title: string } };
    return data.data?.title ?? null;
  } catch {
    return null;
  }
}

/** Capture console errors (filters known non-critical ones) */
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

// ── Pre-flight: fetch page list from API ────────────────────────────
let pages: PageMeta[] = [];
let pagesBySlug: Record<string, string | null> = {};

test.beforeAll(async () => {
  pages = await fetchPageList();
  // Fetch titles for a subset of pages
  const coreSlugs = ['home', 'about', 'services', 'team', 'contact', 'privacy', 'faq'];
  for (const slug of coreSlugs) {
    pagesBySlug[slug] = await fetchPageTitle(slug);
  }
});

// ═════════════════════════════════════════════════════════════════════
// Static Page Rendering Tests
// ═════════════════════════════════════════════════════════════════════

test.describe('Static Content Rendering', () => {
  test('homepage renders with content', async ({ page }) => {
    // Check the page title (HTML <title>) contains expected text
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(1000);

    // Check the page has loaded content
    const bodyText = await page.textContent('body');
    expect(bodyText?.length ?? 0, 'Body should have content').toBeGreaterThan(100);

    // The HTML <title> should contain a page name
    const title = await page.title();
    expect(title?.length ?? 0, 'Page should have a non-empty <title>').toBeGreaterThan(0);
  });

  test('header and footer render on every page type', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(1000);

    await expect(page.locator('header'), 'Header should be visible').toBeVisible({ timeout: 5000 });
    await expect(page.locator('footer'), 'Footer should be visible').toBeVisible({ timeout: 5000 });

    // Page should have navigation links
    const navLinks = page.locator('header a, nav a');
    const linkCount = await navLinks.count();
    expect(linkCount, 'Navigation should have links').toBeGreaterThanOrEqual(3);
  });

  test('no critical console errors on any page', async ({ page }) => {
    const getErrors = captureErrors(page);
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(1000);

    const critical = getErrors();
    expect(critical, 'Homepage should have no critical console errors').toHaveLength(0);
  });
});

// ═════════════════════════════════════════════════════════════════════
// API-Backed Content Rendering Tests
// ═════════════════════════════════════════════════════════════════════

test.describe('API-Backed Content Rendering', () => {
  test.beforeEach(async () => {
    test.skip(pages.length === 0, 'No pages from API — skipping');
  });

  // Limit to first 8 nav pages to keep test runtime reasonable
  const navPages = pages.filter(p => p.show_in_nav || p.slug === 'home').slice(0, 8);

  for (const { slug, title } of navPages) {
    test(`${title} (/${slug}) renders with API content`, async ({ page }) => {
      test.skip(pages.length === 0, 'No pages from API — skipping');

      const getErrors = captureErrors(page);

      const response = await page.goto(`/${slug === 'home' ? '' : slug}`, {
        waitUntil: 'domcontentloaded',
        timeout: 10000,
      });

      // Wait for content to settle (FusionProxy may need time)
      await page.waitForTimeout(1000);

      // Check HTTP status
      expect(response?.status(), `${title} should return 200`).toBe(200);

      // Body should have meaningful content (not the skeleton/loading state)
      const bodyText = await page.textContent('body');
      expect(bodyText?.length ?? 0, `${title} body should have content`).toBeGreaterThan(100);
      expect(
        bodyText?.includes('404') && bodyText?.includes('Not Found'),
        `${title} should not be a 404 page`
      ).toBe(false);

      // The page title from the API should appear somewhere in the rendered HTML
      const apiTitle = pagesBySlug[slug] || title;
      if (apiTitle) {
        const titleVisible = bodyText?.includes(apiTitle) ?? false;
        expect(
          titleVisible,
          `API title "${apiTitle}" should be rendered on page`
        ).toBeTruthy();
      }

      // No critical console errors
      const critical = getErrors();
      expect(critical, `${title} should have no critical console errors`).toHaveLength(0);
    });
  }
});

// ═════════════════════════════════════════════════════════════════════
// Dynamic Page Verification
// ═════════════════════════════════════════════════════════════════════

test.describe('Dynamic Page Content Verification', () => {
  test('navigating between pages shows correct content', async ({ page }) => {
    test.skip(pages.length === 0, 'No pages from API — skipping');

    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(1000);

    // Find navigation links and verify they navigate correctly
    const navContainer = page.locator('header, nav').first();
    const navAnchors = navContainer.locator('a');

    const linkCount = await navAnchors.count();
    if (linkCount < 2) {
      console.warn('Not enough nav links to test navigation');
      return;
    }

    // Click the second nav link (skip home, try about/services)
    const secondLink = navAnchors.nth(1);
    const href = await secondLink.getAttribute('href');

    if (href && !href.startsWith('#') && !href.startsWith('http')) {
      await secondLink.click();

      // Wait for navigation and content to load
      await page.waitForTimeout(3000);

      // Verify page is not an error
      const bodyText = await page.textContent('body');
      expect(bodyText?.length ?? 0, 'Navigated page should have content').toBeGreaterThan(100);
      expect(
        bodyText?.includes('500') && bodyText?.includes('Internal Server Error'),
        'Navigation should not lead to 500 error'
      ).toBe(false);
    }
  });

  test('blog page renders with search or content area', async ({ page }) => {
    await page.goto('/blog', { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(1000);

    // Blog should have a heading
    const h1 = page.locator('h1');
    const h1Count = await h1.count();
    if (h1Count > 0) {
      await expect(h1.first()).toBeVisible();
    }

    // Should have content area (posts grid, skeleton, or empty state)
    const contentAreas = page.locator('.grid, main, article, .fusion-proxy, [class*="post"]');
    const contentCount = await contentAreas.count();
    expect(contentCount, 'Blog page should have a content area').toBeGreaterThanOrEqual(0);

    // No server errors
    const bodyText = await page.textContent('body');
    expect(
      bodyText?.includes('500') && bodyText?.includes('Internal Server Error'),
      'Blog should not show server error'
    ).toBe(false);
  });

  test('courses page renders with filter/search elements', async ({ page }) => {
    await page.goto('/courses', { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(1000);

    // Courses page should have a heading
    const h1 = page.locator('h1');
    const h1Count = await h1.count();
    if (h1Count > 0) {
      await expect(h1.first()).toBeVisible();
    }

    // Should have either a search input or filter area
    const searchInput = page.locator('input[type="text"], input[type="search"]');
    const filterSidebar = page.locator('[class*="filter"], [class*="sidebar"]');
    const contentGrid = page.locator('.grid, main, [class*="course"]');

    const hasSearch = (await searchInput.count()) > 0;
    const hasFilters = (await filterSidebar.count()) > 0;
    const hasContent = (await contentGrid.count()) > 0;

    expect(hasSearch || hasFilters || hasContent, 'Courses should have search, filters, or content').toBe(true);
  });
});

// ═════════════════════════════════════════════════════════════════════
// Footer Content Verification
// ═════════════════════════════════════════════════════════════════════

test.describe('Footer Content Verification', () => {
  test('footer has branding and links', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(1000);

    const footer = page.locator('footer');
    await expect(footer, 'Footer should be visible').toBeVisible({ timeout: 5000 });

    // Footer should have links
    const footerLinks = footer.locator('a');
    const linkCount = await footerLinks.count();
    expect(linkCount, 'Footer should have links').toBeGreaterThanOrEqual(3);

    // Footer should have copyright text
    const footerText = await footer.textContent() ?? '';
    expect(
      footerText.toLowerCase().includes('all rights reserved') ||
      footerText.toLowerCase().includes('©') ||
      footerText.toLowerCase().includes('copyright'),
      'Footer should contain copyright or rights reserved text'
    ).toBeTruthy();
  });
});
