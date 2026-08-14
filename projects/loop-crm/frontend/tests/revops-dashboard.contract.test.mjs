import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const read = (relativePath) => readFile(resolve(ROOT, relativePath), 'utf8');

test('RevOpsDashboard island fetches the dashboard through the compatibility API road', async () => {
  const island = await read('src/components/dashboard/RevOpsDashboard.tsx');
  assert.match(island, /fetch\(`\$\{apiPrefix\}\/dashboard\/`\)/);
  assert.match(island, /fallbackApiPrefix/);
  assert.match(island, /dashboard\.data\.counts/);
  assert.match(island, /workflow_count/);
});

test('RevOpsDashboard consumes the pipeline board for the deal-flow funnel', async () => {
  const island = await read('src/components/dashboard/RevOpsDashboard.tsx');
  assert.match(island, /fetch\(`\$\{apiPrefix\}\/board\/`\)/);
  assert.match(island, /Promise\.allSettled/);
  assert.match(island, /sort\(\(a, b\) => b\.stages\.length - a\.stages\.length\)/);
});

test('RevOpsDashboard funnel stages deep-link to the board filtered by stage', async () => {
  const island = await read('src/components/dashboard/RevOpsDashboard.tsx');
  assert.match(island, /\/crm\/deals\/\?pipeline=\$\{pipeline\?\.id\}&stage=\$\{stage\.id\}/);
  assert.match(island, /loop-dash__stage--link/);
  assert.match(island, /Open the deals board filtered to/);
  assert.match(island, /loop-dash__stage-arrow/);
});

test('RevOpsDashboard trend card fetches the finance revenue-trend endpoint', async () => {
  const island = await read('src/components/dashboard/RevOpsDashboard.tsx');
  assert.match(island, /fetch\(`\$\{apiPrefix\}\/revenue\/trend\/`\)/);
  assert.match(island, /Recognized revenue/);
  assert.match(island, /grand_total/);
  assert.match(island, /trailing six months/);
});

test('Dashboard counts are workspace-scoped on both API roads', async () => {
  const compatApi = await read('../backend/apps/core/api.py');
  assert.match(compatApi, /filter\(workspace_id=workspace_id\) if workspace_id is not None/);
  const boltApi = await read('../backend/apps/core/bolt_api.py');
  assert.match(boltApi, /_workspace_id\(getattr\(request, "user", None\)\)/);
});

test('Finance revenue-trend endpoint is mounted on the API road', async () => {
  const financeUrls = await read('../backend/apps/finance/urls.py');
  assert.match(financeUrls, /revenue\/trend\//);
  assert.match(financeUrls, /revenue_trend_api/);
});

test('Revenue-trend aggregate is registered on the canonical bolt road', async () => {
  const boltApi = await read('../backend/apps/core/bolt_api.py');
  assert.match(boltApi, /@bolt\.get\("\/revenue\/trend", \*\*_protected\)/);
  assert.match(boltApi, /from apps\.finance\.services import revenue_trend_results/);
  assert.match(boltApi, /TruncMonth\("recognized_on"\)/);
  assert.match(boltApi, /filter\(workspace_id=workspace_id\)/);
});

test('RevOpsDashboard uses shadcn components and the StoreProvider bridge', async () => {
  const island = await read('src/components/dashboard/RevOpsDashboard.tsx');
  for (const component of ['Card', 'Badge', 'Button', 'Separator', 'Skeleton', 'Tooltip']) {
    assert.match(island, new RegExp(`${component}`));
  }
  assert.match(island, /components\/ui\/card/);
  assert.match(island, /<StoreProvider>/);
});

test('Overview page mounts the dashboard island on the app-shell road', async () => {
  const shell = await read('src/pages/[...path].astro');
  assert.match(shell, /import RevOpsDashboard/);
  assert.match(shell, /page\.path === '\/overview\/'/);
  assert.match(shell, /<RevOpsDashboard client:load \/>/);
  assert.match(shell, /path: '\/overview\/', title: 'Overview'/);
});

test('Overview navigation points at /overview/ on both the Astro and Django roads', async () => {
  const astroNav = await read('src/lib/navigation.ts');
  assert.match(astroNav, /id: 'overview', label: 'Overview', href: '\/overview\/'/);

  const backendNav = await read('../backend/apps/core/navigation.py');
  assert.match(backendNav, /"href": "\/overview\/"/);
  const backendRoutes = await read('../backend/apps/core/fusion.py');
  assert.match(backendRoutes, /path\("overview\/", DashboardView/);
});

test('Skeleton component is installed for loading placeholders', async () => {
  const skeleton = await read('src/components/ui/skeleton.tsx');
  assert.match(skeleton, /Skeleton/);
});
