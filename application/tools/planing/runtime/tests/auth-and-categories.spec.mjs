import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { test, expect } from '@playwright/test';

// Tests 1..N share one seeded admin. Playwright restarts the worker process
// after a failing test (which re-evaluates this module), so the name is pinned
// for the whole run in a temp file keyed by the run id instead of using
// Date.now() per evaluation — otherwise later tests sign in as a user that was
// never created.
const adminFile = path.join(os.tmpdir(), `planing-pw-admin-${process.env.PLANING_PW_RUN || 'run'}.txt`);
const adminName = (() => {
  try {
    const stored = fs.readFileSync(adminFile, 'utf8').trim();
    if (stored) return stored;
  } catch { /* first evaluation writes the file */ }
  const name = `admin-${Date.now()}`;
  try { fs.writeFileSync(adminFile, name); } catch { /* best effort */ }
  return name;
})();

const admin = { name: adminName, password: 'local-test-password-123' };

async function createAccount(page) {
  await page.goto('/');
  await page.locator('#username').fill(admin.name);
  await page.locator('#password').fill(admin.password);
  await page.getByRole('button', { name: 'Create account' }).click();
  await expect(page.locator('[data-view="notes"]')).toBeVisible();
  await expect(page.locator('#app-panel')).toBeVisible();
}

test('creates admin, notes with markdown/tags/pin, archive and recycle, settings tabs', async ({ page }) => {
  await createAccount(page);

  await expect(page.locator('[data-view="settings"]')).toBeVisible();
  await expect(page.locator('#category-buttons .category-button', { hasText: 'Notes' })).toBeVisible();
  await expect(page.locator('[data-note-view="all"] [data-i18n="viewAll"]')).toBeVisible();

  await page.locator('#new-category').fill('Research');
  await page.getByRole('button', { name: '+ Add' }).click();
  await expect(page.locator('#category-buttons .category-button', { hasText: 'Research' })).toBeVisible();

  const markdown = '# Plan\n\n- **bold** item\n- `code` item\n\n> quote line';
  await page.locator('#note-content').fill(markdown);
  await page.locator('#note-tags').fill('#plan #surreal');
  await page.getByRole('button', { name: 'Save note' }).click();
  await expect(page.locator('.note h1')).toHaveText('Plan');
  await expect(page.locator('.note strong')).toHaveText('bold');
  await expect(page.locator('.note code').first()).toHaveText('code');
  await expect(page.locator('.note blockquote')).toContainText('quote line');
  await expect(page.locator('#tag-chips .tag-chip[data-tag="plan"]')).toBeVisible();
  // Sidebar filters were replaced by toolbar chips; the sr-only mirror keeps
  // the keyboard/a11y path, so assert presence rather than visibility.
  await expect(page.locator('#tag-buttons [data-tag="plan"]')).toHaveCount(1);

  await page.locator('.note-actions [data-note-action="pin"]').first().click();
  await expect(page.locator('.pin-badge')).toBeVisible();
  await page.locator('.note-actions [data-note-action="unpin"]').first().click();
  await expect(page.locator('.pin-badge')).toHaveCount(0);

  await page.locator('.note-actions [data-note-action="edit"]').first().click();
  await expect(page.locator('.note .edit-content')).toBeVisible();
  await page.locator('.note-actions [data-note-action="cancel-edit"]').click();
  await expect(page.locator('.note .edit-content')).toHaveCount(0);

  await page.locator('.note-actions [data-note-action="edit"]').first().click();
  await page.locator('.note .edit-content').fill('# Plan v2\n\nedited body');
  await page.locator('.note .edit-tags').fill('#plan #edited');
  await page.locator('.note-actions [data-note-action="save-edit"]').click();
  await expect(page.locator('.note h1')).toHaveText('Plan v2');
  await expect(page.locator('.note .note-content')).toContainText('edited body');
  await expect(page.locator('#tag-chips .tag-chip[data-tag="edited"]')).toBeVisible();
  await expect(page.locator('#tag-chips .tag-chip[data-tag="surreal"]')).toHaveCount(0);

  await page.locator('.note-actions [data-note-action="archive"]').first().click();
  await expect(page.locator('#note-count')).toHaveText(/0 notes/);
  await page.getByRole('button', { name: /Archive/ }).click();
  await expect(page.locator('.note .note-content')).toContainText('Plan');
  await page.locator('.note-actions [data-note-action="restore"]').first().click();
  await page.getByRole('button', { name: /All notes/ }).click();
  await expect(page.locator('.note .note-content')).toContainText('Plan');

  await page.locator('.note-actions [data-note-action="recycle"]').first().click();
  await page.getByRole('button', { name: /Recycle bin/ }).click();
  await expect(page.locator('.note .note-content')).toContainText('Plan');
  await page.locator('.note-actions [data-note-action="restore"]').first().click();
  await page.getByRole('button', { name: /All notes/ }).click();
  await expect(page.locator('.note .note-content')).toContainText('Plan');

  await page.locator('#note-search').fill('edited body');
  await expect(page.locator('.note .note-content')).toContainText('edited body');
  await page.locator('#note-search').fill('zzz-no-match');
  await expect(page.locator('#notes-empty')).toBeVisible();
  await page.locator('#note-search').fill('');
  await expect(page.locator('.note .note-content')).toContainText('Plan v2');

  await page.locator('#category-buttons .category-button', { hasText: 'Research' }).click();
  await page.locator('#note-content').fill('Dedicated research note');
  await page.getByRole('button', { name: 'Save note' }).click();
  await expect(page.locator('.note', { hasText: 'Dedicated research note' }).locator('.note-content')).toContainText('Dedicated research note');

  await page.locator('[data-lane-edit="research"]').click();
  await expect(page.locator('#category-edit-form')).toBeVisible();
  await page.locator('#category-name-input').fill('Research Lab');
  await page.locator('[data-swatch="#e11d48"]').click();
  await page.locator('#category-edit-form button[type="submit"]').click();
  await expect(page.locator('#category-buttons .category-button', { hasText: 'Research Lab' })).toBeVisible();

  await page.locator('[data-lane-edit="notes"]').click();
  await expect(page.locator('#category-name-input')).toBeDisabled();
  await page.locator('#category-editor-close').click();

  await page.locator('[data-lane-edit="research"]').click();
  page.once('dialog', (dialog) => dialog.accept());
  await page.locator('#category-delete').click();
  await expect(page.locator('#category-buttons .category-button', { hasText: 'Research Lab' })).toHaveCount(0);
  await expect(page.locator('.category-editor-mount')).toBeHidden();
  await page.locator('#category-buttons .category-button', { hasText: 'Notes' }).click();
  await expect(page.locator('.note', { hasText: 'Dedicated research note' }).locator('.note-content')).toContainText('Dedicated research note');

  await page.getByRole('button', { name: /Settings/ }).click();
  await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
  await page.locator('#workspace-name').fill('Team context');
  await page.getByRole('button', { name: 'Save settings' }).click();
  await expect(page.getByText('Settings saved to SurrealDB.')).toBeVisible();

  await page.getByRole('button', { name: 'Appearance' }).click();
  await expect(page.getByText('THEME MODE')).toBeVisible();
  // Scope to the option grids: preset cards' descriptions also contain these
  // words, so unscoped role+name selectors are ambiguous now.
  await page.locator('#accent-options [data-option-value="blue"]').click();
  await expect(page.locator('html')).toHaveAttribute('data-accent', 'blue');
  await page.locator('#theme-options [data-option-value="dark"]').click();
  await expect(page.locator('html[data-theme="dark"]')).toHaveCount(1);
  await page.locator('#theme-options [data-option-value="light"]').click();
  await page.locator('#accent-options [data-option-value="violet"]').click();
  await expect(page.getByText('Appearance saved.')).toBeVisible();

  await page.getByRole('button', { name: 'People', exact: true }).click();
  await expect(page.getByRole('heading', { name: /Give someone a lane/ })).toBeVisible();

  await page.getByRole('button', { name: 'AI', exact: true }).click();
  await expect(page.locator('#ai-context')).toBeVisible();

  await page.getByRole('button', { name: 'Data', exact: true }).click();
  await expect(page.getByText('STORAGE SNAPSHOT')).toBeVisible();
  await expect(page.locator('.snapshot-item').first()).toBeVisible();

  await page.getByRole('button', { name: /Notes/ }).first().click();
  await expect(page.locator('[data-view="notes"]')).toBeVisible();
});

test('applies note actions optimistically and retries them after reconnect', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /Already have an account/ }).click();
  await page.locator('#username').fill(admin.name);
  await page.locator('#password').fill(admin.password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.locator('#app-panel')).toBeVisible({ timeout: 10_000 });
  const notesBtn = page.locator('[data-view="notes"]');
  await notesBtn.scrollIntoViewIfNeeded();
  await expect(notesBtn).toBeVisible({ timeout: 10_000 });
  await page.locator('#note-content').fill('offline optimistic note');
  await page.getByRole('button', { name: 'Save note' }).click();
  const optimisticCard = page.locator('.note').filter({ hasText: 'offline optimistic note' });
  await expect(optimisticCard).toHaveCount(1);
  await expect(optimisticCard.locator('.note-content')).toContainText('offline optimistic note');

  // Sever the connection: mutations now fail at the network level and are
  // queued in the outbox while the optimistic state stays visible.
  await page.route('**/api/notes/**', (route) => route.abort('internetdisconnected'));
  await optimisticCard.locator('[data-note-action="pin"]').click();
  await expect(page.locator('.pin-badge')).toBeVisible();
  await expect(page.locator('#outbox-banner')).toBeVisible();
  await expect(page.locator('[data-outbox-count]')).toHaveText('1');

  // Restore the network: the queued mutation must flush and reconcile.
  await page.unroute('**/api/notes/**');
  await page.locator('#outbox-retry').click();
  await expect(page.locator('#outbox-banner')).toBeHidden();
  await expect(optimisticCard.locator('.pin-badge')).toBeVisible();

  // A permanent rejection must roll the optimistic change back.
  await page.route('**/api/notes/**', async (route) => {
    if (route.request().method() === 'PATCH') {
      await route.fulfill({ status: 403, contentType: 'application/json', body: JSON.stringify({ error: 'Permission denied' }) });
    } else {
      await route.continue();
    }
  });
  await optimisticCard.locator('[data-note-action="unpin"]').click();
  await expect(optimisticCard.locator('.pin-badge')).toHaveCount(0);
  await expect(page.locator('#app-message')).toContainText('Permission denied');
  await page.unroute('**/api/notes/**');
});

