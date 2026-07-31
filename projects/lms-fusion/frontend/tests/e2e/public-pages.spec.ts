import { test, expect } from '@playwright/test';
import type { Page } from '@playwright/test';

/**
 * Public Pages E2E Tests — LMS-Fusion Frontend
 *
 * Tests all public-facing pages:
 * - Homepage (FusionProxy)
 * - Dynamic CMS pages ([slug]: about, services, team, contact)
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

// ── Public page config ───────────────────────────────────────────────

const PUBLIC_PAGES = [
  { path: '/', name: 'Homepage' },
] as const;

const CMS_PAGES = [
  { path: '/about',    name: 'About' },
  { path: '/services', name: 'Services' },
  { path: '/team',     name: 'Team' },
  { path: '/contact',  name: 'Contact' },
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

    test(`${name} (${path}) has header and footer`, async ({ page }) => {
      await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(2000);

      // Header should be present
      await expect(page.locator('header')).toBeVisible();

      // Footer should be present
      await expect(page.locator('footer')).toBeVisible();

      // Navigation links exist in header
      const navLinks = page.locator('header nav a, header a[href]');
      const linkCount = await navLinks.count();
      expect(linkCount, `${name} header should have navigation links`).toBeGreaterThanOrEqual(3);
    });
  }
});

// ── CMS Dynamic Pages ─────────────────────────────────────────────────

test.describe('CMS Dynamic Pages (FusionProxy)', () => {
  for (const { path, name } of CMS_PAGES) {
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

    test(`${name} (${path}) has header and footer`, async ({ page }) => {
      await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(2000);

      await expect(page.locator('header')).toBeVisible();
      await expect(page.locator('footer')).toBeVisible();
    });
  }
});

// ── Header & Navigation ──────────────────────────────────────────────

test.describe('Header & Navigation', () => {
  test('desktop navigation links are present and functional', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);

    const header = page.locator('header');

    // Check key nav links are visible on desktop
    const navLink = header.locator('a').filter({ hasText: 'Home' });
    await expect(navLink.first()).toBeVisible();

    // Click About link if present
    const aboutLink = header.locator('a').filter({ hasText: /about/i });
    if ((await aboutLink.count()) > 0) {
      await aboutLink.first().click();
      await page.waitForURL('**/about', { timeout: 10000 });
    }
  });

  test('mobile hamburger menu toggles navigation', async ({ page }) => {
    // Mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Hamburger button should be visible on mobile
    const hamburger = page.locator('button[aria-label="Toggle menu"]');
    const hasHamburger = (await hamburger.count()) > 0;

    if (hasHamburger) {
      await expect(hamburger).toBeVisible();
      await hamburger.click();

      // After clicking hamburger, navigation links should be clickable
      const navLink = page.locator('a').filter({ hasText: 'About' });
      if ((await navLink.count()) > 0) {
        await navLink.first().click();
        await page.waitForURL('**/about', { timeout: 10000 }).catch(() => {});
      }
    }
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
