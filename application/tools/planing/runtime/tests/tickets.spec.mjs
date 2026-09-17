import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { test, expect } from '@playwright/test';

// Support tickets: custom field definitions, ticket CRUD through the modal
// editor, validation of required custom fields, replies, and seeded samples.
// Runs on the extra config's server. Only one bootstrap admin exists per
// server, and appearance-and-graph.spec.mjs creates it — so we log in as that
// pinned account instead of registering (the file only exists after that spec
// ran; config order guarantees it in `npm test`).

test.describe.configure({ mode: 'serial' });

let adminToken;
let admin;

// Shared bootstrap credentials for this config. The appearance spec registers
// this account first and pins it; a filtered run (e.g. `--grep retention`) skips
// that spec, so this suite creates the same bootstrap account when the pin file
// is absent. Either way exactly one account exists on the fresh server.
const BOOTSTRAP = { name: 'pw-appearance', password: 'appearance-pass-1' };

test.beforeAll(async ({ request }) => {
  const pinFile = path.join(os.tmpdir(), `planing-pw-extra-admin-${process.env.PLANING_PW_RUN}.json`);
  admin = fs.existsSync(pinFile) ? JSON.parse(fs.readFileSync(pinFile, 'utf8')) : BOOTSTRAP;
  let res = await request.post('/api/auth/login', { data: admin });
  if (!res.ok()) {
    res = await request.post('/api/auth/register', { data: admin });
    expect(res.ok()).toBeTruthy();
  }
  const body = await res.json();
  adminToken = body.token;
});

async function api(path, options = {}) {
  const res = await request.fetch(path, {
    ...options,
    headers: { 'content-type': 'application/json', authorization: `Bearer ${adminToken}`, ...(options.headers || {}) },
  });
  return res;
}

async function signIn(page) {
  await page.goto('/');
  await page.locator('#switch-auth').click();
  await page.fill('#username', admin.name);
  await page.fill('#password', admin.password);
  await page.click('#auth-form button[type="submit"]');
  await expect(page.locator('#app-panel')).toBeVisible();
}

test('manages custom field definitions from settings', async ({ page }) => {
  await signIn(page);
  await page.click('[data-view="settings"]');
  await page.click('[data-settings-tab="tickets"]');
  // Create a required select field.
  await page.fill('#ticket-field-label', 'Region');
  await page.selectOption('#ticket-field-type', 'select');
  await page.fill('#ticket-field-options', 'EU, US, APAC');
  await page.check('#ticket-field-required');
  await page.click('#ticket-field-form button[type="submit"]');
  await expect(page.locator('#ticket-fields-message')).toContainText(/added/i);
  await expect(page.locator('#ticket-fields-list')).toContainText('Region');
  await expect(page.locator('#ticket-fields-list')).toContainText('EU / US / APAC');
  // A second field of a scalar type.
  await page.fill('#ticket-field-label', 'CSAT score');
  await page.selectOption('#ticket-field-type', 'number');
  await page.click('#ticket-field-form button[type="submit"]');
  await expect(page.locator('#ticket-fields-list .ticket-field-row')).toHaveCount(2);
  // Delete the number field explicitly (rows sort alphabetically within the
  // same sort_order, so positional selectors are ambiguous); Region stays.
  await page.locator('#ticket-fields-list .ticket-field-row', { hasText: 'CSAT score' }).locator('[data-ticket-field-delete]').click();
  await expect(page.locator('#ticket-fields-list .ticket-field-row')).toHaveCount(1);
  await expect(page.locator('#ticket-fields-list')).toContainText('Region');
});

test('creates a ticket through the modal with custom fields and edits it', async ({ page }) => {
  await signIn(page);
  await page.click('[data-view="tickets"]');
  await page.click('#ticket-new');
  await expect(page.locator('#ticket-editor .modal-dialog')).toBeVisible();
  await page.fill('#ticket-subject', 'Printer on fire');
  await page.fill('#ticket-description', 'Smoke detected near the paper tray.');
  // Custom select (required) must be filled before submit succeeds.
  const regionSelect = page.locator('#ticket-editor select[data-cf-id]');
  await expect(regionSelect).toBeVisible();
  await page.click('#ticket-form button[type="submit"]');
  await expect(page.locator('#tickets-message')).toContainText(/Validation failed|required/i);
  await regionSelect.selectOption('EU');
  await page.click('#ticket-form button[type="submit"]');
  await expect(page.locator('#ticket-editor .modal-dialog')).toBeHidden();
  await expect(page.locator('.ticket-card', { hasText: 'Printer on fire' })).toBeVisible();
  await expect(page.locator('.ticket-card', { hasText: 'Printer on fire' })).toContainText('EU');

  // Reopen through the card, edit the status, verify the record details show.
  await page.locator('.ticket-card', { hasText: 'Printer on fire' }).click();
  await expect(page.locator('#ticket-editor .modal-dialog')).toBeVisible();
  await page.selectOption('#ticket-status', 'open');
  await page.selectOption('#ticket-priority', 'urgent');
  await page.click('#ticket-form button[type="submit"]');
  await expect(page.locator('#ticket-editor .modal-dialog')).toBeHidden();
  await expect(page.locator('.ticket-card', { hasText: 'Printer on fire' })).toContainText(/open/i);
});