test('exports workspace JSON, restores it through import, and never duplicates on re-import', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /Already have an account/ }).click();
  await page.locator('#username').fill(admin.name);
  await page.locator('#password').fill(admin.password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.locator('#app-panel')).toBeVisible({ timeout: 10_000 });
  const notesBtn = page.locator('[data-view="notes"]');
  await notesBtn.scrollIntoViewIfNeeded();
  await expect(notesBtn).toBeVisible({ timeout: 10_000 });

  // Create a dedicated note to track through the round trip.
  const marker = `export round-trip ${Date.now()}`;
  await page.locator('#note-content').fill(marker);
  await page.getByRole('button', { name: 'Save note' }).click();
  const markerCard = page.locator('.note').filter({ hasText: marker });
  await expect(markerCard).toHaveCount(1);

  // Export via the API and capture the payload.
  const exportHandle = await page.evaluate(async () => {
    const response = await fetch('/api/export', { headers: { authorization: `Bearer ${localStorage.getItem('planing-token')}` } });
    return { status: response.status, body: await response.json() };
  });
  expect(exportHandle.status).toBe(200);
  expect(exportHandle.body.schemaVersion).toMatch(/^workspace-v\d+$/);
  expect(Array.isArray(exportHandle.body.notes)).toBe(true);
  expect(exportHandle.body.notes.some((note) => note.content.includes(marker))).toBe(true);

  // Delete the note permanently, then import the payload back.
  const noteId = exportHandle.body.notes.find((note) => note.content.includes(marker)).id;
  await page.evaluate(async (id) => {
    await fetch(`/api/notes/${encodeURIComponent(id)}`, { method: 'DELETE', headers: { authorization: `Bearer ${localStorage.getItem('planing-token')}` } });
  }, noteId);
  await page.reload();
  await expect(page.locator('[data-view="notes"]')).toBeVisible();
  await expect(markerCard).toHaveCount(0);

  const importResult = await page.evaluate(async (payload) => {
    const response = await fetch('/api/import', { method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${localStorage.getItem('planing-token')}` }, body: JSON.stringify(payload) });
    return { status: response.status, body: await response.json() };
  }, exportHandle.body);
  expect(importResult.status).toBe(200);
  expect(importResult.body.imported.notes).toBeGreaterThanOrEqual(1);
  await page.reload();
  await expect(page.locator('[data-view="notes"]')).toBeVisible();
  await expect(markerCard).toHaveCount(1);

  // Re-importing the same file must be a no-op (idempotency).
  const reimport = await page.evaluate(async (payload) => {
    const response = await fetch('/api/import', { method: 'POST', headers: { 'content-type': 'application/json', authorization: `Bearer ${localStorage.getItem('planing-token')}` }, body: JSON.stringify(payload) });
    return { status: response.status, body: await response.json() };
  }, exportHandle.body);
  expect(reimport.status).toBe(200);
  expect(reimport.body.imported.notes).toBe(0);
  await page.reload();
  await expect(page.locator('[data-view="notes"]')).toBeVisible();
  await expect(markerCard).toHaveCount(1);
});

test('invites a teammate, shares a note publicly, and shows workspace activity', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await page.goto('/');
  await page.getByRole('button', { name: /Already have an account/ }).click();
  await page.locator('#username').fill(admin.name);
  await page.locator('#password').fill(admin.password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.locator('#app-panel')).toBeVisible({ timeout: 10_000 });
  const notesBtn = page.locator('[data-view="notes"]');
  await notesBtn.scrollIntoViewIfNeeded();
  await expect(notesBtn).toBeVisible({ timeout: 10_000 });
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };

  // Create a shareable note and share it.
  const shared = await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `public share check ${Date.now()}`, category: 'notes' }) });
  const note = await shared.json();
  expect(shared.status()).toBe(201);
  const shareToggle = await api(`/api/notes/${encodeURIComponent(note.id)}/share`, { method: 'PATCH', headers: auth, data: JSON.stringify({ share: true }) });
  expect(shareToggle.status()).toBe(200);
  const publicView = await request.fetch(`${baseURL}/share/${encodeURIComponent(note.id)}`);
  expect(publicView.status()).toBe(200);
  expect(await publicView.text()).toContain('public share check');
  // Unshared notes vanish from the public URL.
  await api(`/api/notes/${encodeURIComponent(note.id)}/share`, { method: 'PATCH', headers: auth, data: JSON.stringify({ share: false }) });
  expect((await request.fetch(`${baseURL}/share/${encodeURIComponent(note.id)}`)).status()).toBe(404);

  // Invite flow: create code, register a teammate with it, verify membership.
  const invite = await (await api('/api/invitations', { method: 'POST', headers: auth, data: JSON.stringify({ role: 'editor' }) })).json();
  expect(invite.code).toBeTruthy();
  const teammate = { name: `editor-${Date.now()}`, password: 'local-test-password-123' };
  const signup = await api('/api/auth/register', { method: 'POST', data: JSON.stringify({ ...teammate, invite: invite.code }) });
  expect(signup.status()).toBe(201);
  const memberProfile = await (await api('/api/auth/profile', { headers: { authorization: `Bearer ${(await signup.json()).token}` } })).json();
  expect(memberProfile.user.role).toBe('editor');
  // Registration without a code is closed.
  expect((await api('/api/auth/register', { method: 'POST', data: JSON.stringify({ name: 'no-code-user', password: 'local-test-password-123' }) })).status()).toBe(403);
  // The same code cannot be used twice.
  expect((await api('/api/auth/register', { method: 'POST', data: JSON.stringify({ name: 'code-reuse-user', password: 'local-test-password-123', invite: invite.code }) })).status()).toBe(403);
  // The teammate shares the workspace stream and can write notes.
  const teammateNote = await api('/api/notes', { method: 'POST', headers: { authorization: `Bearer ${(await signup.json()).token}` }, data: JSON.stringify({ content: 'from the invited editor', category: 'notes' }) });
  expect(teammateNote.status()).toBe(201);
  const adminStream = await (await api('/api/notes', { headers: auth })).json();
  expect(adminStream.some((entry) => entry.content === 'from the invited editor')).toBe(true);

  // Workspace activity records the mutations.
  const audit = await (await api('/api/audit', { headers: auth })).json();
  expect(audit.some((event) => event.action === 'note.share')).toBe(true);
  expect(audit.some((event) => event.action === 'invite.accept')).toBe(true);

  // UI: invitations render in People and the Activity tab lists events.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="people"]').click();
  await expect(page.locator('#invite-panel')).toBeVisible();
  await page.locator('[data-settings-tab="activity"]').click();
  await expect(page.locator('.audit-row').first()).toBeVisible();
});

test('switches the complete shell to Arabic RTL and stays within a mobile viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await page.locator('#locale-toggle').click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page).toHaveTitle('بلينكو — سياق مشترك.');
  await expect(page.getByRole('heading', { name: 'أنشئ حساب المدير' })).toBeVisible();
  await expect(page.getByPlaceholder('اسمك')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
  await page.locator('#locale-toggle').click();
  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
});

test('rejects invalid credentials', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /Already have an account/ }).click();
  await page.locator('#username').fill('missing-user');
  await page.locator('#password').fill('wrong-password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('alert')).toContainText('Invalid credentials');
});



// Tests 7/8 reuse the shared admin created by test 1 (registration is
// invite-only afterwards by design). Isolation comes from per-run namespaces.
async function signInAsSharedAdmin(page) {
  await page.goto('/');
  await page.getByRole('button', { name: /Already have an account/ }).click();
  await page.locator('#username').fill(admin.name);
  await page.locator('#password').fill(admin.password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.locator('#app-panel')).toBeVisible({ timeout: 10_000 });
  await expect(page.locator('#notes-view:not(.hidden)')).toBeVisible({ timeout: 10_000 });
}

test('loads sample content and renders GFM elements inside note cards', async ({ page }) => {
  await signInAsSharedAdmin(page);
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="data"]').click();
  await page.locator('#samples-form button[type="submit"]').click();
  await expect(page.locator('#samples-message')).toContainText(/Samples loaded|Samples refreshed|already loaded/);
  // Back to notes: sample cards render GFM structures.
  await page.locator('[data-view="notes"]').click();
  await page.locator('#category-buttons .category-button', { hasText: 'Playbook' }).click();
  // Scope by the exact heading: several samples mention this title inline.
  const showcase = page.locator('.note').filter({ has: page.getByRole('heading', { name: 'Markdown showcase', exact: true }) });
  await expect(showcase).toBeVisible();
  await expect(showcase.locator('table')).toBeVisible();
  await expect(showcase.locator('table th').first()).toContainText('Feature');
  await expect(showcase.locator('li.task-item input[type="checkbox"]').first()).toBeVisible();
  await expect(showcase.locator('blockquote')).toContainText('Capture the thought');
  await expect(showcase.locator('pre[data-lang="js"] code')).toContainText('greet');
  await expect(showcase.locator('pre[data-lang="sql"]')).toHaveCount(1);
  await expect(showcase.locator('mark')).toContainText('highlighted');
  await expect(showcase.locator('hr')).toHaveCount(1);
  // Samples are cross-linked, so the link graph is populated, not empty.
  await expect(showcase.locator('.wikilink')).toHaveCount(5);
  await showcase.locator('[data-note-action="links"]').click();
  const linkPanel = showcase.locator('.note-links');
  await expect(linkPanel).toContainText('LINKED NOTES');
  await expect(linkPanel).not.toContainText('No outgoing links yet');
  // Copy-markdown action copies the raw source.
  await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
  await showcase.locator('[data-note-action="copy-md"]').click();
  await expect(page.locator('#app-message')).toContainText('Markdown copied');
  // Re-loading is idempotent: nothing is duplicated, content is refreshed.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="data"]').click();
  await page.locator('#samples-form button[type="submit"]').click();
  await expect(page.locator('#samples-message')).toContainText(/Samples refreshed|already loaded/);
});

test('wides the markdown editor, exposes formatting tooltips, and inserts markdown', async ({ page }) => {
  await signInAsSharedAdmin(page);
  const composer = page.locator('#composer');
  const textarea = page.locator('#note-content');
  const toolbar = composer.locator('.editor-toolbar');
  await expect(toolbar).toBeVisible();

  // Every toolbar control carries a localized tooltip rather than a bare glyph.
  const tooltips = await toolbar.locator('button[data-md-insert]').evaluateAll((nodes) => nodes.map((node) => node.getAttribute('title')));
  expect(tooltips.length).toBeGreaterThanOrEqual(15);
  expect(tooltips.every((title) => title && title.length > 3)).toBe(true);

  // The Wide toggle widens the editing surface and persists the choice.
  const wideToggle = page.locator('#composer-expand-toggle');
  await wideToggle.click();
  await expect(wideToggle).toHaveAttribute('aria-pressed', 'true');
  await expect(composer).toHaveClass(/is-wide/);
  expect(await page.evaluate(() => localStorage.getItem('planing-composer-wide'))).toBe('1');

  // Inserting a wiki link from the toolbar writes markdown at the caret.
  await textarea.click();
  await toolbar.locator('[data-md-insert="wikilink"]').click();
  await expect(textarea).toHaveValue(/\[\[Note title\]\]/);
  await toolbar.locator('[data-md-insert="table"]').click();
  await expect(textarea).toHaveValue(/\| Column \| Value \|/);

  // A live preview renders beside the source once toggled on.
  await textarea.fill('# Draft heading\n\n- [ ] first task');
  await page.locator('#composer-preview-toggle').click();
  const preview = page.locator('#composer-preview');
  await expect(preview.locator('h1')).toContainText('Draft heading');
  await expect(preview.locator('li.task-item input[type="checkbox"]')).toHaveCount(1);

  // Inline note editing opens with the same wide surface and toolbar.
  await page.locator('[data-view="notes"]').click();
  const firstNote = page.locator('.note').first();
  await firstNote.locator('[data-note-action="edit"]').click();
  const editing = page.locator('.note.editing');
  await expect(editing.locator('.editor-surface')).toHaveClass(/is-wide/);
  await expect(editing.locator('.editor-toolbar button')).toHaveCount(15);
  await editing.locator('[data-note-action="cancel-edit"]').click();
  await expect(page.locator('.note.editing')).toHaveCount(0);

  // Restore the default composer width for later tests.
  await wideToggle.click();
  await expect(wideToggle).toHaveAttribute('aria-pressed', 'false');
});

test('configures a provider, chats over it, and switches prompt styles', async ({ page }) => {
  await signInAsSharedAdmin(page);

  // Provider setup in Settings → AI.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="ai"]').click();
  await page.locator('#provider-name').fill('mock-llm');
  await page.locator('#provider-base-url').fill('http://127.0.0.1:11434/v1');
  await page.locator('#provider-model').fill('mock-model');
  await page.locator('#provider-api-key').fill('mock-key-123');
  await page.locator('.provider-activate input').check();
  await page.locator('#provider-form button[type="submit"]').click();
  await expect(page.locator('#provider-message')).toContainText('Provider saved');
  const row = page.locator('.provider-row').filter({ hasText: 'mock-llm' });
  await expect(row).toBeVisible();
  await expect(row).toContainText('ACTIVE');
  await expect(row).not.toContainText('mock-key-123'); // key never echoed back

  // Verify hits the mock /models endpoint.
  await row.locator('[data-i18n="edit"]').click();
  await page.locator('[data-i18n="providerVerify"]').click();
  await expect(page.locator('#provider-message')).toContainText('Provider reachable');

  // Chat: new session, prompt style choice, message round trip.
  await page.locator('[data-view="chat"]').click();
  await expect(page.locator('#chat-view')).toBeVisible();
  await expect(page.locator('#chat-sessions')).toHaveCount(1);
  await page.locator('#chat-prompt').selectOption({ index: 1 });
  await page.locator('#chat-new').click();
  await page.locator('#chat-input').fill('hello mock model');
  await page.locator('#chat-form button[type="submit"]').click();
  const reply = page.locator('.chat-bubble.from-ai').first();
  await expect(reply).toContainText('Mock reply to "hello mock model"');
  await expect(reply).toContainText('system:yes'); // prompt template reached the provider

  // Session list keeps the conversation; reopening restores messages.
  await expect(page.locator('.chat-session-item')).toHaveCount(1);
  await page.reload();
  await page.locator('[data-view="chat"]').click();
  await page.locator('.chat-session-item').first().click();
  await expect(page.locator('.chat-bubble.from-ai').first()).toContainText('Mock reply');
});

test('imports markdown files as notes and navigates the note link graph', async ({ page }) => {
  await signInAsSharedAdmin(page);
  const stamp = Date.now();
  const title = `Study note ${stamp}`;
  const linked = `Manual ${stamp}`;
  const files = [
    { name: 'study-note.md', mimeType: 'text/markdown', buffer: Buffer.from(`# ${title}\n\nSee [[${linked}]] for the next step.\n\n- [ ] revise\n- [x] draft\n`) },
    { name: 'linked.md', mimeType: 'text/markdown', buffer: Buffer.from(`# ${linked}\n\nFollow-up detail.\n`) },
  ];

  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="data"]').click();
  await page.locator('#markdown-files').setInputFiles(files);
  await page.locator('#markdown-import-form button[type="submit"]').click();
  await expect(page.locator('#markdown-import-message')).toContainText('Imported 2 markdown');

  // Re-importing the same files never duplicates notes.
  await page.locator('#markdown-files').setInputFiles(files);
  await page.locator('#markdown-import-form button[type="submit"]').click();
  await expect(page.locator('#markdown-import-message')).toContainText('Imported 0 markdown');
  await expect(page.locator('#markdown-import-message')).toContainText('2 skipped');

  // The imported heading became the title and the wikilink renders as a chip.
  await page.locator('[data-view="notes"]').click();
  const card = page.locator('.note').filter({ hasText: title });
  await expect(card).toBeVisible();
  await expect(card.locator('h1')).toHaveText(title);
  await expect(card.locator('.wikilink')).toHaveText(linked);

  // The links panel resolves outgoing links and shows incoming backlinks.
  await card.locator('[data-note-action="links"]').click();
  await expect(card.locator('.note-links')).toContainText('LINKED NOTES');
  await expect(card.locator('.note-links')).toContainText(linked);
  await expect(card.locator('.note-links')).toContainText('LINKED FROM');
  // Match by heading: the study note's body also contains the linked title.
  const backlink = page.locator('.note').filter({ has: page.getByRole('heading', { name: linked, exact: true }) });
  await backlink.locator('[data-note-action="links"]').click();
  await expect(backlink.locator('.note-links')).toContainText(title);
});

