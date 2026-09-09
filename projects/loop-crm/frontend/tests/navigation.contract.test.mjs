import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const read = (relativePath) => readFile(resolve(ROOT, relativePath), 'utf8');

test('Astro shell preloads the complete backend navigator before interaction', async () => {
  const shell = await read('src/components/AppShell.astro');
  assert.match(shell, /\/fragments\/navigation\/\?variant=astro/);
  assert.match(shell, /hx-trigger="load"/);
  assert.match(shell, /hx-select="\*"/);
  assert.match(shell, /htmx:afterSettle/);
  assert.match(shell, /refreshNavigator/);
});

test('Bolt client owns token storage, refresh rotation, retry, and fallback behavior', async () => {
  const client = await read('src/lib/boltApi.ts');
  assert.match(client, /sessionStorage/);
  assert.match(client, /refreshInFlight/);
  assert.match(client, /auth\/refresh/);
  assert.match(client, /response\.status === 401/);
  assert.match(client, /fallbackPrefix/);
  assert.match(client, /clearSession/);
  assert.match(client, /retry401/);
});

test('AI Hub exposes consent, bounded briefs, and human-review safeguards', async () => {
  const island = await read('src/components/dashboard/AiHub.tsx');
  const shell = await read('src/pages/[...path].astro');
  assert.match(shell, /import AiHub/);
  assert.match(shell, /page\.path === '\/ai\/'/);
  assert.match(island, /\/apis\/core\/ai\//);
  assert.match(island, /X-CSRFToken/);
  assert.match(island, /maxLength=\{12000\}/);
  assert.match(island, /!catalog\?\.consent/);
  assert.match(island, /human (approval|review)|human-review/i);
});

test('frontend navigation keeps every module and subpage route explicit', async () => {
  const navigation = await read('src/lib/navigation.ts');
  const page = await read('src/pages/[...path].astro');
  for (const route of ['/crm/companies/', '/crm/deals/', '/marketing/calendar/', '/finance/invoices/', '/settings/workflows/', '/ai/']) {
    assert.match(navigation, new RegExp(route.replaceAll('/', '\\/')));
    assert.match(page, new RegExp(route.replaceAll('/', '\\/')));
  }
});
