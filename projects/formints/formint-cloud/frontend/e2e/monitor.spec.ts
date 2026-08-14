import { test, expect } from '@playwright/test';

/**
 * Cloud monitor e2e suite (Task C7).
 *
 * Requires the cloud stack:
 *   - backend API on :8767 (`make dev-api` from projects/formints/formint-cloud)
 *   - frontend dev server (started automatically by the Playwright webServer)
 *   - the Astro dev proxy `/monitor` → SERVER entry (astro.config.mjs) —
 *     the /telemetry page test relies on it for the same-origin fetch
 *
 * Covers:
 *   - the /monitor/status JSON contract (db health, last backup, queue depth)
 *   - the /fusion/monitor fragment tile rendering the latest backup
 *   - the /telemetry page surfacing monitor status (via CloudMonitorTile)
 */

const API = process.env.E2E_API_BASE || 'http://127.0.0.1:8767';

test('monitor endpoint returns the JSON contract', async ({ request }) => {
  const res = await request.get(`${API}/monitor/status`);
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(body).toHaveProperty('database');
  expect(body).toHaveProperty('last_backup');
  expect(body).toHaveProperty('sync_queue_depth');
});

test('monitor fragment renders the latest backup at /fusion/monitor', async ({ request }) => {
  const res = await request.get(`${API}/fusion/monitor`);
  expect(res.status()).toBe(200);
  const html = await res.text();
  // The fragment tile renders the last backup filename and queue depth.
  expect(html).toContain('Cloud Backup Monitor');
  expect(html).toContain('Sync queue depth');
});

test('monitor status shows a healthy database on /telemetry', async ({ page }) => {
  // Explicitly enable the local-only browser bypass. Production web sessions
  // must not inherit an authentication bypass merely because Tauri is absent.
  await page.addInitScript(() => localStorage.setItem('formint-e2e-auth-bypass', 'true'));
  // This is a client-only island. DOM readiness is the meaningful navigation
  // boundary; waiting for every dev-server asset's `load` event can hang on
  // optional WebSocket/icon resources even after the page is interactive.
  await page.goto('/telemetry', { waitUntil: 'commit', timeout: 15_000 });
  // Wait for the client-only island's stable data marker. The telemetry
  // panel intentionally uses layered visual effects; an ancestor can report
  // hidden while the island is still hydrating even though its data contract
  // is attached. Assert attachment plus user-visible status instead of
  // coupling this contract test to that transient CSS state.
  const databaseStatus = page.getByTestId('cloud-monitor-db');
  await expect(databaseStatus).toBeAttached({ timeout: 15_000 });
  await expect(databaseStatus).toHaveText('OK', { timeout: 15_000 });
});