test('shares from the note card, previews the public page, then unshares', async ({ page, request, baseURL }) => {
  await signInAsSharedAdmin(page);
  await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
  const body = `share ui check ${Date.now()}`;
  await page.locator('#note-content').fill(body);
  await page.getByRole('button', { name: 'Save note' }).click();

  const card = page.locator('.note').filter({ hasText: body });
  await expect(card).toBeVisible();
  await card.locator('[data-note-action="share"]').click();
  await expect(card.locator('.shared-badge')).toBeVisible();
  await expect(page.locator('#app-message')).toContainText('Share link copied');
  await expect(card.locator('[data-note-action="copy-link"]')).toBeVisible();

  // The preview link serves the read-only markdown page for anyone with the link.
  const href = await card.locator('a[href^="/share/"]').getAttribute('href');
  const publicView = await request.fetch(`${baseURL}${href}`);
  expect(publicView.status()).toBe(200);
  expect(await publicView.text()).toContain(body);
  expect((await request.fetch(`${baseURL}${href}/raw`)).headers()['content-type']).toContain('text/markdown');

  await card.locator('[data-note-action="copy-link"]').click();
  await expect(page.locator('#app-message')).toContainText('Public link copied');

  // Unsharing revokes public access again. The card updates optimistically, so
  // the badge clears before the PATCH is acknowledged — poll the public URL
  // instead of reading its status once, or the assertion races its own write.
  await card.locator('[data-note-action="unshare"]').click();
  await expect(card.locator('.shared-badge')).toHaveCount(0);
  await expect.poll(async () => (await request.fetch(`${baseURL}${href}`)).status(), { timeout: 10_000 }).toBe(404);
});

