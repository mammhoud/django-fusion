import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { test, expect } from '@playwright/test';

// Regression coverage for the Tier-1 appearance tokens and the graph
// timeline/orphan/force-layout work. Runs against the deployed runtime config
// contract (baseURL from playwright.config.mjs, isolated engine per run).

const dir = path.dirname(fileURLToPath(import.meta.url));
const shotDir = path.join(dir, 'test-results', 'artifacts');
fs.mkdirSync(shotDir, { recursive: true });

test.describe.configure({ mode: 'serial' });

let adminToken;

test.beforeAll(async ({ request }) => {
  const res = await request.post('/api/auth/register', { data: { name: 'pw-appearance', password: 'appearance-pass-1' } });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  adminToken = body.token;
  // This spec owns the extra config's bootstrap admin. tickets.spec.mjs runs on
  // the same server and logs in as this account instead of registering (only
  // the first account may bootstrap; later registrations need invitations).
  try { fs.writeFileSync(path.join(os.tmpdir(), `planing-pw-extra-admin-${process.env.PLANING_PW_RUN}.json`), JSON.stringify({ name: 'pw-appearance', password: 'appearance-pass-1' })); } catch { /* best effort */ }
  // Seed a few dated notes so the graph has nodes, edges, and a timeline range.
  for (let i = 0; i < 4; i++) {
    const created = await request.post('/api/notes', {
      headers: { authorization: `Bearer ${adminToken}` },
      data: {
        content: `# Graph node ${i}\n\nlinks to [[Graph node ${(i + 1) % 4}]]`,
        category: 'notes',
        status: 'todo',
        dueDate: new Date(Date.now() + i * 86400000).toISOString(),
      },
    });
    expect(created.ok()).toBeTruthy();
  }
});

async function signIn(page) {
  await page.goto('/');
  // First visit has no stored token, so the auth form shows in register mode;
  // flip to sign-in unless the switcher already says the form is on sign-in.
  // Later visits auto-enter via the stored token (localStorage planing-token),
  // so the auth form never appears — just wait for the workspace.
  // Branch on the token instead of panel visibility: enterApp() is async, so a
  // reload briefly shows neither panel. Playwright contexts start with empty
  // localStorage, so a token here can only come from an earlier signIn in this
  // same test — deterministic, no race.
  const token = await page.evaluate(() => localStorage.getItem('planing-token'));
  if (token) {
    await expect(page.locator('#app-panel')).toBeVisible();
    return;
  }
  const switcher = page.locator('#switch-auth');
  if (((await switcher.textContent()) || '').includes('Sign in')) await switcher.click();
  await page.fill('#username', 'pw-appearance');
  await page.fill('#password', 'appearance-pass-1');
  await page.click('#auth-form button[type="submit"]');
  await expect(page.locator('#app-panel')).toBeVisible();
}

test('appearance: radius + density tokens apply and persist', async ({ page }) => {
  await signIn(page);
  await page.click('[data-view="settings"]');
  await page.click('[data-settings-tab="appearance"]');
  // Square corners
  await page.click('#radius-options [data-option-value="none"]');
  await expect(page.locator('html')).toHaveAttribute('data-radius-scale', 'none');
  await expect(page.locator('#appearance-message')).toContainText(/saved|SurrealDB/i);
  await page.screenshot({ path: `${shotDir}/appearance-radius-none.png` });
  // Compact density
  await page.click('#density-options [data-option-value="compact"]');
  await expect(page.locator('html')).toHaveAttribute('data-density', 'compact');
  // Floating shadow
  await page.click('#shadow-options [data-option-value="floating"]');
  await expect(page.locator('html')).toHaveAttribute('data-shadow-depth', 'floating');
  // Strong edges
  await page.click('#edge-options [data-option-value="strong"]');
  await expect(page.locator('html')).toHaveAttribute('data-edge-strength', 'strong');

  // Persist across reload: settings come back from SurrealDB.
  await page.reload();
  await signIn(page);
  await expect(page.locator('html')).toHaveAttribute('data-radius-scale', 'none');
  await expect(page.locator('html')).toHaveAttribute('data-density', 'compact');
  await expect(page.locator('html')).toHaveAttribute('data-shadow-depth', 'floating');
  await expect(page.locator('html')).toHaveAttribute('data-edge-strength', 'strong');

  // Element-tier axes: buttons and badges (the reload above reset the view
  // back to notes, so re-open the settings tab first).
  await page.click('[data-view="settings"]');
  await page.click('[data-settings-tab="appearance"]');
  await page.click('#button-style-options [data-option-value="outline"]');
  await expect(page.locator('html')).toHaveAttribute('data-button-style', 'outline');
  await page.click('#badge-style-options [data-option-value="tinted"]');
  await expect(page.locator('html')).toHaveAttribute('data-badge-style', 'tinted');
  // Theme variant ported from Formints.
  await page.click('#theme-variant-options [data-option-value="luxury"]');
  await expect(page.locator('html')).toHaveAttribute('data-theme-variant', 'luxury');

  // Presets are PATCH bundles; applying one must move every axis at once.
  await page.click('[data-preset="midnight"]');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await expect(page.locator('html')).toHaveAttribute('data-theme-variant', 'corporate');
  await expect(page.locator('html')).toHaveAttribute('data-button-style', 'solid');
  await expect(page.locator('html')).toHaveAttribute('data-badge-style', 'solid');
  await expect(page.locator('html')).toHaveAttribute('data-shadow-depth', 'floating');
  await expect(page.locator('html')).toHaveAttribute('data-density', 'cozy');
  await expect(page.locator('html')).toHaveAttribute('data-radius-scale', 'soft');

  // Persist across reload: settings come back from SurrealDB.
  await page.reload();
  await signIn(page);
  await expect(page.locator('html')).toHaveAttribute('data-radius-scale', 'soft');
  await expect(page.locator('html')).toHaveAttribute('data-density', 'cozy');
  await expect(page.locator('html')).toHaveAttribute('data-shadow-depth', 'floating');
  // Midnight defines edgeStrength 'default', overriding the 'strong' set above —
  // receiving 'default' here proves the preset replaced every axis.
  await expect(page.locator('html')).toHaveAttribute('data-edge-strength', 'default');
  await expect(page.locator('html')).toHaveAttribute('data-theme-variant', 'corporate');
  await expect(page.locator('html')).toHaveAttribute('data-button-style', 'solid');
  await expect(page.locator('html')).toHaveAttribute('data-badge-style', 'solid');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');

  // Restore defaults for the rest of the run.
  await page.click('[data-view="settings"]');
  await page.click('[data-settings-tab="appearance"]');
  await page.click('[data-preset="industrial"]');
  await expect(page.locator('html')).toHaveAttribute('data-radius-scale', 'subtle');
  await page.click('[data-preset="default"]', { timeout: 2000 }).catch(() => {});
  await page.click('#radius-options [data-option-value="default"]');
  await page.click('#density-options [data-option-value="cozy"]');
  await page.click('#shadow-options [data-option-value="default"]');
  await page.click('#edge-options [data-option-value="default"]');
  await page.click('#theme-variant-options [data-option-value="default"]');
  await page.click('#button-style-options [data-option-value="default"]');
  await page.click('#badge-style-options [data-option-value="default"]');
  await page.click('#theme-options [data-option-value="light"]');
  await page.click('#accent-options [data-option-value="violet"]');
  await page.click('#font-scale-options [data-option-value="default"]');
  await page.click('#style-options [data-option-value="sharp"]');
  await expect(page.locator('html')).toHaveAttribute('data-radius-scale', 'default');
});

