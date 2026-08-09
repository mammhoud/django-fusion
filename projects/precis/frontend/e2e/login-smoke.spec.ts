import { test, expect } from '@playwright/test';

test('login modal opens from header Log In', async ({ page }) => {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  // Wait for Alpine to initialize (the modal listens for fusion:open-login).
  await page.waitForFunction(() => (window as any).__FUSION_AUTH !== undefined, null, { timeout: 15000 });
  // Header Log In button
  const loginBtn = page.locator('button:has-text("Log In")').first();
  await expect(loginBtn).toBeVisible({ timeout: 10000 });
  await loginBtn.click();
  // Modal opens (scope to the login dialog — cookie consent is also a dialog)
  const dialog = page.getByRole('dialog', { name: 'Sign in' });
  await expect(dialog).toBeVisible({ timeout: 5000 });
  await expect(dialog.locator('input[type="email"]')).toBeVisible();
  await expect(dialog.locator('input[type="password"]')).toBeVisible();
  await expect(dialog.locator('button:has-text("Sign in")')).toBeVisible();
  // Close via Escape
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden({ timeout: 5000 });
});