test('attaches project and document files to a chat and sends them as context', async ({ page }) => {
  await signInAsSharedAdmin(page);
  await page.locator('[data-view="chat"]').click();
  await expect(page.locator('#chat-view')).toBeVisible();

  // Roots come from server configuration; the client can only pick from them.
  await page.locator('#chat-context-toggle').click();
  await expect(page.locator('.context-root')).toHaveCount(3);
  const projectRoot = page.locator('.context-root').filter({ hasText: 'Project directory' });
  await expect(projectRoot).toContainText('READ-ONLY');
  await projectRoot.click();
  await expect(page.locator('#context-path-label')).toHaveText('project');

  // A context file becomes a note in one click.
  await page.locator('.context-entry').filter({ hasText: 'README.md' }).locator('.context-entry-save').click();
  await expect(page.locator('#chat-context-status')).toContainText('Saved README.md as a note');

  // Attach a single file.
  await page.locator('.context-entry').filter({ hasText: 'README.md' }).locator('.context-entry-main').click();
  await expect(page.locator('.context-chip')).toHaveCount(1);
  await expect(page.locator('.context-chip')).toContainText('project:README.md');

  // Attach a whole folder: the picker walks the tree for readable files.
  await page.locator('.context-entry').filter({ hasText: 'nested' }).locator('.context-entry-main').click();
  await expect(page.locator('#context-path-label')).toHaveText('project:nested');
  await page.locator('#context-attach-folder').click();
  await expect(page.locator('.context-chip')).toHaveCount(2);
  await expect(page.locator('.context-chip').nth(1)).toContainText('project:nested/deep-notes.md');

  // A document written into the writable root is attachable too.
  const docName = `checklist-${Date.now()}.md`;
  const written = await page.evaluate(async (name) => {
    const response = await fetch('/api/context/roots/documents/file', {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${localStorage.getItem('planing-token')}` },
      body: JSON.stringify({ path: name, content: '# Release checklist\n\nContext fixture document.\n' }),
    });
    return { status: response.status, body: await response.json() };
  }, docName);
  expect(written.status).toBe(201);
  await page.locator('.context-root').filter({ hasText: 'Documents' }).click();
  await page.locator('.context-entry').filter({ hasText: docName }).locator('.context-entry-main').click();
  await expect(page.locator('.context-chip')).toHaveCount(3);

  // Sending the message ships the file text to the provider as a context block.
  await page.locator('#chat-new').click();
  await page.locator('#chat-input').fill('summarise the attached files');
  await page.locator('#chat-form button[type="submit"]').click();
  const reply = page.locator('.chat-bubble.from-ai').first();
  await expect(reply).toContainText('Mock reply to "summarise the attached files"');
  await expect(reply).toContainText('context:project:README.md,project:nested/deep-notes.md');
  await expect(reply).toContainText(`documents:${docName}`);

  // The session remembers its attachments across reloads.
  await page.reload();
  await page.locator('[data-view="chat"]').click();
  await page.locator('.chat-session-item').first().click();
  await expect(page.locator('.context-chip')).toHaveCount(3);

  // Detaching clears them from the session.
  await page.locator('#chat-context-chips .link-button').click();
  await expect(page.locator('.context-chip')).toHaveCount(0);
  await page.reload();
  await page.locator('[data-view="chat"]').click();
  await page.locator('.chat-session-item').first().click();
  await expect(page.locator('.context-chip')).toHaveCount(0);
});

test('reads PDF text and sends images from the documents root', async ({ page }) => {
  await signInAsSharedAdmin(page);
  await page.locator('[data-view="chat"]').click();
  await page.locator('#chat-context-toggle').click();
  await page.locator('.context-root').filter({ hasText: 'Documents' }).click();

  // Each file type announces what it contributes.
  const pdfEntry = page.locator('.context-entry').filter({ hasText: 'report.pdf' });
  const imageEntry = page.locator('.context-entry').filter({ hasText: 'diagram.png' });
  await expect(pdfEntry.locator('.context-entry-mark')).toHaveClass(/kind-pdf/);
  await expect(imageEntry.locator('.context-entry-mark')).toHaveClass(/kind-image/);
  // Images are never offered as a note: they carry no extractable text.
  await expect(imageEntry.locator('.context-entry-save')).toBeHidden();

  await pdfEntry.locator('.context-entry-main').click();
  await imageEntry.locator('.context-entry-main').click();
  await expect(page.locator('.context-chip')).toHaveCount(2);

  // The PDF travels as extracted text, the image as a multimodal part.
  await page.locator('#chat-new').click();
  await page.locator('#chat-input').fill('what does the attached report say');
  await page.locator('#chat-form button[type="submit"]').click();
  const reply = page.locator('.chat-bubble.from-ai').first();
  await expect(reply).toContainText('context:documents:report.pdf');
  await expect(reply).toContainText('images:1');

  // Extracted PDF text is real text: it becomes a note in one click.
  await pdfEntry.locator('.context-entry-save').click();
  await expect(page.locator('#chat-context-status')).toContainText('Saved report.pdf as a note');
  await page.locator('[data-view="notes"]').click();
  await page.locator('[data-note-view="all"]').click();
  const imported = page.locator('.note').filter({ hasText: 'Retention target is ninety percent' });
  await expect(imported).toBeVisible();
});

test('shows study retention, lapse hotspots, and the review forecast', async ({ page }) => {
  await signInAsSharedAdmin(page);
  const stamp = Date.now();
  const tag = `drill${stamp}`;
  await page.locator('#note-content').fill(`# Recall drill ${stamp}\n\n- Alpha ${stamp} :: first term\n- Beta ${stamp} :: second term\n- Gamma ${stamp} :: third term\n`);
  await page.locator('#note-tags').fill(`#${tag} #recall`);
  await page.getByRole('button', { name: 'Save note' }).click();

  // Cards come from the note, then two cards are graded in the Study view.
  const card = page.locator('.note').filter({ hasText: `Recall drill ${stamp}` });
  await expect(card).toBeVisible();
  await card.locator('[data-note-action="cards"]').click();
  await expect(page.locator('#app-message')).toContainText(/card/i);

  await page.locator('[data-view="study"]').click();
  const first = page.locator('.study-question').first();
  await expect(first).toBeVisible();
  const lapsedQuestion = (await first.textContent())?.trim() || '';
  await page.locator('[data-study-reveal]').click();
  await page.locator('[data-study-grade="again"]').click();
  await page.locator('[data-study-reveal]').click();
  await page.locator('[data-study-grade="good"]').click();

  // Totals, per-tag retention, and the forecast are all populated.
  await expect(page.locator('[data-study-total="studyAnalyticsRetention"] strong')).toContainText('%');
  // The panel refreshes after each grade, so the count is polled rather than
  // read once while the refresh request is still in flight.
  await expect.poll(async () => Number(await page.locator('[data-study-total="studyAnalyticsReviews"] strong').textContent())).toBeGreaterThanOrEqual(2);
  await expect(page.locator('[data-study-total="studyAnalyticsLapses"] strong')).not.toHaveText('0');
  await expect(page.locator('#study-analytics-empty')).toBeHidden();

  const tagRow = page.locator(`[data-study-tag="${tag}"]`);
  await expect(tagRow).toBeVisible();
  await expect(tagRow.locator('.study-tag-value')).toContainText('%');

  // The card graded "again" twice is the top lapse hotspot.
  const hotspot = page.locator('[data-study-hotspot]').first();
  await expect(hotspot).toBeVisible();
  await expect(hotspot).toContainText(lapsedQuestion.slice(0, 12));
  await expect(hotspot.locator('.study-hotspot-meta')).toContainText('lapses');

  await expect(page.locator('[data-study-forecast]')).toHaveCount(7);
  await expect(page.locator('[data-study-activity]')).toHaveCount(14);
});

test('creates a second workspace, switches between them, and scopes context roots', async ({ page }) => {
  await signInAsSharedAdmin(page);
  const stamp = Date.now();
  const workspaceName = `Research lab ${stamp}`;
  const teamNote = `team note ${stamp}`;
  const labNote = `lab note ${stamp}`;

  // A note in the shared workspace, so isolation is observable after switching.
  await page.locator('#note-content').fill(`# ${teamNote}`);
  await page.getByRole('button', { name: 'Save note' }).click();
  await expect(page.locator('.note').filter({ hasText: teamNote })).toBeVisible();
  await expect(page.locator('#workspace-select option')).toHaveCount(1);
  // The shared workspace may already have been renamed by an earlier test, so
  // its id and label are captured rather than assumed.
  const sharedOption = page.locator('#workspace-select option').first();
  const sharedWorkspaceId = await sharedOption.getAttribute('value');
  const sharedWorkspaceLabel = ((await sharedOption.textContent()) || '').split(' · ')[0].trim();

  // Creating a workspace switches to it and swaps the sidebar chrome.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="general"]').click();
  await page.locator('#workspace-new-name').fill(workspaceName);
  await page.locator('#workspace-create-form button[type="submit"]').click();
  await expect(page.locator('#workspace-admin-message')).toContainText('Created');
  await expect(page.locator('#workspace-list [data-workspace-row]')).toHaveCount(2);
  await expect(page.locator('#workspace-title')).toHaveText(workspaceName);

  // The new workspace is empty and has its own lanes.
  await page.locator('[data-view="notes"]').click();
  await page.locator('[data-note-view="all"]').click();
  await expect(page.locator('.note').filter({ hasText: teamNote })).toHaveCount(0);
  await page.locator('#note-content').fill(`# ${labNote}`);
  await page.getByRole('button', { name: 'Save note' }).click();
  await expect(page.locator('.note').filter({ hasText: labNote })).toBeVisible();

  // Context roots are per workspace: the project directory is switched off here.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="ai"]').click();
  const projectToggle = page.locator('#context-root-list .provider-row').filter({ hasText: 'Project directory' }).locator('input[type="checkbox"]');
  await expect(projectToggle).toBeChecked();
  await projectToggle.uncheck();
  await expect(projectToggle).not.toBeChecked();

  // The chat picker only offers what this workspace may read.
  await page.locator('[data-view="chat"]').click();
  await page.locator('#chat-context-toggle').click();
  await expect(page.locator('.context-root')).toHaveCount(2);
  await expect(page.locator('.context-root').filter({ hasText: 'Project directory' })).toHaveCount(0);

  // Switching back restores the shared workspace: its note, and all its roots.
  await page.locator('#workspace-select').selectOption(sharedWorkspaceId);
  await expect(page.locator('#workspace-title')).toHaveText(sharedWorkspaceLabel);
  await page.locator('[data-view="notes"]').click();
  await page.locator('[data-note-view="all"]').click();
  await expect(page.locator('.note').filter({ hasText: teamNote })).toBeVisible();
  await expect(page.locator('.note').filter({ hasText: labNote })).toHaveCount(0);
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="ai"]').click();
  await expect(page.locator('#context-root-list .provider-row').filter({ hasText: 'Project directory' }).locator('input[type="checkbox"]')).toBeChecked();

  // The switch survives a reload, and the lab workspace still has its own state.
  await page.reload();
  await expect(page.locator('#workspace-title')).toHaveText(sharedWorkspaceLabel);
  await expect(page.locator('#workspace-select option')).toHaveCount(2);
});

test('manages the prompt library from settings and uses it in the chat', async ({ page }) => {
  await signInAsSharedAdmin(page);
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="ai"]').click();

  // Built-in prompts are read-only: they offer Duplicate, never Edit or Delete.
  const builtIn = page.locator('#prompt-list .provider-row').filter({ hasText: 'BUILT-IN' }).first();
  await expect(builtIn).toBeVisible();
  await expect(builtIn.locator('[data-i18n="edit"]')).toBeHidden();
  await expect(builtIn.locator('[data-i18n="providerDelete"]')).toBeHidden();

  // Duplicating seeds the form with a fresh identifier.
  await builtIn.locator('[data-i18n="promptDuplicate"]').click();
  await expect(page.locator('#prompt-id')).toHaveValue(/-copy$/);
  await page.locator('#prompt-title').fill('Compliance review');
  await page.locator('#prompt-body').fill('Review the attached files and list every risk with a citation.');
  await page.locator('#prompt-save').click();
  await expect(page.locator('#prompt-message')).toContainText('Prompt saved');
  const row = page.locator('#prompt-list .provider-row').filter({ hasText: 'Compliance review' });
  await expect(row).toBeVisible();

  // Editing a custom prompt updates it in place.
  await row.locator('[data-i18n="edit"]').click();
  await page.locator('#prompt-title').fill('Compliance review v2');
  await page.locator('#prompt-save').click();
  const edited = page.locator('#prompt-list .provider-row').filter({ hasText: 'Compliance review v2' });
  await expect(edited).toBeVisible();

  // The prompt is selectable in the chat toolbar.
  await page.locator('[data-view="chat"]').click();
  await expect(page.locator('#chat-prompt option').filter({ hasText: 'Compliance review v2' })).toHaveCount(1);

  // Deleting removes the custom prompt only.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="ai"]').click();
  page.on('dialog', (dialog) => dialog.accept());
  await page.locator('#prompt-list .provider-row').filter({ hasText: 'Compliance review v2' }).locator('[data-i18n="providerDelete"]').click();
  await expect(page.locator('#prompt-list .provider-row').filter({ hasText: 'Compliance review v2' })).toHaveCount(0);
  await expect(page.locator('#prompt-list .provider-row').filter({ hasText: 'BUILT-IN' }).first()).toBeVisible();
});

test('invites per workspace with owner and commenter roles', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();
  // The workspace this session starts in, captured before anything is created:
  // membership order is not stable, so "the other workspace" is named, not
  // guessed from the option order.
  const startingId = await page.locator('#workspace-select').inputValue();
  const startingLabel = ((await page.locator(`#workspace-select option[value="${startingId}"]`).textContent()) || '').split(' · ')[0].trim();

  // The role vocabulary grew: owner and commenter are offered, and the People
  // tab says which workspace you are looking at and what you are in it.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="people"]').click();
  await expect(page.locator('#role-reference')).toContainText('Owner');
  await expect(page.locator('#role-reference')).toContainText('Commenter');
  await expect(page.locator('#join-panel')).toBeVisible();
  const grantable = await page.locator('#invite-role option').evaluateAll((nodes) => nodes.filter((node) => !node.disabled && !node.hidden).map((node) => node.value));
  expect(grantable).toEqual(expect.arrayContaining(['owner', 'admin', 'editor', 'commenter', 'viewer']));
  await expect(page.locator('#people-scope')).toContainText(startingLabel);

  // A workspace created here is owned by its creator.
  await page.locator('[data-settings-tab="general"]').click();
  await page.locator('#workspace-new-name').fill(`Roles lab ${stamp}`);
  await page.locator('#workspace-create-form button[type="submit"]').click();
  await expect(page.locator('#workspace-admin-message')).toContainText('Created');
  // The switcher repopulates asynchronously once the create round-trip settles.
  await expect(page.locator('#workspace-select option').filter({ hasText: `Roles lab ${stamp}` })).toHaveCount(1);
  const options = await page.locator('#workspace-select option').evaluateAll((nodes) => nodes.map((node) => ({ id: node.value, label: node.textContent || '' })));
  const lab = options.find((option) => option.label.startsWith(`Roles lab ${stamp}`));
  expect(lab).toBeTruthy();
  const shared = options.find((option) => option.id === startingId);
  expect(shared).toBeTruthy();
  await expect(page.locator('#people-scope')).toContainText('Owner');

  // Two codes for the lab: one claimed by a new commenter, one left open.
  const inviteA = await (await api('/api/invitations', { method: 'POST', headers: auth, data: JSON.stringify({ role: 'commenter' }) })).json();
  const inviteB = await (await api('/api/invitations', { method: 'POST', headers: auth, data: JSON.stringify({ role: 'viewer' }) })).json();
  expect(inviteA.role).toBe('commenter');
  expect(new Date(inviteB.expiresAt).getTime()).toBeGreaterThan(Date.now());
  await page.locator('[data-settings-tab="people"]').click();
  await expect(page.locator('#invitations-list')).toContainText(inviteB.code);
  await expect(page.locator('#invitations-list')).toContainText('Invited by');

  // A new account redeeming the code becomes a commenter of the lab only.
  const teammate = { name: `commenter-${stamp}`, password: 'local-test-password-123' };
  const signup = await api('/api/auth/register', { method: 'POST', data: JSON.stringify({ ...teammate, invite: inviteA.code }) });
  expect(signup.status()).toBe(201);
  const teammateAuth = { authorization: `Bearer ${(await signup.json()).token}` };
  const teammateProfile = await (await api('/api/auth/profile', { headers: teammateAuth })).json();
  expect(teammateProfile.user.role).toBe('commenter');
  expect(teammateProfile.workspaceId).toBe(lab.id);
  const teammateWorkspaces = await (await api('/api/workspaces', { headers: teammateAuth })).json();
  expect(teammateWorkspaces.workspaces.map((workspace) => workspace.id)).toEqual([lab.id]);

  // Commenters read and reply, but do not write notes or manage people.
  expect((await api('/api/notes', { headers: teammateAuth })).status()).toBe(200);
  expect((await api('/api/notes', { method: 'POST', headers: teammateAuth, data: JSON.stringify({ content: 'commenter write attempt', category: 'notes' }) })).status()).toBe(403);
  expect((await api('/api/members', { headers: teammateAuth })).status()).toBe(403);
  expect((await api('/api/invitations', { headers: teammateAuth })).status()).toBe(403);

  // Switching workspace switches the People tab: the lab's open code is not
  // listed here, and it cannot be revoked from the wrong workspace.
  await page.locator('[data-settings-tab="general"]').click();
  await page.locator('#workspace-select').selectOption(shared.id);
  await page.locator('[data-settings-tab="people"]').click();
  await expect(page.locator('#invitations-list')).not.toContainText(inviteB.code);
  await expect(page.locator('#people-scope')).toContainText(startingLabel);
  expect((await api(`/api/invitations/${encodeURIComponent(inviteB.code)}`, { method: 'DELETE', headers: auth })).status()).toBe(404);

  // An existing account joins a second workspace with a code from this one. The
  // code is scoped to the workspace that issued it, and redeeming switches the
  // joiner there — where their role is the one the code carried.
  const inviteC = await (await api('/api/invitations', { method: 'POST', headers: auth, data: JSON.stringify({ role: 'viewer' }) })).json();
  const joined = await api('/api/invitations/redeem', { method: 'POST', headers: teammateAuth, data: JSON.stringify({ code: inviteC.code }) });
  expect(joined.status()).toBe(200);
  expect((await joined.json()).role).toBe('viewer');
  const afterJoin = await (await api('/api/workspaces', { headers: teammateAuth })).json();
  expect(afterJoin.workspaces.map((workspace) => workspace.id).sort()).toEqual([lab.id, shared.id].sort());
  const teammateAfterJoin = await (await api('/api/auth/profile', { headers: teammateAuth })).json();
  expect(teammateAfterJoin.workspaceId).toBe(shared.id);
  expect(teammateAfterJoin.user.role).toBe('viewer');
  // A claimed code is spent, and a signed-up account cannot re-register with it.
  expect((await api('/api/invitations/redeem', { method: 'POST', headers: teammateAuth, data: JSON.stringify({ code: inviteC.code }) })).status()).toBe(403);
  expect((await api('/api/auth/register', { method: 'POST', data: JSON.stringify({ name: `late-${stamp}`, password: 'local-test-password-123', invite: inviteC.code }) })).status()).toBe(403);

  // Back in the lab the pending code is still there, and the People tab shows
  // the teammate with the membership role rather than a global one.
  await page.locator('[data-settings-tab="general"]').click();
  await page.locator('#workspace-select').selectOption(lab.id);
  await page.locator('[data-settings-tab="people"]').click();
  await expect(page.locator('#invitations-list')).toContainText(inviteB.code);
  const teammateRow = page.locator('.member-row').filter({ hasText: teammate.name });
  await expect(teammateRow.locator('.member-role')).toHaveValue('commenter');
  await expect(page.locator('.member-row').filter({ has: page.locator('.owner-badge') })).toHaveCount(1);

  // Promoting the commenter to editor through the row select grants note writes
  // in this workspace only — the same account is still a viewer in the other.
  await teammateRow.locator('.member-role').selectOption('editor');
  await expect(page.locator('#member-message')).toContainText('Role updated');
  expect((await api('/api/notes', { method: 'POST', headers: teammateAuth, data: JSON.stringify({ content: `editor write ${stamp}`, category: 'notes' }) })).status()).toBe(403);
  await api(`/api/workspaces/${encodeURIComponent(lab.id)}/active`, { method: 'POST', headers: teammateAuth, data: JSON.stringify({}) });
  const teammateHere = await (await api('/api/auth/profile', { headers: teammateAuth })).json();
  expect(teammateHere.workspaceId).toBe(lab.id);
  expect(teammateHere.user.role).toBe('editor');
  expect((await api('/api/notes', { method: 'POST', headers: teammateAuth, data: JSON.stringify({ content: `editor write ${stamp}`, category: 'notes' }) })).status()).toBe(201);

  // An admin cannot grant ownership, nor demote the only owner of a workspace.
  const adminName = `admin-role-${stamp}`;
  expect((await api('/api/members', { method: 'POST', headers: auth, data: JSON.stringify({ name: adminName, password: 'local-test-password-123', role: 'admin' }) })).status()).toBe(201);
  const adminB = await (await api('/api/auth/login', { method: 'POST', data: JSON.stringify({ name: adminName, password: 'local-test-password-123' }) })).json();
  const adminBAuth = { authorization: `Bearer ${adminB.token}` };
  expect((await api('/api/invitations', { method: 'POST', headers: adminBAuth, data: JSON.stringify({ role: 'owner' }) })).status()).toBe(403);
  const members = await (await api('/api/members', { headers: auth })).json();
  const ownerRow = members.find((member) => member.role === 'owner');
  expect(ownerRow).toBeTruthy();
  const demote = await api(`/api/members/${encodeURIComponent(ownerRow.id)}`, { method: 'PATCH', headers: adminBAuth, data: JSON.stringify({ role: 'viewer' }) });
  expect(demote.status()).toBe(400);
  expect((await demote.json()).error).toContain('owner');
  // An owner may hand out ownership, which is the only way to share it.
  expect((await api('/api/invitations', { method: 'POST', headers: auth, data: JSON.stringify({ role: 'owner' }) })).status()).toBe(201);

  // Revoking works inside the owning workspace, and removes the row.
  await page.locator('[data-revoke-invite="' + inviteB.code + '"]').click();
  await expect(page.locator('#invite-message')).toContainText('revoked');
  await expect(page.locator('#invitations-list')).not.toContainText(inviteB.code);
});

test('threads note comments inside their workspace and honours comment roles', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();
  const password = 'local-test-password-123';
  const home = await (await api('/api/workspaces', { headers: auth })).json();
  const homeId = home.activeId;

  // A note in the workspace this session is in, with an empty thread.
  const note = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Thread target ${stamp}\n\nComment me.`, category: 'notes' }) })).json();
  const emptyThread = await (await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { headers: auth })).json();
  expect(emptyThread.comments).toEqual([]);
  expect(emptyThread.canComment).toBe(true);

  // A viewer reads the thread but cannot reply; a commenter can.
  const viewerName = `viewer-c-${stamp}`;
  expect((await api('/api/members', { method: 'POST', headers: auth, data: JSON.stringify({ name: viewerName, password, role: 'viewer' }) })).status()).toBe(201);
  const viewer = await (await api('/api/auth/login', { method: 'POST', data: JSON.stringify({ name: viewerName, password }) })).json();
  const viewerAuth = { authorization: `Bearer ${viewer.token}` };
  const viewerThread = await (await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { headers: viewerAuth })).json();
  expect(viewerThread.canComment).toBe(false);
  expect((await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { method: 'POST', headers: viewerAuth, data: JSON.stringify({ body: 'viewer reply' }) })).status()).toBe(403);

  const commenterName = `commenter-c-${stamp}`;
  expect((await api('/api/members', { method: 'POST', headers: auth, data: JSON.stringify({ name: commenterName, password, role: 'commenter' }) })).status()).toBe(201);
  const commenter = await (await api('/api/auth/login', { method: 'POST', data: JSON.stringify({ name: commenterName, password }) })).json();
  const commenterAuth = { authorization: `Bearer ${commenter.token}` };
  const created = await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { method: 'POST', headers: commenterAuth, data: JSON.stringify({ body: 'Can we cite the source?' }) });
  expect(created.status()).toBe(201);
  const comment = await created.json();
  expect(comment.authorName).toBe(commenterName);
  expect(comment.isOwn).toBe(true);
  expect(comment.canEdit).toBe(true);
  expect((await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { method: 'POST', headers: commenterAuth, data: JSON.stringify({ body: '   ' }) })).status()).toBe(400);

  // The author edits their own comment; nobody else may.
  const edited = await api(`/api/comments/${encodeURIComponent(comment.id)}`, { method: 'PATCH', headers: commenterAuth, data: JSON.stringify({ body: 'Cite the source, please.' }) });
  expect(edited.status()).toBe(200);
  expect((await edited.json()).edited).toBe(true);
  expect((await api(`/api/comments/${encodeURIComponent(comment.id)}`, { method: 'PATCH', headers: auth, data: JSON.stringify({ body: 'owner edit' }) })).status()).toBe(403);

  // A member who manages people moderates the thread; a peer without that
  // permission cannot remove someone else's reply.
  const ownerComment = await (await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { method: 'POST', headers: auth, data: JSON.stringify({ body: 'Opening the source wiki now.' }) })).json();
  expect((await api(`/api/comments/${encodeURIComponent(ownerComment.id)}`, { method: 'DELETE', headers: commenterAuth })).status()).toBe(403);
  expect((await api(`/api/comments/${encodeURIComponent(ownerComment.id)}`, { method: 'DELETE', headers: auth })).status()).toBe(204);
  const afterModeration = await (await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { headers: auth })).json();
  const removedComment = afterModeration.comments.find((row) => row.id === ownerComment.id);
  expect(removedComment.isDeleted).toBe(true);
  expect(removedComment.body).toBe('');
  expect(afterModeration.count).toBe(1);

  // Threads are per workspace: from another workspace the note is not there and
  // the comment id resolves to nothing, so neither can be read or changed.
  await api('/api/workspaces', { method: 'POST', headers: auth, data: JSON.stringify({ name: `Comments lab ${stamp}` }) });
  expect((await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { headers: auth })).status()).toBe(404);
  expect((await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { method: 'POST', headers: auth, data: JSON.stringify({ body: 'wrong workspace' }) })).status()).toBe(404);
  expect((await api(`/api/comments/${encodeURIComponent(comment.id)}`, { method: 'PATCH', headers: auth, data: JSON.stringify({ body: 'wrong workspace' }) })).status()).toBe(404);
  expect((await api(`/api/comments/${encodeURIComponent(comment.id)}`, { method: 'DELETE', headers: auth })).status()).toBe(404);
  await api(`/api/workspaces/${encodeURIComponent(homeId)}/active`, { method: 'POST', headers: auth, data: JSON.stringify({}) });
  const restored = await (await api(`/api/notes/${encodeURIComponent(note.id)}/comments`, { headers: auth })).json();
  expect(restored.comments.length).toBe(2);
  expect(restored.comments[0].body).toContain('Cite the source');
  expect((await (await api('/api/audit', { headers: auth })).json()).some((event) => event.action === 'comment.create')).toBe(true);

  // The thread is usable from the note card: read it, reply, and see it land.
  await page.locator('[data-view="notes"]').click();
  await page.locator('#note-search').fill(`Thread target ${stamp}`);
  const card = page.locator('.note').filter({ hasText: `Thread target ${stamp}` });
  await expect(card).toBeVisible();
  await card.locator('[data-note-action="comments"]').click();
  const panel = card.locator('.note-comments');
  await expect(panel).toContainText('Cite the source');
  await expect(panel).toContainText(commenterName);
  await expect(panel.locator('.comment-removed')).toContainText('Comment deleted');
  await panel.locator('.comment-form textarea').fill(`ui reply ${stamp}`);
  await panel.locator('.comment-form button[type="submit"]').click();
  await expect(page.locator('#app-message')).toContainText('Comment added');
  await expect(panel).toContainText(`ui reply ${stamp}`);
  // The author can edit through the thread, which re-renders in place.
  const uiComment = panel.locator('.comment').filter({ hasText: `ui reply ${stamp}` });
  await uiComment.locator('[data-comment-edit]').click();
  await uiComment.locator('.comment-edit').fill(`ui reply edited ${stamp}`);
  await uiComment.locator('[data-comment-save]').click();
  await expect(panel).toContainText(`ui reply edited ${stamp}`);
});

test('moves a whole workspace between deployments through a bundle', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();
  const source = await (await api('/api/workspaces', { headers: auth })).json();
  const sourceId = source.activeId;
  const sourceName = source.workspaces.find((workspace) => workspace.id === sourceId).name;

  // A workspace worth moving: a lane, a linked pair of notes, a comment thread,
  // and a study card. The target is written first so the wiki link resolves.
  const lane = await (await api('/api/categories', { method: 'POST', headers: auth, data: JSON.stringify({ name: `Bundle lane ${stamp}`, color: '#0f766e' }) })).json();
  const target = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Bundle target ${stamp}\n\nSecond note.`, category: lane.slug }) })).json();
  const seed = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Bundle source ${stamp}\n\nSee [[Bundle target ${stamp}]].\n\n- Recall ${stamp} :: the answer to recall`, category: lane.slug, tags: [`bundle${stamp}`] }) })).json();
  expect((await api(`/api/notes/${encodeURIComponent(seed.id)}/comments`, { method: 'POST', headers: auth, data: JSON.stringify({ body: `moved comment ${stamp}` }) })).status()).toBe(201);
  const cards = await (await api('/api/study/generate', { method: 'POST', headers: auth, data: JSON.stringify({ noteId: seed.id, mode: 'auto' }) })).json();
  expect(cards.created).toBeGreaterThanOrEqual(1);

  // The bundle carries the workspace, its content, and its structure.
  const bundleResponse = await api(`/api/workspaces/${encodeURIComponent(sourceId)}/bundle`, { headers: auth });
  expect(bundleResponse.status()).toBe(200);
  expect(bundleResponse.headers()['content-disposition']).toContain('-bundle.json');
  const bundle = await bundleResponse.json();
  expect(bundle.bundleVersion).toBe(1);
  expect(bundle.workspace.name).toBe(sourceName);
  expect(bundle.categories.some((entry) => entry.slug === lane.slug)).toBe(true);
  expect(bundle.notes.some((entry) => entry.id === seed.id)).toBe(true);
  expect(bundle.comments.some((entry) => entry.note === seed.id)).toBe(true);
  expect(bundle.study.some((entry) => entry.note === seed.id)).toBe(true);

  // Importing lands as a new workspace and switches to it. The source notes
  // still exist here, so every taken id is remapped instead of overwritten.
  const importedResponse = await api('/api/workspaces/import', { method: 'POST', headers: auth, data: JSON.stringify(bundle) });
  expect(importedResponse.status()).toBe(201);
  const imported = await importedResponse.json();
  expect(imported.imported.notes).toBe(bundle.notes.length);
  expect(imported.imported.remapped).toBeGreaterThan(0);
  expect(imported.workspace.name.startsWith(sourceName)).toBe(true);
  expect(imported.workspace.name).not.toBe(sourceName);
  const afterImport = await (await api('/api/workspaces', { headers: auth })).json();
  expect(afterImport.activeId).toBe(imported.workspace.id);
  expect(afterImport.workspaces.length).toBe(source.workspaces.length + 1);

  // Lanes, notes, tags, links, cards, and comments all arrived with the copy,
  // and the remapped note kept its own thread and card pointing at it.
  const restoredNotes = await (await api('/api/notes', { headers: auth })).json();
  // Match on the heading, not the body: the seed mentions the target's title in
  // its wiki link, so a `content.includes` lookup would match the wrong note.
  const titleOf = (content) => String(content).split('\n').map((line) => line.trim()).find((line) => line.length > 0)?.replace(/^#+\s*/, '').trim() || '';
  const restoredSeed = restoredNotes.find((note) => titleOf(note.content) === `Bundle source ${stamp}`);
  const restoredTarget = restoredNotes.find((note) => titleOf(note.content) === `Bundle target ${stamp}`);
  expect(restoredSeed).toBeTruthy();
  expect(restoredTarget).toBeTruthy();
  expect(restoredSeed.id).not.toBe(seed.id);
  expect(restoredSeed.tags.some((tag) => tag.name === `bundle${stamp}`)).toBe(true);
  expect(restoredSeed.category.slug).toBe(lane.slug);
  const restoredLanes = await (await api('/api/categories', { headers: auth })).json();
  expect(restoredLanes.some((entry) => entry.slug === lane.slug && entry.color === '#0f766e')).toBe(true);
  const restoredLinks = await (await api(`/api/notes/${encodeURIComponent(restoredSeed.id)}/backlinks`, { headers: auth })).json();
  expect(restoredLinks.links.some((link) => link.note && link.note.id === restoredTarget.id)).toBe(true);
  const restoredThread = await (await api(`/api/notes/${encodeURIComponent(restoredSeed.id)}/comments`, { headers: auth })).json();
  expect(restoredThread.comments.map((comment) => comment.body)).toContain(`moved comment ${stamp}`);
  const restoredStudy = await (await api('/api/study/items', { headers: auth })).json();
  expect(restoredStudy.some((item) => item.note === restoredSeed.id)).toBe(true);

  // The source workspace is untouched: it still owns its own copy.
  await api(`/api/workspaces/${encodeURIComponent(sourceId)}/active`, { method: 'POST', headers: auth, data: JSON.stringify({}) });
  const sourceNotes = await (await api('/api/notes', { headers: auth })).json();
  expect(sourceNotes.filter((note) => note.id === seed.id).length).toBe(1);
  expect((await api(`/api/notes/${encodeURIComponent(seed.id)}/comments`, { headers: auth })).status()).toBe(200);

  // Importing the same bundle again makes a second independent workspace, and
  // every record whose id was taken is remapped rather than overwritten.
  const againResponse = await api('/api/workspaces/import', { method: 'POST', headers: auth, data: JSON.stringify(bundle) });
  expect(againResponse.status()).toBe(201);
  const again = await againResponse.json();
  expect(again.workspace.id).not.toBe(imported.workspace.id);
  expect(again.imported.remapped).toBeGreaterThan(0);
  const movedNotes = await (await api('/api/notes', { headers: auth })).json();
  expect(movedNotes.some((note) => note.id !== seed.id && titleOf(note.content) === `Bundle source ${stamp}`)).toBe(true);

  // A bundle whose ids nobody here has used keeps them, which is what keeps
  // wiki links and share links stable when a workspace moves to a fresh
  // deployment.
  const foreignId = `foreign${stamp}`;
  const foreign = {
    bundleVersion: 1,
    workspace: { name: `Foreign workspace ${stamp}`, description: 'Arrived from another deployment.', theme: 'system' },
    categories: [{ slug: 'notes', name: 'Notes', isSystem: true, isDefault: true }],
    notes: [{ id: foreignId, content: `# Foreign note ${stamp}\n\nMoved in whole.`, tags: [], metadata: {} }],
  };
  const foreignResponse = await api('/api/workspaces/import', { method: 'POST', headers: auth, data: JSON.stringify(foreign) });
  expect(foreignResponse.status()).toBe(201);
  const foreignResult = await foreignResponse.json();
  expect(foreignResult.imported.notes).toBe(1);
  expect(foreignResult.imported.remapped).toBe(0);
  const foreignNotes = await (await api('/api/notes', { headers: auth })).json();
  expect(foreignNotes.some((note) => note.id === foreignId)).toBe(true);

  // Anything that is not a bundle is refused before a workspace is created.
  const beforeInvalid = (await (await api('/api/workspaces', { headers: auth })).json()).workspaces.length;
  expect((await api('/api/workspaces/import', { method: 'POST', headers: auth, data: JSON.stringify({ hello: 'world' }) })).status()).toBe(400);
  expect((await api('/api/workspaces/import', { method: 'POST', headers: auth, data: JSON.stringify({ ...bundle, bundleVersion: 99 }) })).status()).toBe(400);
  expect((await (await api('/api/workspaces', { headers: auth })).json()).workspaces.length).toBe(beforeInvalid);

  // The Data tab drives both halves of the move.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="data"]').click();
  await expect(page.locator('#bundle-export')).toBeVisible();
  const download = page.waitForEvent('download');
  await page.locator('#bundle-export').click();
  expect((await download).suggestedFilename()).toContain('-bundle.json');
  await expect(page.locator('#bundle-message')).toContainText('Bundle exported');
  await page.locator('#bundle-import').click();
  await expect(page.locator('#bundle-message')).toContainText('Choose a bundle file');
});

