import { test, expect } from '@playwright/test';

// Matches the operator seeded by apps.core seed_playwright — the only account
// the browser suite signs in with to reach the auth-gated Task Center.
const EMAIL = 'playwright@loop.dev';
const PASSWORD = 'playwright-pass-123';

test.describe('Loop CRM Task Center', () => {
  test('anonymous access redirects to the login page', async ({ page }) => {
    await page.goto('/tasks/');
    await page.waitForURL(/\/accounts\/login\//);
    expect(page.url()).toContain('next=');
    expect(page.url()).toContain('tasks');
  });

  test('signed-in operator sees the shared audit trail', async ({ page }) => {
    await page.goto('/accounts/login/');
    await expect(page.locator('#id_login')).toBeVisible();
    await page.locator('#id_login').fill(EMAIL);
    await page.locator('#id_password').fill(PASSWORD);
    await page.locator('button[type="submit"]').click();

    // Successful login redirects to the dashboard (LOGIN_REDIRECT_URL="/").
    await expect(page).toHaveURL((url) => url.pathname === '/', { timeout: 15_000 });

    await page.goto('/tasks/');
    await expect(page.locator('#loop-navigation')).toBeVisible();
    await expect(page.locator('#loop-navigation a[href="/tasks/"]')).toHaveAttribute('aria-current', 'page');
    await expect(page.locator('h1')).toContainText('Tasks');
    await expect(page.getByText('Execution history')).toBeVisible();
    // Honest dual-state: the page renders either the empty state (fresh DB)
    // or the merged audit table — never a blank shell.
    await expect(
      page.locator('.loop-empty-state, .loop-table-wrap').first(),
    ).toBeVisible();
  });
});
