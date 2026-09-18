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

test('workspace controls wire ledger settings to AI, automation, and integration APIs', async () => {
  const component = await read('src/components/dashboard/WorkspaceControls.tsx');
  const page = await read('src/pages/[...path].astro');
  assert.match(component, /settings\/ledger/);
  assert.match(component, /settings\/workflows/);
  assert.match(component, /\/apis\/core\/ai/);
  assert.match(component, /X-CSRFToken/);
  assert.match(page, /WorkspaceControls/);
  assert.match(page, /settings\/ledger/);
});

test('pipeline manager exposes ordered stage CRUD and kanban configuration', async () => {
  const manager = await read('src/components/dashboard/PipelineManager.tsx');
  const page = await read('src/pages/[...path].astro');
  assert.match(page, /PipelineManager client:load/);
  assert.match(manager, /pipeline_stages/);
  assert.match(manager, /const API = '\/apis\/core\/resources'/);
  assert.match(manager, /method: 'POST'/);
  assert.match(manager, /method: 'PATCH'/);
  assert.match(manager, /method: 'DELETE'/);
  assert.match(manager, /Stage order updated/);
  assert.match(manager, /probability/);
});

test('content calendar mounts a live CRUD surface with filters and CSRF mutations', async () => {
  const calendar = await read('src/components/dashboard/ContentCalendar.tsx');
  const page = await read('src/pages/[...path].astro');
  assert.match(page, /ContentCalendar client:load/);
  assert.match(calendar, /const API = '\/apis\/core\/resources'/);
  assert.match(calendar, /method: editing \? 'PATCH' : 'POST'/);
  assert.match(calendar, /method: 'DELETE'/);
  assert.match(calendar, /calendar-status/);
  assert.match(calendar, /X-CSRFToken/);
});

test('render-first shell uses backend HTMX navigation and canonical API roads', async () => {
  const shell = await read('src/components/AppShell.astro');
  const landing = await read('src/lib/landing.ts');
  const config = await read('src/store/slices/configSlice.ts');
  assert.match(shell, /hx-get=\{`\/fragments\/navigation/);
  assert.match(shell, /hx-target="this"/);
  assert.match(shell, /responseError/);
  assert.match(landing, /same-origin proxy/);
  assert.match(landing, /PUBLIC_BACKEND_URL/);
  assert.match(config, /PUBLIC_API_FALLBACK_PREFIX \?\? '\/apis\/core'/);
});

test('render-first shell keeps backend templates authoritative and Alpine presentation-only', async () => {
  const shell = await read('src/components/AppShell.astro');
  const alpine = await read('src/pages/index.astro');
  const template = await read('../backend/templates/dashboard/resource_list.html');
  assert.match(shell, /Workspace navigation unavailable/);
  assert.match(shell, /htmx:responseError/);
  assert.match(alpine, /x-data/);
  assert.match(alpine, /x-intersect/);
  assert.match(template, /\{% for row in table_rows %\}/);
  assert.match(template, /\{% if table_rows %\}/);
  assert.match(template, /loop-empty-state/);
  assert.doesNotMatch(template, /mock|localhost/);
});

test('top-level module pages mount live overview components instead of placeholder cards', async () => {
  const page = await read('src/pages/[...path].astro');
  const overview = await read('src/components/dashboard/ModuleOverview.tsx');
  assert.match(page, /import ModuleOverview/);
  assert.match(page, /isModuleOverview && <ModuleOverview module=\{page\.module as/);
  assert.match(page, /ModuleOverview module=.*client:load/);
  assert.match(page, /isModuleOverview/);
  assert.match(overview, /fetch\('\/apis\/core\/dashboard\//);
  assert.match(overview, /No fallback records were loaded/);
  assert.match(overview, /Retry request/);
  assert.match(overview, /live records in view/);
  assert.doesNotMatch(overview, /localhost|mock data|placeholder records/);
});

test('frontend navigation keeps every module and subpage route explicit', async () => {
  const navigation = await read('src/lib/navigation.ts');
  const page = await read('src/pages/[...path].astro');
  for (const route of ['/crm/companies/', '/crm/deals/', '/marketing/calendar/', '/finance/invoices/', '/settings/workflows/', '/settings/ledger/', '/ai/']) {
    assert.match(navigation, new RegExp(route.replaceAll('/', '\\/')));
    assert.match(page, new RegExp(route.replaceAll('/', '\\/')));
  }
});