test('scopes the AI policy to the workspace and records every provider run', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();

  // A second provider so the allow-list has something to exclude.
  await api('/api/providers', { method: 'POST', headers: auth, data: JSON.stringify({ name: `spare-${stamp}`, baseUrl: 'http://127.0.0.1:11434/v1', model: 'mock-model', apiKey: 'k', activate: false }) });
  await api('/api/providers', { method: 'POST', headers: auth, data: JSON.stringify({ name: 'mock-llm', baseUrl: 'http://127.0.0.1:11434/v1', model: 'mock-model', apiKey: 'mock-key-123', activate: true }) });

  // Default policy: empty allow-list, no cap, everything allowed.
  const initial = await (await api('/api/ai/policy', { headers: auth })).json();
  expect(initial.allowedProviders).toEqual([]);
  expect(initial.providers.every((provider) => provider.allowed)).toBe(true);

  // Restrict to the active provider and set it as default.
  const patched = await api('/api/ai/policy', { method: 'PATCH', headers: auth, data: JSON.stringify({ allowedProviders: ['mock-llm'], defaultProvider: 'mock-llm', runCap: 500 }) });
  expect(patched.status()).toBe(200);
  const restricted = await patched.json();
  expect(restricted.allowedProviders).toEqual(['mock-llm']);
  expect(restricted.defaultProvider).toBe('mock-llm');
  expect(restricted.runCap).toBe(500);
  expect(restricted.providers.find((provider) => provider.id === 'spare-' + stamp)?.allowed).toBe(false);
  expect(restricted.providers.find((provider) => provider.id === 'mock-llm')?.allowed).toBe(true);

  // An unknown default is refused; the cap must be a sane number.
  expect((await api('/api/ai/policy', { method: 'PATCH', headers: auth, data: JSON.stringify({ defaultProvider: 'nope' }) })).status()).toBe(400);
  expect((await api('/api/ai/policy', { method: 'PATCH', headers: auth, data: JSON.stringify({ runCap: 0 }) })).status()).toBe(400);

  // A chat over the allowed provider lands in the run ledger.
  const session = await (await api('/api/chat/sessions', { method: 'POST', headers: auth, data: JSON.stringify({}) })).json();
  const message = await api(`/api/chat/sessions/${encodeURIComponent(session.id)}/messages`, { method: 'POST', headers: auth, data: JSON.stringify({ content: `policy run ${stamp}` }) });
  expect(message.status()).toBe(201);
  const runs = await (await api('/api/ai/runs', { headers: auth })).json();
  const run = runs.find((entry) => entry.feature === 'chat' && entry.status === 'ok');
  expect(run).toBeTruthy();
  expect(run.model).toBe('mock-model');
  expect(run.durationMs).toBeGreaterThanOrEqual(0);
  expect(run.responseChars).toBeGreaterThan(0);
  expect(run.accountName).toBe(admin.name);

  // Study generation calls the provider through the same policy path (the echo
  // mock cannot produce JSON flashcards, so parsing falls back to offline — the
  // run row is still recorded from the successful provider round-trip).
  const note = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Policy study ${stamp}\n\n- What is SurrealDB? :: A multi-model database`, category: 'notes' }) })).json();
  await api('/api/study/generate', { method: 'POST', headers: auth, data: JSON.stringify({ noteId: note.id, mode: 'auto' }) });
  const runsAfter = await (await api('/api/ai/runs', { headers: auth })).json();
  expect(runsAfter.some((entry) => entry.feature === 'study.generate' && entry.status === 'ok')).toBe(true);

  // The Settings → AI panels render the policy and the ledger.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="ai"]').click();
  await expect(page.locator('#ai-policy-panel')).toBeVisible();
  await expect(page.locator('#ai-runs-panel .provider-row').first()).toBeVisible();
  await expect(page.locator('#ai-policy-panel .provider-row').filter({ hasText: 'mock-llm' }).locator('input[type="checkbox"]')).toBeChecked();

  // Back to open policy so later tests are unaffected.
  await api('/api/ai/policy', { method: 'PATCH', headers: auth, data: JSON.stringify({ allowedProviders: [], defaultProvider: null, runCap: null }) });
});

test('records per-note activity history and rejects it outside the workspace', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();

  const note = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# History ${stamp}\n\nOriginal body.`, category: 'notes', tags: ['history'] }) })).json();
  expect(note.id).toBeTruthy();

  // Mutate it a few times; each one should land in the timeline.
  await api(`/api/notes/${encodeURIComponent(note.id)}`, { method: 'PATCH', headers: auth, data: JSON.stringify({ content: `# History ${stamp}\n\nEdited body.` }) });
  await api(`/api/notes/${encodeURIComponent(note.id)}`, { method: 'PATCH', headers: auth, data: JSON.stringify({ isTop: true }) });
  const activity = await (await api(`/api/notes/${encodeURIComponent(note.id)}/activity`, { headers: auth })).json();
  expect(activity.length).toBeGreaterThanOrEqual(3);
  expect(activity[0].action).toBe('note.updated'); // newest first
  expect(activity.map((entry) => entry.action)).toContain('note.created');
  expect(activity.every((entry) => entry.createdAt)).toBe(true);

  // The viewer gets the timeline through the UI pane on the note card.
  await page.locator('#note-search').fill(`History ${stamp}`);
  await page.locator('#note-search').dispatchEvent('input');
  await expect(page.locator('.note', { hasText: `History ${stamp}` })).toBeVisible();
  await page.locator('.note', { hasText: `History ${stamp}` }).locator('[data-note-action="history"]').click();
  await expect(page.locator('.note', { hasText: `History ${stamp}` }).locator('.history-entry').first()).toBeVisible();

  // A note id from nowhere resolves to nothing, like any other scoped read.
  expect((await api('/api/notes/no-such-note/activity', { headers: auth })).status()).toBe(404);
});

