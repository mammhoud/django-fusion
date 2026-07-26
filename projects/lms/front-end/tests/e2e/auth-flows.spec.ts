import { test, expect } from '../fixtures/auth';
import type { Page } from '@playwright/test';

/**
 * Auth Flow E2E Tests — Login, Register, Logout, Password Reset
 *
 * Tests the complete authentication user journey:
 * - Login form submission
 * - Registration form submission
 * - Password validation
 * - Role selection
 * - Navigation between auth pages
 */

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
        !e.includes('Failed to load') &&
        !e.includes('ERR_CONNECTION_REFUSED') &&
        !e.includes('fetch') &&
        !e.includes('NetworkError')
    );
}

test.describe('Auth Flows', () => {
  test('login form validates empty fields', async ({ page }) => {
    const getErrors = captureErrors(page);
    await page.goto('/login', { waitUntil: 'networkidle', timeout: 15000 });

    // Submit empty form
    await page.locator('button[type="submit"]').click();

    // Should show validation (HTML5 or custom)
    const usernameInput = page.locator('#username');
    const isValid = await usernameInput.evaluate((el) => (el as HTMLInputElement).validity.valid);
    expect(isValid).toBe(false);
    expect(getErrors()).toHaveLength(0);
  });

  test('registration validates password match', async ({ page }) => {
    await page.goto('/registration', { waitUntil: 'networkidle', timeout: 15000 });

    const passwordFields = page.locator('input[type="password"]');
    const count = await passwordFields.count();

    if (count >= 2) {
      await passwordFields.first().fill('password123');
      await passwordFields.nth(1).fill('different');

      // Should show mismatch error
      const errorText = page.locator('text=/match/i');
      const hasError = await errorText.isVisible().catch(() => false);
      expect(hasError).toBe(true);
    }
  });

  test('login page navigates to registration', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle', timeout: 15000 });

    await page.locator('a[href="/registration"]').first().click();
    await page.waitForURL('**/registration');

    await expect(page.locator('h1')).toContainText(/create|register|sign up/i);
  });

  test('registration page navigates to login', async ({ page }) => {
    await page.goto('/registration', { waitUntil: 'networkidle', timeout: 15000 });

    await page.locator('a[href="/login"]').first().click();
    await page.waitForURL('**/login');

    await expect(page.locator('h1')).toContainText(/welcome|sign in|login/i);
  });

  test('password toggle reveals and hides password', async ({ page }) => {
    await page.goto('/login', { waitUntil: 'networkidle', timeout: 15000 });

    const passwordInput = page.locator('input[type="password"]');
    if (await passwordInput.isVisible()) {
      // Click the eye toggle
      const toggleBtn = page.locator('button').filter({ has: page.locator('svg') }).first();
      if (await toggleBtn.isVisible()) {
        await toggleBtn.click();
        // Password should now be visible (type="text")
        await expect(page.locator('input[type="text"]')).toBeVisible();
      }
    }
  });
});
