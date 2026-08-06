import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TAURI_MOCK = path.resolve(__dirname, 'mocks/tauri.ts');

/**
 * Helper: navigate to the Auth page and wait for it to settle.
 * After navigation, we wait for the React app to mount by checking
 * for the app root or one of the known Auth page texts.
 */
async function navigateToAuth(page: import('@playwright/test').Page) {
  await page.goto('/');
  // Wait for React to mount — the tokenized i18n keys appear as text
  // (e.g. "auth.checking", "auth.createAccount", "auth.welcomeBack")
  await page.waitForSelector('text=auth.', { timeout: 10_000 });
}

test.describe('Auth Page — Visual Regression', () => {
  test.describe('Register step (no existing users)', () => {
    test.beforeEach(async ({ page }) => {
      await page.addInitScript({ path: TAURI_MOCK });
      // has_users = false → register step
      await page.addInitScript(`
        window.__TAURI_MOCK_SET__('check_auth_required', true);
        window.__TAURI_MOCK_SET__('has_users', false);
        window.__TAURI_MOCK_SET__('get_superuser_email', null);
      `);
    });

    test('renders the register form with illustration panel', async ({ page }) => {
      await navigateToAuth(page);

      // Wait for register content
      await expect(page.getByText('auth.createAccount')).toBeVisible();

      // ── Illustration panel ──
      await expect(page.getByText('Formint')).toBeVisible();
      await expect(page.getByText('Point of Sale & Order Management')).toBeVisible();
      await expect(page.getByText('Real-time Analytics & Reports')).toBeVisible();
      await expect(page.getByText('Inventory & Recipe Tracking')).toBeVisible();

      // ── Form elements ──
      await expect(page.getByPlaceholder('manager@restaurant.com')).toBeVisible();
      await expect(page.getByText('auth.sendCode')).toBeVisible();
      await expect(page.getByText('auth.signIn')).toBeVisible();

      // ── Screenshot ──
      await page.screenshot({
        path: `e2e/screenshots/auth-register.png`,
        fullPage: false,
      });
    });

    test('renders floating particles and brand icons in illustration', async ({ page }) => {
      await navigateToAuth(page);

      await expect(page.getByText('auth.createAccount')).toBeVisible();

      // The illustration panel is a sibling of the form panel
      // Particles are rendered as divs with specific styling
      const illustration = page.locator('.bg-gradient-to-br').first();
      await expect(illustration).toBeVisible();

      // Brand icons render FaStore, FaChartLine, FaCogs, FaUtensils, FaClipboardList
      // as SVG elements inside the illustration panel
      const svgIcons = illustration.locator('svg');
      const count = await svgIcons.count();
      expect(count).toBeGreaterThanOrEqual(5);
    });

    test('send code button is disabled when email is empty', async ({ page }) => {
      await navigateToAuth(page);

      await expect(page.getByText('auth.createAccount')).toBeVisible();

      const sendBtn = page.getByText('auth.sendCode').locator('..');
      await expect(sendBtn).toBeDisabled();
    });

    test('transitions from register to verify step on valid email', async ({ page }) => {
      await navigateToAuth(page);

      await expect(page.getByText('auth.createAccount')).toBeVisible();

      // Type a valid email
      const emailInput = page.getByPlaceholder('manager@restaurant.com');
      await emailInput.fill('manager@restaurant.com');

      // Click send code — needs to also mock send_auth_confirmation_code
      await page.evaluate(() => {
        (window as Record<string, unknown>).__TAURI_MOCK_SET__('send_auth_confirmation_code', undefined);
      });

      await page.getByText('auth.sendCode').click();

      // Should transition to verify step
      await expect(page.getByText('auth.verifyEmail')).toBeVisible({ timeout: 5000 });

      // ── Screenshot ──
      await page.screenshot({
        path: `e2e/screenshots/auth-verify.png`,
        fullPage: false,
      });
    });

    test('switches to login step on "Sign In" click', async ({ page }) => {
      await navigateToAuth(page);

      await expect(page.getByText('auth.createAccount')).toBeVisible();

      await page.getByText('auth.signIn').click();

      // Should transition to login
      await expect(page.getByText('auth.welcomeBack')).toBeVisible({ timeout: 5000 });

      // ── Screenshot ──
      await page.screenshot({
        path: `e2e/screenshots/auth-login-from-register.png`,
        fullPage: false,
      });
    });

    test('switches back to register from login on "Create one"', async ({ page }) => {
      await navigateToAuth(page);

      await expect(page.getByText('auth.createAccount')).toBeVisible();

      // First → login
      await page.getByText('auth.signIn').click();
      await expect(page.getByText('auth.welcomeBack')).toBeVisible({ timeout: 5000 });

      // The "create one" link should now be visible (no users exist)
      await expect(page.getByText('auth.createOne')).toBeVisible();

      // Click it to go back to register
      await page.getByText('auth.createOne').click();

      // Should be back on register step
      await expect(page.getByText('auth.createAccount')).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Login step (existing users)', () => {
    test.beforeEach(async ({ page }) => {
      await page.addInitScript({ path: TAURI_MOCK });
      // has_users = true → login step, with pre-filled email
      await page.addInitScript(`
        window.__TAURI_MOCK_SET__('check_auth_required', true);
        window.__TAURI_MOCK_SET__('has_users', true);
        window.__TAURI_MOCK_SET__('get_superuser_email', 'admin@restaurant.com');
      `);
    });

    test('renders the login form', async ({ page }) => {
      await navigateToAuth(page);

      await expect(page.getByText('auth.welcomeBack')).toBeVisible();
      await expect(page.getByText('auth.loginDesc')).toBeVisible();
      await expect(page.getByText('auth.signIn')).toBeVisible();
      await expect(page.getByText('auth.rememberMe')).toBeVisible();

      // ── Screenshot ──
      await page.screenshot({
        path: `e2e/screenshots/auth-login.png`,
        fullPage: false,
      });
    });

    test('"Create one" link is hidden when users exist', async ({ page }) => {
      await navigateToAuth(page);

      await expect(page.getByText('auth.welcomeBack')).toBeVisible();

      // The "create one" link should NOT be visible
      await expect(page.getByText('auth.createOne')).not.toBeVisible();
    });

    test('sign in button is disabled when password is empty', async ({ page }) => {
      await navigateToAuth(page);

      await expect(page.getByText('auth.welcomeBack')).toBeVisible();

      // Email is pre-filled, but password is empty
      const signInBtn = page.getByText('auth.signIn').locator('..');
      await expect(signInBtn).toBeDisabled();
    });

    test('displays error on failed login attempt', async ({ page }) => {
      // Mock login_user to fail
      await page.addInitScript(`
        window.__TAURI_MOCK_SET__('login_user', new Error('Invalid credentials'));
      `);

      await navigateToAuth(page);

      await expect(page.getByText('auth.welcomeBack')).toBeVisible();

      // Type password and click sign in
      const passwordInput = page.getByPlaceholder('••••••••');
      await passwordInput.fill('wrongpassword');

      await page.getByText('auth.signIn').click();

      // Error should appear as a toast notification
      await expect(page.getByText('Invalid credentials')).toBeVisible({ timeout: 5000 });

      // ── Screenshot ──
      await page.screenshot({
        path: `e2e/screenshots/auth-login-error.png`,
        fullPage: false,
      });
    });
  });

  test.describe('Checking / loading state', () => {
    test('shows loading spinner before auth resolves', async ({ page }) => {
      await page.addInitScript({ path: TAURI_MOCK });
      // Don't set check_auth_required yet — the mock will return null immediately
      // Instead, we'll use a deliberately slow navigation approach
      await page.addInitScript(`
        // Make the invoke hang for a bit to catch the checking state
        const originalInvoke = window.__TAURI_INTERNALS__.invoke;
        window.__TAURI_INTERNALS__.invoke = (cmd, args) => {
          if (cmd === 'check_auth_required') {
            return new Promise(resolve => setTimeout(() => resolve(true), 2000));
          }
          return originalInvoke(cmd, args);
        };
        window.__TAURI_MOCK_SET__('has_users', false);
        window.__TAURI_MOCK_SET__('get_superuser_email', null);
      `);

      await page.goto('/');
      // Should show checking state
      await expect(page.getByText('auth.checking')).toBeVisible({ timeout: 3000 });

      // ── Screenshot ──
      await page.screenshot({
        path: `e2e/screenshots/auth-checking.png`,
        fullPage: false,
      });

      // Eventually resolves to register step
      await expect(page.getByText('auth.createAccount')).toBeVisible({ timeout: 5000 });
    });
  });
});

test.describe('Auth Page — Theme & Layout', () => {
  test('renders the LanguageToggle and ThemeToggle', async ({ page }) => {
    await page.addInitScript({ path: TAURI_MOCK });
    await page.addInitScript(`
      window.__TAURI_MOCK_SET__('check_auth_required', true);
      window.__TAURI_MOCK_SET__('has_users', false);
      window.__TAURI_MOCK_SET__('get_superuser_email', null);
    `);

    await navigateToAuth(page);

    await expect(page.getByText('auth.createAccount')).toBeVisible();

    // The toggles container is fixed top-right
    const toggleContainer = page.locator('.fixed.top-4');
    await expect(toggleContainer).toBeVisible();

    // ThemeToggle and LanguageToggle both render as buttons
    const toggleBtns = toggleContainer.locator('button');
    const count = await toggleBtns.count();
    expect(count).toBeGreaterThanOrEqual(2);
  });

  test('illustration panel has gradient background', async ({ page }) => {
    await page.addInitScript({ path: TAURI_MOCK });
    await page.addInitScript(`
      window.__TAURI_MOCK_SET__('check_auth_required', true);
      window.__TAURI_MOCK_SET__('has_users', false);
      window.__TAURI_MOCK_SET__('get_superuser_email', null);
    `);

    await navigateToAuth(page);

    await expect(page.getByText('auth.createAccount')).toBeVisible();

    // The illustration panel has a background gradient
    const illustration = page.locator('.bg-gradient-to-br').first();
    await expect(illustration).toBeVisible();

    // ── Screenshot ──
    await page.screenshot({
      path: `e2e/screenshots/auth-theme-register.png`,
      fullPage: false,
    });
  });
});