test('throttles failed logins and records security events', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };

  // Failed logins from the test runner's IP pile into the same fixed window.
  const attempts = Array.from({ length: 3 }, (_, index) => api('/api/auth/login', { method: 'POST', data: JSON.stringify({ name: `ghost-${index}`, password: 'wrong-password' }) }));
  const responses = await Promise.all(attempts);
  expect(responses.every((response) => response.status() === 401)).toBe(true);

  // Security events capture the failures with the request context.
  const events = await (await api('/api/security/events?limit=100', { headers: auth })).json();
  expect(events.some((event) => event.kind === 'login.failed')).toBe(true);
  expect(events.some((event) => event.kind === 'login.success')).toBe(true);
  expect(events[0].createdAt).toBeTruthy();
  // Failures carry the IP; successes are recorded but the limit only counts hits.
  const failed = events.find((event) => event.kind === 'login.failed');
  expect(failed.detail.reason).toBe('unknown-user');

  // The Activity tab lists them beside the audit stream.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="activity"]').click();
  await expect(page.locator('#security-list .audit-row').first()).toBeVisible();

  // Forged tokens are throttled too and produce their own event kind.
  await request.fetch(`${baseURL}/api/notes`, { headers: { authorization: 'Bearer not-a-jwt' } });
  const after = await (await api('/api/security/events?limit=100', { headers: auth })).json();
  expect(after.some((event) => event.kind === 'token.invalid')).toBe(true);
});

