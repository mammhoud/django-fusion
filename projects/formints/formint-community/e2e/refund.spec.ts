import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TAURI_MOCK = path.resolve(__dirname, 'mocks/tauri.ts');

const COMPLETED_SALE = {
  id: 1,
  items: [],
  total_amount: 25,
  currency: 'USD',
  date: '2026-08-01',
  time: '12:00',
  order_type: 'dine-in',
  status: 'completed',
  payment_method: 'cash',
  discount_amount: 0,
};

test.describe('Transactions — Refund flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript({ path: TAURI_MOCK });
    // Bypass the auth gate and load one completed sale.
    await page.addInitScript(`
      window.__TAURI_MOCK_SET__('check_auth_required', false);
      window.__TAURI_MOCK_SET__('get_settings', {
        restaurant_name: 'Formint', address: '', phone: '',
        currency: 'USD', receipt_footer: 'Thank you for your business!'
      });
    `);
  });

  test('refunds a completed sale end to end', async ({ page }) => {
    await page.addInitScript(
      `window.__TAURI_MOCK_SET__('get_transactions', [${JSON.stringify(COMPLETED_SALE)}]);`,
    );
    await page.goto('/transactions');

    await expect(page.getByRole('button', { name: /refund/i })).toBeVisible();
    await page.getByRole('button', { name: /refund/i }).click();

    await expect(page.getByRole('button', { name: /confirm refund/i })).toBeVisible();
    await page.getByRole('button', { name: /confirm refund/i }).click();

    // Local state flips the row to `refunded` — the amber chip appears and the
    // success toast confirms. i18n keys render as text in the e2e browser, so
    // match case-insensitively.
    await expect(page.getByText(/refund(ed| success)/i).first()).toBeVisible();
    await expect(page.getByRole('button', { name: /refund/i })).toHaveCount(0);
  });

  test('does not show refund for an already refunded sale', async ({ page }) => {
    await page.addInitScript(
      `window.__TAURI_MOCK_SET__('get_transactions', [${JSON.stringify({
        ...COMPLETED_SALE,
        status: 'refunded',
      })}]);`,
    );
    await page.goto('/transactions');

    await expect(page.getByText(/refunded/i).first()).toBeVisible();
    await expect(page.getByRole('button', { name: /refund/i })).toHaveCount(0);
  });
});
