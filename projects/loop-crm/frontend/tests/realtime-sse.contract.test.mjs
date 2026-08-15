import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import assert from 'node:assert/strict';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const read = (relativePath) => readFile(resolve(ROOT, relativePath), 'utf8');

test('Astro shell bundles the htmx SSE extension alongside htmx core', async () => {
  const layout = await read('src/layouts/Layout.astro');
  assert.match(layout, /import 'htmx\.org'/);
  assert.match(layout, /import 'htmx-ext-sse'/);
});

test('htmx-ext-sse is a declared frontend dependency', async () => {
  const pkg = await read('package.json');
  assert.match(pkg, /"htmx-ext-sse"\s*:\s*"\^2\.2\.4"/);
});

test('render-first shell subscribes to the workspace-scoped SSE stream', async () => {
  const base = await read('../backend/templates/base.html');
  assert.match(base, /htmx-ext-sse@2\.2\.4/);
  assert.match(base, /sse-connect="\/sse\/workspace\/\{\{ workspace_id \}\}\/events\/"/);
  assert.match(base, /hx-trigger="sse:resource\.created, sse:resource\.updated, sse:resource\.deleted, sse:pos\.sales\.ingested"/);
});

test('Astro navigation fragment carries the workspace-scoped SSE subscribe element', async () => {
  const nav = await read('../backend/templates/dashboard/navigation_astro.html');
  assert.match(nav, /sse-connect="\/sse\/workspace\/\{\{ workspace_id \}\}\/events\/"/);
  assert.match(nav, /hx-trigger="sse:resource\.created, sse:resource\.updated, sse:resource\.deleted, sse:pos\.sales\.ingested"/);
});

test('navigation fragment exposes workspace_id in its context', async () => {
  const views = await read('../backend/apps/core/views.py');
  assert.match(views, /"workspace_id": current_workspace_id\(request\)/);
});

test('mutation roads publish workspace events through the realtime helper', async () => {
  const api = await read('../backend/apps/core/api.py');
  assert.match(api, /safe_publish_workspace_event\(\s*workspace_id, "resource\.created"/);
  const crmViews = await read('../backend/apps/crm/views.py');
  assert.match(crmViews, /safe_publish_workspace_event/);
  const financeViews = await read('../backend/apps/finance/views.py');
  assert.match(financeViews, /safe_publish_workspace_event/);
});

test('ASGI entry point routes websockets through the workspace event consumer', async () => {
  const asgi = await read('../backend/asgi.py');
  assert.match(asgi, /ProtocolTypeRouter/);
  assert.match(asgi, /websocket_urlpatterns/);
  assert.match(asgi, /AllowedHostsOriginValidator/);
  assert.match(asgi, /AuthMiddlewareStack/);
});

test('realtime module defines the workspace group + SSE + WebSocket transports', async () => {
  const realtime = await read('../backend/apps/core/realtime.py');
  assert.match(realtime, /workspace_group\(workspace_id\)/);
  assert.match(realtime, /WorkspaceEventConsumer/);
  assert.match(realtime, /workspace_events_sse/);
  assert.match(realtime, /safe_publish_workspace_event/);
});

test('session workspace-id endpoint feeds the WebSocket URL without hardcoding a tenant', async () => {
  const api = await read('../backend/apps/core/api.py');
  assert.match(api, /def workspace_current_api/);
  assert.match(api, /current_workspace_id\(request\)/);
  const urls = await read('../backend/apps/core/urls.py');
  assert.match(urls, /workspace\/current\//);
});

test('useWorkspaceRealtime opens a workspace-scoped WebSocket with backoff + cleanup', async () => {
  const hook = await read('src/lib/useWorkspaceRealtime.ts');
  assert.match(hook, /new WebSocket\(socketUrl\(workspaceId\)\)/);
  assert.match(hook, /\/api\/v1\/workspace\/current\//);
  assert.match(hook, /MAX_BACKOFF_MS/);
  assert.match(hook, /socket\?\.close\(\)/);
});

test('PipelineBoard subscribes to deal/pipeline mutations and silently refreshes', async () => {
  const board = await read('src/components/board/PipelineBoard.tsx');
  assert.match(board, /useWorkspaceRealtime/);
  assert.match(board, /loadBoard\(true\)/);
  assert.match(board, /\['deals', 'pipelines'\]\.includes/);
});

test('RevOpsDashboard subscribes to resource + POS ingest events and silently refreshes', async () => {
  const island = await read('src/components/dashboard/RevOpsDashboard.tsx');
  assert.match(island, /useWorkspaceRealtime/);
  assert.match(island, /loadDashboard\(true\)/);
  assert.match(island, /event\.event === 'pos\.sales\.ingested'/);
});

test('useLiveSync flashes a self-dismissing synced flag on each refresh', async () => {
  const hook = await read('src/lib/useLiveSync.ts');
  assert.match(hook, /export function useLiveSync/);
  assert.match(hook, /setSynced\(true\)/);
  assert.match(hook, /setTimeout\(\(\) => setSynced\(false\), durationMs\)/);
});

test('board and dashboard flash a pulsing synced chip when a realtime refresh lands', async () => {
  const board = await read('src/components/board/PipelineBoard.tsx');
  assert.match(board, /useLiveSync/);
  assert.match(board, /flash\(\)/);
  assert.match(board, /loop-live-sync/);
  assert.match(board, /data-synced=\{synced \? 'true' : 'false'\}/);

  const island = await read('src/components/dashboard/RevOpsDashboard.tsx');
  assert.match(island, /useLiveSync/);
  assert.match(island, /flash\(\)/);
  assert.match(island, /loop-live-sync/);
  assert.match(island, /synced \? 'synced' : 'live'/);
});

test('Astro dev proxy upgrades /ws to the backend for the WebSocket consumer', async () => {
  const config = await read('astro.config.mjs');
  assert.match(config, /'\/ws': \{ target: BACKEND_URL, changeOrigin: true, ws: true \}/);
});
