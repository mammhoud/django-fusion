import { test, expect } from '@playwright/test';
import { CLOUD_ADMIN } from '../../helpers/sync';

/**
 * Formint Cloud browser flows (backend-rendered pages served by Django).
 *
 * Runs against the Django backend (runserver :8082), which serves the Unfold
 * admin, the bolt analytics dashboard, and the industrial-brutalist Sync
 * Monitor. Screenshots land in `projects/formints/docs/screenshots/`.
 */

const SHOTS = '../../docs/screenshots';

test.describe('cloud dashboard', () => {
  test('sync monitor renders masthead + tabs and captures a screenshot', async ({ page }) => {
    await page.goto(`${CLOUD_ADMIN}/apis/data/sync-monitor`);
    await expect(page.locator('.masthead h1')).toContainText('SYNC MONITOR');
    await expect(page.locator('.tab-bar')).toBeVisible();

    // Interaction: switch to the QUEUE tab.
    await page.locator('.tab[data-tab="queue"]').click();
    await expect(page.locator('#tab-queue')).toHaveClass(/active/);

    await page.screenshot({ path: `${SHOTS}/admin/cloud-sync-monitor.png`, fullPage: true });
  });

  test('analytics dashboard renders KPI cards + captures a screenshot', async ({ page }) => {
    await page.goto(`${CLOUD_ADMIN}/apis/data/`);
    await expect(page.locator('.topbar-brand h1')).toContainText('Formint Cloud Analytics');
    await expect(page.locator('.kpi-grid .kpi-card')).toHaveCount(6);

    await page.screenshot({ path: `${SHOTS}/admin/cloud-analytics.png`, fullPage: true });
  });

  test('Unfold admin login renders + captures a screenshot', async ({ page }) => {
    await page.goto(`${CLOUD_ADMIN}/admin/login/`);
    await expect(page.locator('form')).toBeVisible();
    await page.screenshot({ path: `${SHOTS}/admin/cloud-admin-login.png`, fullPage: true });
  });
});
