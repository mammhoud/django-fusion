import { test, expect } from '@playwright/test';

/**
 * Cloud monitor e2e suite (Task C7).
 *
 * Requires the cloud stack:
 *   - backend API on :8767 (`make dev-api` from projects/formints/formint-cloud)
 *   - frontend dev server (started automatically by the Playwright webServer)
 *
 * Covers:
 *   - the /monitor/status JSON contract (db health, last backup, queue depth)
 *   - the /fusion/monitor fragment tile rendering the latest backup
 *   - the /telemetry page surfacing monitor status (via CloudMonitorTile)
 */

test('monitor endpoint returns the JSON contract', async ({ request }) => {
  const res = await request.get('http://127.0.0.1:8767/monitor/status');
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(body).toHaveProperty('database');
  expect(body).toHaveProperty('last_backup');
  expect(body).toHaveProperty('sync_queue_depth');
});

test('monitor fragment renders the latest backup at /fusion/monitor', async ({ request }) => {
  const res = await request.get('http://127.0.0.1:8767/fusion/monitor');
  expect(res.status()).toBe(200);
  const html = await res.text();
  // The fragment tile renders the last backup filename and queue depth.
  expect(html).toContain('Cloud Backup Monitor');
  expect(html).toContain('Sync queue depth');
});

test('monitor status shows a healthy database on /telemetry', async ({ page }) => {
  await page.goto('/telemetry');
  await expect(page.getByText('OK').first()).toBeVisible();
});