test('adds replies inside the ticket modal', async ({ page }) => {
  await signIn(page);
  await page.click('[data-view="tickets"]');
  await page.locator('.ticket-card', { hasText: 'Printer on fire' }).click();
  await expect(page.locator('#ticket-editor .modal-dialog')).toBeVisible();
  await page.fill('#ticket-reply-body', 'Extinguisher deployed, monitoring.');
  await page.click('#ticket-reply-form button[type="submit"]');
  await expect(page.locator('#ticket-replies-list')).toContainText('Extinguisher deployed');
  await expect(page.locator('.ticket-replies-section .appearance-sublabel')).toContainText('1');
});

test('samples seed demo tickets idempotently', async ({ page }) => {
  await signIn(page);
  await page.click('[data-view="settings"]');
  await page.click('[data-settings-tab="data"]');
  const first = await page.evaluate(async () => {
    const token = localStorage.getItem('planing-token');
    const res = await fetch('/api/samples', { method: 'POST', headers: { authorization: `Bearer ${token}` } });
    return res.json();
  });
  expect(first.imported.tickets.created).toBeGreaterThan(0);
  const second = await page.evaluate(async () => {
    const token = localStorage.getItem('planing-token');
    const res = await fetch('/api/samples', { method: 'POST', headers: { authorization: `Bearer ${token}` } });
    return res.json();
  });
  expect(second.imported.tickets.created).toBe(0);
  // Status filter chips drive the list.
  await page.click('[data-view="tickets"]');
  await page.click('[data-ticket-status="open"]');
  await expect(page.locator('.ticket-card', { hasText: 'Login fails for SSO customers' })).toBeVisible();
  await page.click('[data-ticket-status="closed"]');
  await expect(page.locator('.ticket-card', { hasText: 'Invoice shows wrong VAT rate' })).toBeVisible();
  // Search narrows by subject.
  await page.click('[data-ticket-status=""]');
  await page.fill('#ticket-search', 'webhook');
  await expect(page.locator('.ticket-card')).toHaveCount(1);
});

test('retention controls persist and purge expired recycle-bin notes', async ({ page }) => {
  await signIn(page);
  await page.click('[data-view="settings"]');
  await page.click('[data-settings-tab="data"]');
  // The retention form shows the current (unset) state: empty = forever.
  await expect(page.locator('#retention-days')).toHaveValue('');
  // Set a 1-day window through the UI.
  await page.fill('#retention-days', '1');
  await page.click('#retention-form button[type="submit"]');
  await expect(page.locator('#retention-message')).toContainText(/1/);
  // Create a note and move it to the recycle bin. Both writes go through the
  // app's own bearer token (page.request has no localStorage and would 401),
  // exactly like the recycle flow the UI performs.
  const noteId = await page.evaluate(async () => {
    const token = localStorage.getItem('planing-token');
    const res = await fetch('/api/notes', {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` },
      body: JSON.stringify({ content: 'retention spec purge target', category: 'notes' }),
    });
    const note = await res.json();
    const patched = await fetch(`/api/notes/${note.id}`, {
      method: 'PATCH',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` },
      body: JSON.stringify({ isRecycle: true }),
    });
    return patched.ok ? note.id : null;
  });
  expect(noteId).toBeTruthy();
  // The note was just recycled, so it is inside the 1-day window: the sweep is
  // a no-op. (Deleting an older bin entry needs a backdated `updated_at`,
  // which the API deliberately does not expose — the destructive path is
  // covered by the server-level retention smoke test instead.)
  const purgeResult = await page.evaluate(async () => {
    const token = localStorage.getItem('planing-token');
    const res = await fetch('/api/retention/purge', { method: 'POST', headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' }, body: '{}' });
    return res.json();
  });
  expect(purgeResult.purgedNotes).toBe(0);
  const recycleCount = await page.evaluate(async () => {
    const token = localStorage.getItem('planing-token');
    const res = await fetch('/api/notes?view=recycle', { headers: { authorization: `Bearer ${token}` } });
    return (await res.json()).length;
  });
  expect(recycleCount).toBeGreaterThanOrEqual(1);
  // Disable retention again: empty field = forever.
  await page.fill('#retention-days', '');
  await page.click('#retention-form button[type="submit"]');
  await expect(page.locator('#retention-message')).toContainText(/disabled/i);
});