// Poll until the predicate holds; the job worker ticks every 5s.
async function waitFor(predicate, timeout = 20_000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) {
    const value = await predicate();
    if (value) return value;
    await new Promise((resolve) => setTimeout(resolve, 1_000));
  }
  return null;
}

test('enforces the hourly AI run cap on chat and study generation', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();

  // The mock provider is instance-wide; make sure it is active for this run.
  await api('/api/providers', { method: 'POST', headers: auth, data: JSON.stringify({ name: 'mock-llm', baseUrl: 'http://127.0.0.1:11434/v1', model: 'mock-model', apiKey: 'mock-key-123', activate: true }) });

  // A fresh workspace starts with an empty run ledger, so the cap is exact.
  const created = await (await api('/api/workspaces', { method: 'POST', headers: auth, data: JSON.stringify({ name: `Capped ${stamp}` }) })).json();
  const cappedId = created.workspace?.id || created.id;
  expect(cappedId).toBeTruthy();

  // Cap = 1 provider call this hour.
  await api('/api/ai/policy', { method: 'PATCH', headers: auth, data: JSON.stringify({ runCap: 1 }) });
  const policy = await (await api('/api/ai/policy', { headers: auth })).json();
  expect(policy.runCap).toBe(1);
  expect(policy.cap.used).toBe(0);
  expect(policy.cap.remaining).toBe(1);

  // First chat passes and consumes the budget.
  const session = await (await api('/api/chat/sessions', { method: 'POST', headers: auth, data: JSON.stringify({}) })).json();
  const first = await api(`/api/chat/sessions/${encodeURIComponent(session.id)}/messages`, { method: 'POST', headers: auth, data: JSON.stringify({ content: `cap probe ${stamp}` }) });
  expect(first.status()).toBe(201);

  // The policy endpoint now reports the budget as spent.
  const spent = await (await api('/api/ai/policy', { headers: auth })).json();
  expect(spent.cap.used).toBe(1);
  expect(spent.cap.limited).toBe(true);

  // Second chat is refused with 429 before any provider call.
  const second = await api(`/api/chat/sessions/${encodeURIComponent(session.id)}/messages`, { method: 'POST', headers: auth, data: JSON.stringify({ content: 'should be refused' }) });
  expect(second.status()).toBe(429);
  const refusal = await second.json();
  expect(refusal.error).toContain('AI run cap');

  // Study generation is refused too; offline mode still works.
  const note = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Capped note ${stamp}\n\n- Q :: A`, category: 'notes' }) })).json();
  const blockedGenerate = await api('/api/study/generate', { method: 'POST', headers: auth, data: JSON.stringify({ noteId: note.id, mode: 'auto' }) });
  expect(blockedGenerate.status()).toBe(429);
  const offline = await (await api('/api/study/generate', { method: 'POST', headers: auth, data: JSON.stringify({ noteId: note.id, mode: 'offline' }) })).json();
  expect(offline.generatedBy).toBe('offline');
  expect(offline.created).toBeGreaterThanOrEqual(1);

  // Queued jobs respect the cap at enqueue time.
  const blockedJob = await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'study.generate', noteId: note.id }) });
  expect(blockedJob.status()).toBe(429);

  // Raising the cap immediately unblocks the workspace.
  await api('/api/ai/policy', { method: 'PATCH', headers: auth, data: JSON.stringify({ runCap: 10 }) });
  expect((await api(`/api/chat/sessions/${encodeURIComponent(session.id)}/messages`, { method: 'POST', headers: auth, data: JSON.stringify({ content: 'unblocked now' }) })).status()).toBe(201);

  // Cleanup: remove the cap so later tests are unaffected.
  await api('/api/ai/policy', { method: 'PATCH', headers: auth, data: JSON.stringify({ runCap: null }) });
});

test('records token usage and estimated cost per provider run', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();

  // An unpriced model records zero cost; a priced one (gpt-4o-mini) is costed.
  await api('/api/providers', { method: 'POST', headers: auth, data: JSON.stringify({ name: 'priced-llm', baseUrl: 'http://127.0.0.1:11434/v1', model: 'gpt-4o-mini', apiKey: 'k', activate: true }) });

  const session = await (await api('/api/chat/sessions', { method: 'POST', headers: auth, data: JSON.stringify({}) })).json();
  await api(`/api/chat/sessions/${encodeURIComponent(session.id)}/messages`, { method: 'POST', headers: auth, data: JSON.stringify({ content: `usage probe ${stamp}` }) });

  // The mock reports usage {prompt:1, completion:1, total:2} for chat turns.
  const runs = await (await api('/api/ai/runs', { headers: auth })).json();
  const run = runs.find((entry) => entry.feature === 'chat' && entry.status === 'ok');
  expect(run).toBeTruthy();
  expect(run.totalTokens).toBe(2);
  expect(run.promptTokens).toBe(1);
  expect(run.completionTokens).toBe(1);
  expect(run.provider).toBe('priced-llm');
  // 2 tokens on gpt-4o-mini: (1*0.15 + 1*0.60) USD per 1M → sub-micro, rounded
  // up to at least 1 micro so the ledger never shows a positive-only phantom.
  expect(run.costMicros).toBeGreaterThanOrEqual(1);

  // The policy usage summary aggregates the same rows per provider + model.
  const policy = await (await api('/api/ai/policy', { headers: auth })).json();
  expect(policy.usage.totalCalls).toBeGreaterThanOrEqual(1);
  expect(policy.usage.totalTokens).toBeGreaterThanOrEqual(2);
  expect(policy.usage.currency).toBe('USD');
  const group = policy.usage.byProvider.find((entry) => entry.provider === 'priced-llm');
  expect(group).toBeTruthy();
  expect(group.calls).toBeGreaterThanOrEqual(1);
  expect(group.costMicros).toBeGreaterThanOrEqual(1);

  // Deactivate the priced provider again so the active one stays mock-model.
  await api('/api/providers', { method: 'POST', headers: auth, data: JSON.stringify({ name: 'mock-llm', baseUrl: 'http://127.0.0.1:11434/v1', model: 'mock-model', apiKey: 'mock-key-123', activate: true }) });
});

test('runs queued AI jobs with retries and honours cancellation', async ({ page, request, baseURL }) => {
  test.setTimeout(60_000);
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();

  // Success path: the mock returns JSON flashcards, the job completes and the
  // cards land in the workspace study queue.
  const goodNote = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Job source ${stamp}\n\nMaterial for cards.`, category: 'notes' }) })).json();
  const job = await (await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'study.generate', noteId: goodNote.id, maxAttempts: 2 }) })).json();
  expect(job.status).toBe('queued');
  const succeeded = await waitFor(async () => {
    const rows = await (await api('/api/ai/jobs', { headers: auth })).json();
    return rows.find((entry) => entry.id === job.id && entry.status === 'succeeded') || null;
  });
  expect(succeeded).toBeTruthy();
  expect(succeeded.attempts).toBe(1);
  const queue = await (await api('/api/study/items', { headers: auth })).json();
  expect(queue.some((item) => item.note === goodNote.id && item.question === 'Mock question 1?')).toBe(true);

  // Failure path with retries: the note contains the mock's no-JSON marker, so
  // attempt 1 fails, the job goes back to queued with a backoff, and then it is
  // cancelled before attempt 2.
  const badNote = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Job failing ${stamp}\n\nMOCK_NO_JSON`, category: 'notes' }) })).json();
  const doomed = await (await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'study.generate', noteId: badNote.id, maxAttempts: 3 }) })).json();
  const retried = await waitFor(async () => {
    const rows = await (await api('/api/ai/jobs', { headers: auth })).json();
    const row = rows.find((entry) => entry.id === doomed.id);
    return row && row.attempts >= 1 && row.status === 'queued' && row.lastError ? row : null;
  }, 25_000);
  expect(retried).toBeTruthy();
  expect(retried.lastError).toContain('flashcards');

  // A queued job (even scheduled for a later retry) can be cancelled.
  const cancelledResponse = await api(`/api/ai/jobs/${encodeURIComponent(doomed.id)}/cancel`, { method: 'POST', headers: auth, data: JSON.stringify({}) });
  expect(cancelledResponse.status()).toBe(200);
  expect((await cancelledResponse.json()).status).toBe('cancelled');

  // Cancelling history is refused.
  const lateCancel = await api(`/api/ai/jobs/${encodeURIComponent(job.id)}/cancel`, { method: 'POST', headers: auth, data: JSON.stringify({}) });
  expect(lateCancel.status()).toBe(409);

  // Unknown kinds and foreign notes are refused before a job is created.
  expect((await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'world-domination', noteId: goodNote.id }) })).status()).toBe(400);
  expect((await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'study.generate', noteId: 'no-such-note' }) })).status()).toBe(404);

  // The Settings → AI Jobs panel renders the lifecycle.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="ai"]').click();
  await expect(page.locator('#ai-jobs-panel')).toBeVisible();
  await expect(page.locator('#ai-jobs-list .provider-row').first()).toBeVisible();
});

test('deduplicates queued jobs by idempotency key and re-runs after terminal', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();
  await api('/api/providers', { method: 'POST', headers: auth, data: JSON.stringify({ name: 'mock-llm', baseUrl: 'http://127.0.0.1:11434/v1', model: 'mock-model', apiKey: 'mock-key-123', activate: true }) });
  const note = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Idem source ${stamp}\n\nMaterial.`, category: 'notes' }) })).json();

  // First enqueue creates the job. It is scheduled 10 minutes out so the
  // worker's 5s tick cannot claim it while this test dedupes against it.
  const first = await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'study.generate', noteId: note.id, maxAttempts: 1, idempotencyKey: `idem-${stamp}`, runAt: new Date(Date.now() + 10 * 60_000).toISOString() }) });
  expect(first.status()).toBe(201);
  const job = await first.json();
  expect(job.created).toBe(true);
  expect(job.idempotencyKey).toBe(`idem-${stamp}`);

  // An immediate retry with the same key resolves to the same job, not a new
  // spend.
  const retry = await (await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'study.generate', noteId: note.id, maxAttempts: 1, idempotencyKey: `idem-${stamp}` }) })).json();
  expect(retry.created).toBe(false);
  expect(retry.id).toBe(job.id);

  // The same payload without a caller key derives the same identity, so a
  // double-click is also safe.
  const derived = await (await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'study.generate', noteId: note.id, maxAttempts: 1 }) })).json();
  expect(derived.created).toBe(false);
  expect(derived.id).toBe(job.id);

  // After the job reaches a terminal state the key is free: re-running is a
  // new, deliberate spend with a fresh job. Cancelling the scheduled job is
  // what makes it terminal deterministically instead of waiting on the worker.
  const cancelled = await api(`/api/ai/jobs/${job.id}/cancel`, { method: 'POST', headers: auth });
  expect(cancelled.status()).toBe(200);
  const finished = await waitFor(async () => {
    const rows = await (await api('/api/ai/jobs', { headers: auth })).json();
    return rows.find((entry) => entry.id === job.id && ['succeeded', 'failed', 'cancelled'].includes(entry.status)) || null;
  });
  expect(finished).toBeTruthy();
  const rerun = await (await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'study.generate', noteId: note.id, maxAttempts: 1, idempotencyKey: `idem-${stamp}` }) })).json();
  expect(rerun.created).toBe(true);
  expect(rerun.id).not.toBe(job.id);
});

