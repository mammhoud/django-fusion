import { test, expect } from '../../fixtures/auth';

/**
 * Theme Visual Regression Tests
 *
 * Captures full-page screenshots of:
 * 1. Theme Showcase page — every CSS class, swatch, and component
 * 2. Key dashboard pages — with auth mocked, dynamic content masked
 *
 * ## Running
 *   npx playwright test tests/e2e/theme-visual-regression.spec.ts
 *
 * ## Updating Snapshots
 *   npx playwright test tests/e2e/theme-visual-regression.spec.ts --update-snapshots
 *
 * ## Snapshot Storage
 *   Snapshots are stored alongside tests in __screenshots__/
 *   These should be committed to git for CI comparison.
 */

// ── Theme Showcase Page ──────────────────────────────────────────

test.describe('Theme Showcase — Visual Regression', () => {
  test('full page snapshot matches baseline', async ({ page }) => {
    await page.goto('/dev/theme', { waitUntil: 'networkidle', timeout: 15000 });

    // Wait for all components to render
    await page.waitForTimeout(1000);

    // Capture full-page screenshot
    await expect(page).toHaveScreenshot('theme-showcase-full.png', {
      fullPage: true,
      maxDiffPixels: 500, // Allow small anti-aliasing differences
      threshold: 0.05,    // 5% pixel difference threshold
    });
  });

  test('color swatches section matches baseline', async ({ page }) => {
    await page.goto('/dev/theme', { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(500);

    const swatches = page.getByTestId('swatch-ctc-primary');
    await swatches.scrollIntoViewIfNeeded();

    // Capture just the swatches area
    const section = page.locator('section').filter({ hasText: 'CTC Color Palette' });
    await expect(section).toHaveScreenshot('theme-swatches.png', {
      maxDiffPixels: 100,
      threshold: 0.03,
    });
  });

  test('buttons section matches baseline', async ({ page }) => {
    await page.goto('/dev/theme', { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(500);

    const section = page.locator('section').filter({ hasText: 'Buttons' });
    await section.scrollIntoViewIfNeeded();

    await expect(section).toHaveScreenshot('theme-buttons.png', {
      maxDiffPixels: 100,
      threshold: 0.03,
    });
  });

  test('cards section matches baseline', async ({ page }) => {
    await page.goto('/dev/theme', { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(500);

    const section = page.locator('section').filter({ hasText: 'Cards' });
    await section.scrollIntoViewIfNeeded();

    await expect(section).toHaveScreenshot('theme-cards.png', {
      maxDiffPixels: 100,
      threshold: 0.03,
    });
  });

  test('UI components section matches baseline', async ({ page }) => {
    await page.goto('/dev/theme', { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(500);

    const section = page.locator('section').filter({ hasText: 'UI Components' });
    await section.scrollIntoViewIfNeeded();

    await expect(section).toHaveScreenshot('theme-components.png', {
      maxDiffPixels: 200,
      threshold: 0.05,
    });
  });
});

// ── Dashboard Pages — Key Snapshots ─────────────────────────────

test.describe('Dashboard Pages — Visual Regression', () => {
  test('main dashboard snapshot (instructor)', async ({ instructorPage }) => {
    await instructorPage.goto('/dashboard', { waitUntil: 'networkidle', timeout: 15000 });
    await instructorPage.waitForTimeout(1000);

    // Mask dynamic content: charts, dates, numbers that change
    await expect(instructorPage).toHaveScreenshot('dashboard-main.png', {
      fullPage: true,
      maxDiffPixels: 1000,
      threshold: 0.08,
      mask: [
        // Mask chart areas (dynamic data)
        instructorPage.locator('.recharts-responsive-container'),
        // Mask dynamic values
        instructorPage.locator('.text-2xl.font-bold, .text-3xl.font-bold'),
      ],
    });
  });

  test('courses list snapshot (instructor)', async ({ instructorPage }) => {
    await instructorPage.goto('/dashboard/courses', { waitUntil: 'networkidle', timeout: 15000 });
    await instructorPage.waitForTimeout(1000);

    await expect(instructorPage).toHaveScreenshot('dashboard-courses.png', {
      fullPage: true,
      maxDiffPixels: 800,
      threshold: 0.08,
      mask: [
        instructorPage.locator('table tbody'), // Dynamic course data
      ],
    });
  });

  test('profile page snapshot (student)', async ({ studentPage }) => {
    await studentPage.goto('/dashboard/profile', { waitUntil: 'networkidle', timeout: 15000 });
    await studentPage.waitForTimeout(1000);

    await expect(studentPage).toHaveScreenshot('dashboard-profile.png', {
      fullPage: true,
      maxDiffPixels: 800,
      threshold: 0.08,
    });
  });

  test('admin withdrawals snapshot (admin)', async ({ adminPage }) => {
    await adminPage.goto('/dashboard/admin/withdrawals', { waitUntil: 'networkidle', timeout: 15000 });
    await adminPage.waitForTimeout(1000);

    await expect(adminPage).toHaveScreenshot('dashboard-admin-withdrawals.png', {
      fullPage: true,
      maxDiffPixels: 800,
      threshold: 0.08,
      mask: [
        adminPage.locator('table tbody'), // Dynamic withdrawal data
      ],
    });
  });
});

// ── Public Pages — Key Snapshots ────────────────────────────────

test.describe('Public Pages — Visual Regression', () => {
  test('homepage snapshot', async ({ page }) => {
    await page.goto('/', { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(1000);

    await expect(page).toHaveScreenshot('public-homepage.png', {
      fullPage: true,
      maxDiffPixels: 1500,
      threshold: 0.10, // Homepage is large, allow more variance
    });
  });

  test('login page snapshot', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('public-login.png', {
      fullPage: true,
      maxDiffPixels: 500,
      threshold: 0.05,
    });
  });
});
