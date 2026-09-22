/**
 * Playwright tests for the tools-web dashboard.
 *
 * Covers:
 *   1. Unauthenticated → sign-in modal appears
 *   2. Wrong password → error shown
 *   3. Correct login (admin/admin) → dashboard revealed, session active
 *   4. Clicking a tool → unlock modal asks for the shared password
 *   5. Wrong unlock password → error
 *   6. Correct unlock → navigates to the tool path
 *   7. Theme toggle persists across reloads
 *   8. /login redirects to /
 */
import { test, expect } from '@playwright/test';

const UNLOCK_PASSWORD = 'test-unlock-pass-123';

test.describe('tools dashboard', () => {
  test('shows sign-in modal when unauthenticated', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
    await expect(page.getByLabel('Username')).toBeVisible();
    await expect(page.getByLabel('Password', { exact: true })).toBeVisible();
    await expect(page.getByLabel('Unlock password')).toBeHidden(); // modal closed
  });

  test('rejects a wrong password', async ({ page }) => {
    await page.goto('/');
    await page.getByLabel('Username').fill('admin');
    await page.getByLabel('Password', { exact: true }).fill('wrong-password');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByText('Invalid username or password')).toBeVisible();
    // Still on the sign-in modal
    await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  });

  test('logs in and reveals the dashboard', async ({ page }) => {
    await page.goto('/');
    await page.getByLabel('Username').fill('admin');
    await page.getByLabel('Password', { exact: true }).fill('admin');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByRole('heading', { name: /Application/ })).toBeVisible();
    await expect(page.getByText('Administrator')).toBeVisible();
    // Sign-in modal is gone
    await expect(page.getByRole('heading', { name: 'Sign in' })).toHaveCount(0);
  });

  test('asks for the unlock password when opening a tool', async ({ page }) => {
    await page.goto('/');
    await page.getByLabel('Username').fill('admin');
    await page.getByLabel('Password', { exact: true }).fill('admin');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByRole('heading', { name: /Application/ })).toBeVisible();

    await page.locator('.card', { hasText: 'Blinko' }).click();
    await expect(page.getByRole('heading', { name: 'Open Blinko' })).toBeVisible();
    await expect(page.getByLabel('Unlock password')).toBeVisible();
  });

  test('rejects a wrong unlock password', async ({ page }) => {
    await page.goto('/');
    await page.getByLabel('Username').fill('admin');
    await page.getByLabel('Password', { exact: true }).fill('admin');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByRole('heading', { name: /Application/ })).toBeVisible();

    await page.locator('.card', { hasText: 'Blinko' }).click();
    await page.getByLabel('Unlock password').fill('wrong');
    await page.getByRole('button', { name: 'Open tool' }).click();
    await expect(page.getByText('Incorrect password for this tool')).toBeVisible();
  });

  test('unlocks and navigates to the tool', async ({ page }) => {
    await page.goto('/');
    await page.getByLabel('Username').fill('admin');
    await page.getByLabel('Password', { exact: true }).fill('admin');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByRole('heading', { name: /Application/ })).toBeVisible();

    await page.locator('.card', { hasText: 'Blinko' }).click();
    await page.getByLabel('Unlock password').fill(UNLOCK_PASSWORD);
    await page.getByRole('button', { name: 'Open tool' }).click();

    // Blinko route does not exist in the test server → our server 404s it,
    // but navigation to /notes/ is what matters.
    await page.waitForURL('**/notes/');
  });

  test('theme toggle persists across reloads', async ({ page }) => {
    // Log in first so the sign-in modal does not block the sidebar toggle.
    await page.goto('/');
    await page.getByLabel('Username').fill('admin');
    await page.getByLabel('Password', { exact: true }).fill('admin');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByRole('heading', { name: /Application/ })).toBeVisible();

    // Dark by default only if the OS prefers it; force light first.
    await page.evaluate(() => localStorage.setItem('tools-theme', 'light'));
    await page.reload();
    await expect(page.getByRole('heading', { name: /Application/ })).toBeVisible();

    const toggle = page.locator('.theme-toggle');
    await toggle.click();
    await expect(page.locator('html')).toHaveClass(/dark/);

    await page.reload();
    await expect(page.locator('html')).toHaveClass(/dark/);

    await toggle.click();
    await expect(page.locator('html')).not.toHaveClass(/dark/);
  });

  test('GET /login redirects to /', async ({ page }) => {
    const response = await page.goto('/login');
    expect(response.status()).toBeGreaterThanOrEqual(200);
    await expect(page).toHaveURL(/\/$/);
  });
});