test('ledgers every provider attempt before the call and enforces the monthly budget', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();

  // A fresh workspace gives exact control over the ledger.
  const created = await (await api('/api/workspaces', { method: 'POST', headers: auth, data: JSON.stringify({ name: `Budget ${stamp}` }) })).json();
  const wsId = created.workspace?.id || created.id;

  // Budget of 1 micro-USD: the first provider call (any cost >= 1 micro)
  // exhausts it. The priced provider must be active — unpriced models are
  // free by design, so the budget could never trip over them.
  await api('/api/providers', { method: 'POST', headers: auth, data: JSON.stringify({ name: 'priced-llm', baseUrl: 'http://127.0.0.1:11434/v1', model: 'gpt-4o-mini', apiKey: 'k', activate: true }) });
  await api('/api/ai/policy', { method: 'PATCH', headers: auth, data: JSON.stringify({ monthlyBudgetMicros: 1 }) });
  const policy = await (await api('/api/ai/policy', { headers: auth })).json();
  expect(policy.monthlyBudgetMicros).toBe(1);
  expect(policy.budget.budget).toBe(1);
  expect(policy.budget.spend).toBe(0);
  expect(policy.budget.limited).toBe(false);

  const session = await (await api('/api/chat/sessions', { method: 'POST', headers: auth, data: JSON.stringify({}) })).json();
  const first = await api(`/api/chat/sessions/${encodeURIComponent(session.id)}/messages`, { method: 'POST', headers: auth, data: JSON.stringify({ content: `budget probe ${stamp}` }) });
  expect(first.status()).toBe(201);

  // The ledger row was completed with its cost.
  const policyAfter = await (await api('/api/ai/policy', { headers: auth })).json();
  expect(policyAfter.budget.spend).toBeGreaterThanOrEqual(1);
  expect(policyAfter.usage.monthCostMicros).toBe(policyAfter.budget.spend);

  // The second call is refused with the budget message, not the cap one.
  const second = await api(`/api/chat/sessions/${encodeURIComponent(session.id)}/messages`, { method: 'POST', headers: auth, data: JSON.stringify({ content: 'should be budget-blocked' }) });
  expect(second.status()).toBe(429);
  expect((await second.json()).error).toContain('monthly AI budget');

  // Study generation and job enqueue hit the same wall.
  const note = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Budget note ${stamp}\n\n- Q :: A`, category: 'notes' }) })).json();
  expect((await api('/api/study/generate', { method: 'POST', headers: auth, data: JSON.stringify({ noteId: note.id, mode: 'auto' }) })).status()).toBe(429);
  expect((await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'study.generate', noteId: note.id }) })).status()).toBe(429);

  // Removing the budget unblocks everything.
  await api('/api/ai/policy', { method: 'PATCH', headers: auth, data: JSON.stringify({ monthlyBudgetMicros: null }) });
  expect((await api(`/api/chat/sessions/${encodeURIComponent(session.id)}/messages`, { method: 'POST', headers: auth, data: JSON.stringify({ content: 'unblocked' }) })).status()).toBe(201);

  // Restore the unpriced active provider for the tests that follow.
  await api('/api/providers', { method: 'POST', headers: auth, data: JSON.stringify({ name: 'mock-llm', baseUrl: 'http://127.0.0.1:11434/v1', model: 'mock-model', apiKey: 'mock-key-123', activate: true }) });

  // Budget input in Settings → AI shows the month line.
  await page.locator('[data-view="settings"]').click();
  await page.locator('[data-settings-tab="ai"]').click();
  await expect(page.locator('#ai-policy-budget')).toBeVisible();
  await expect(page.locator('#ai-policy-panel')).toContainText('This month:');
});

test('queues a summarize job that produces a linked summary note', async ({ page, request, baseURL }) => {
  const api = (path, options = {}) => request.fetch(`${baseURL}${path}`, {
    ...options,
    headers: { 'content-type': 'application/json', ...(options.headers || {}) },
  });
  await signInAsSharedAdmin(page);
  const auth = { authorization: `Bearer ${await page.evaluate(() => localStorage.getItem('planing-token'))}` };
  const stamp = Date.now();

  // Summarize a note: the job lands a markdown summary note tagged ai-summary.
  // The first enqueue is scheduled far out so the warm-dedupe window is
  // deterministic — the worker cannot claim it mid-test.
  const source = await (await api('/api/notes', { method: 'POST', headers: auth, data: JSON.stringify({ content: `# Photosynthesis ${stamp}\n\nPlants convert light into chemical energy.`, category: 'notes' }) })).json();
  const scheduled = await (await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'summarize.note', noteId: source.id, runAt: new Date(Date.now() + 10 * 60_000).toISOString() }) })).json();
  expect(scheduled.created).toBe(true);

  // A second summarize of the same note dedupes while the first is still warm
  // — same identity, no double spend. After completion it would be a new job.
  const again = await (await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'summarize.note', noteId: source.id }) })).json();
  expect(again.created).toBe(false);
  expect(again.id).toBe(scheduled.id);

  // Cancelling frees the identity: the real run then creates a fresh job.
  expect((await api(`/api/ai/jobs/${scheduled.id}/cancel`, { method: 'POST', headers: auth })).status()).toBe(200);
  const job = await (await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'summarize.note', noteId: source.id }) })).json();
  expect(job.created).toBe(true);
  const finished = await waitFor(async () => {
    const rows = await (await api('/api/ai/jobs', { headers: auth })).json();
    return rows.find((entry) => entry.id === job.id && ['succeeded', 'failed'].includes(entry.status)) || null;
  });
  expect(finished?.status).toBe('succeeded');
  const notes = await (await api('/api/notes', { headers: auth })).json();
  const summary = notes.find((entry) => entry.metadata?.job === job.id);
  expect(summary).toBeTruthy();
  expect(summary.content).toContain('Summary:');
  expect(summary.content).toContain('Photosynthesis');
  expect(summary.flags.ai_summary).toBe(true);
  expect(summary.tags.some((tag) => tag.name === 'ai-summary')).toBe(true);
  // The summarize run is visible in the ledger under its own feature.
  const runs = await (await api('/api/ai/runs', { headers: auth })).json();
  const run = runs.find((entry) => entry.feature === 'summarize.note' && entry.job === job.id);
  expect(run).toBeTruthy();
  expect(run.totalTokens).toBeGreaterThan(0);

  // An attachment with extracted text summarizes via the same kind; an
  // attachment without text is refused.
  const withText = await request.fetch(`${baseURL}/api/attachments`, {
    method: 'POST', headers: { authorization: auth.authorization, 'x-file-name': `readme-${stamp}.md`, 'x-file-type': 'text/markdown' },
    data: `# Guide ${stamp}\n\nThis guide explains the workflow step by step.`,
  });
  expect(withText.status()).toBe(201);
  const attachment = await withText.json();
  expect(attachment.hasText).toBe(true);
  const attachmentJob = await (await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'summarize.note', attachmentId: attachment.id }) })).json();
  expect(attachmentJob.created).toBe(true);

  const binary = await request.fetch(`${baseURL}/api/attachments`, {
    method: 'POST', headers: { authorization: auth.authorization, 'x-file-name': `pixel-${stamp}.png`, 'x-file-type': 'image/png' },
    data: Buffer.from('89504e470d0a1a0a0000000d494844520000000100000001080600000,hex-only', 'utf8'),
  });
  const image = await binary.json();
  const noText = await api('/api/ai/jobs', { method: 'POST', headers: auth, data: JSON.stringify({ kind: 'summarize.note', attachmentId: image.id }) });
  expect([400, 404]).toContain(noText.status());

  // The note card carries the Summarize action.
  await page.locator('[data-view="notes"]').click();
  await page.locator('#note-search').fill(`Photosynthesis ${stamp}`);
  await page.locator('#note-search').dispatchEvent('input');
  // The note card carries the Summarize action. The summary note quotes the
  // source title, so two cards match the search — the first is the source.
  await expect(page.locator('.note', { hasText: `Photosynthesis ${stamp}` }).locator('[data-note-summarize]').first()).toBeVisible();
});

test('clearing planning dates on a note removes them instead of leaving stale values', async ({ page }) => {
  // This spec is a serial sequence whose first test seeds the admin, so a
  // filtered run (`--grep`) arrives with no account. Authenticate through the
  // API instead of the form: log in when the admin exists, register it when it
  // does not (the first account bootstraps without an invitation), then let the
  // app pick the session up from localStorage as it does on any reload.
  await page.goto('/');
  const auth = await page.evaluate(async (credentials) => {
    const post = (path, body) => fetch(path, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    });
    let response = await post('/api/auth/login', credentials);
    if (!response.ok) response = await post('/api/auth/register', credentials);
    if (!response.ok) return { ok: false, status: response.status };
    const body = await response.json();
    localStorage.setItem('planing-token', body.token);
    return { ok: true };
  }, admin);
  expect(auth.ok).toBe(true);
  await page.reload();
  await expect(page.locator('#app-panel')).toBeVisible({ timeout: 10_000 });

  const stamp = Date.now();
  const result = await page.evaluate(async (marker) => {
    const token = localStorage.getItem('planing-token');
    const headers = { 'content-type': 'application/json', authorization: `Bearer ${token}` };
    const created = await fetch('/api/notes', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        content: marker,
        category: 'notes',
        status: 'todo',
        startDate: '2026-10-01T09:00:00.000Z',
        dueDate: '2026-10-02T12:00:00.000Z',
        endDate: '2026-10-03T12:00:00.000Z',
        eventColor: '#4466aa',
      }),
    });
    const note = await created.json();
    // The kanban card editor sends null for an emptied date field. Clearing must
    // reach SurrealDB as NONE: a SCHEMAFULL option<datetime> rejects NULL, and a
    // dropped assignment would silently keep the old date on the card.
    const cleared = await fetch(`/api/notes/${encodeURIComponent(note.id)}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({ startDate: null, dueDate: null, endDate: null, eventColor: null }),
    });
    const listed = await fetch(`/api/notes?view=all`, { headers: { authorization: `Bearer ${token}` } });
    const after = (await listed.json()).find((entry) => entry.id === note.id) || null;
    return {
      created: { start: note.startDate, due: note.dueDate, end: note.endDate, color: note.eventColor },
      clearStatus: cleared.status,
      after: after && { start: after.startDate, due: after.dueDate, end: after.endDate, color: after.eventColor },
    };
  }, `planning clear ${stamp}`);

  expect(result.created.start).toBeTruthy();
  expect(result.created.due).toBeTruthy();
  expect(result.created.end).toBeTruthy();
  expect(result.created.color).toBe('#4466aa');
  expect(result.clearStatus).toBe(200);
  expect(result.after).not.toBeNull();
  expect(result.after.start).toBeNull();
  expect(result.after.due).toBeNull();
  expect(result.after.end).toBeNull();
  expect(result.after.color).toBeNull();
});