test('graph: timeline playback and orphan toggle', async ({ page }) => {
  await signIn(page);
  await page.click('[data-view="graph"]');
  await expect(page.locator('.graph-node')).toHaveCount(4);
  await page.screenshot({ path: `${shotDir}/graph-initial.png` });

  // Force layout settles with positions inside the viewport and no overlaps
  // between the first two nodes. The simulation is still running when the node
  // count assertion passes — a single measurement caught the pair at 15.2px
  // mid-settle — so poll the separation instead of reading it once.
  await expect.poll(async () => {
    const first = await page.locator('.graph-node circle').first().boundingBox();
    const second = await page.locator('.graph-node circle').nth(1).boundingBox();
    if (!first || !second) return 0;
    return Math.hypot(first.x - second.x, first.y - second.y);
  }, { timeout: 10_000 }).toBeGreaterThan(16);

  // Tooltip on hover
  await page.locator('.graph-node circle').first().hover();
  await expect(page.locator('#graph-tooltip')).toBeVisible();

  // Drawer on click with links + backlinks sections. Clear the hover first:
  // hover re-scales nodes and a highlighted neighbor can intercept the click.
  // The tooltip hides via a 'visible' class, not display, so assert on that.
  await page.mouse.move(10, 400);
  await expect(page.locator('#graph-tooltip')).not.toHaveClass(/visible/);
  await page.locator('.graph-node').first().click({ force: true });
  await expect(page.locator('#graph-drawer')).toBeVisible();
  await expect(page.locator('#graph-drawer')).toContainText(/LINKED NOTES|linksTitle/i);
  await page.screenshot({ path: `${shotDir}/graph-drawer.png` });
  await page.click('#graph-drawer [data-drawer-close]');
  await expect(page.locator('#graph-drawer')).toBeHidden();

  // Timeline: scrub to the minimum and expect fewer/equal visible nodes, then
  // play and expect the count to recover.
  const before = await page.locator('.graph-node').count();
  const slider = page.locator('#graph-timeline');
  const min = Number(await slider.getAttribute('min'));
  const max = Number(await slider.getAttribute('max'));
  expect(min).toBeLessThan(max);
  await slider.fill(String(min));
  const atMin = await page.locator('.graph-node').count();
  expect(atMin).toBeLessThanOrEqual(before);
  // Playback advances the playhead, re-revealing dated nodes. Poll instead of
  // sleeping so the pause lands as soon as playback demonstrably moved, and
  // only when growth is actually possible (distinct seeded timestamps).
  if (atMin < before) {
    await page.click('#graph-timeline-play');
    await expect.poll(async () => page.locator('.graph-node').count(), { timeout: 10_000 }).toBeGreaterThan(atMin);
  } else {
    await page.click('#graph-timeline-play');
  }
  await page.click('#graph-timeline-play'); // pause
  const after = await page.locator('.graph-node').count();
  expect(after).toBeGreaterThanOrEqual(atMin);
  await page.screenshot({ path: `${shotDir}/graph-after-playback.png` });

  // Orphan toggle: with all nodes linked, hiding orphans must not error and
  // count stays 4; create an orphan note, reload graph state, and expect the
  // toggle to drop it.
  const orphan = await page.request.post('/api/notes', {
    data: { content: '# Orphan island note', category: 'notes' },
    headers: { authorization: `Bearer ${adminToken}` },
  });
  expect(orphan.ok()).toBeTruthy();
  await page.reload();
  await signIn(page);
  await page.click('[data-view="graph"]');
  await expect(page.locator('.graph-node')).toHaveCount(5);
  await page.click('#graph-orphans');
  await expect(page.locator('.graph-node')).toHaveCount(4);
  await page.screenshot({ path: `${shotDir}/graph-orphans-hidden.png` });
});
