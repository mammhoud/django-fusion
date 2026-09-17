import { expect, test } from '@playwright/test';

/**
 * Auth parity smoke — the LF header exposes the same allauth headless
 * login modal as Precis. Verify the modal opens from the header's Log In
 * button (when logged out), shows the email/password form, and closes.
 */
test('login modal opens from header Log In', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  // Wait for Alpine to initialize (the modal listens for fusion:open-login).
  await page.waitForFunction(() => (window as any).__FUSION_AUTH !== undefined, null, { timeout: 15000 });
  // Header Log In button (logged-out state after auth check settles).
  const loginBtn = page.locator('button:has-text("Log In")').first();
  await expect(loginBtn).toBeVisible({ timeout: 15000 });
  await loginBtn.click();
  // Modal opens (scope to the login dialog — cookie consent is also a dialog).
  const dialog = page.getByRole('dialog', { name: 'Sign in' });
  await expect(dialog).toBeVisible({ timeout: 5000 });
  await expect(dialog.locator('input[type="email"]')).toBeVisible();
  await expect(dialog.locator('input[type="password"]')).toBeVisible();
  await expect(dialog.locator('button:has-text("Sign in")')).toBeVisible();
  // Close via Escape
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden({ timeout: 5000 });
});
