import { test, expect, request } from '@playwright/test';
import {
  CLOUD_API,
  E2E_NODE_ID,
  cloudRequest,
  syncPush,
  productPayload,
  salePayload,
  connectSyncSocket,
  waitForSyncEvent,
} from '../../helpers/sync';

/**
 * Live Formint Cloud sync contract.
 *
 * Prerequisites (boot once before this project):
 *   cd projects/formints/formint-cloud
 *   make migrate
 *   make dev-api        # daphne :8767 (REST + /ws/sync-events/)
 *   make dev-backend    # runserver :8082 (admin + analytics)
 *
 * The sync push flow needs an active Branch with `node_id == E2E_NODE_ID`
 * (seed once via `manage.py shell`, or override E2E_NODE_ID).
 */

test.describe('cloud REST surface', () => {
  test('health reports healthy', async () => {
    const ctx = await cloudRequest();
    const res = await ctx.get('/health');
    expect(res.ok()).toBeTruthy();
    expect(await res.json()).toMatchObject({ status: 'healthy' });
  });

  test('stats enumerates core models', async () => {
    const ctx = await cloudRequest();
    const res = await ctx.get('/stats');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.models).toContain('Branch');
    expect(body.models).toContain('SyncQueueItem');
    expect(body).toHaveProperty('counts');
  });

  test('monitor status matches the @formints/client contract', async () => {
    const ctx = await cloudRequest();
    const res = await ctx.get('/monitor/status');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(['ok', 'error']).toContain(body.database);
    expect(typeof body.sync_queue_depth).toBe('number');
    expect(body.last_backup === null || typeof body.last_backup === 'object').toBeTruthy();
  });

  test('dashboard health/queue/conflicts endpoints return arrays+counts', async () => {
    const ctx = await cloudRequest();
    const health = await (await ctx.get('/api/dashboard/branches/health')).json();
    expect(Array.isArray(health.branches)).toBeTruthy();

    const queue = await (await ctx.get('/api/dashboard/queue/summary')).json();
    expect(typeof queue.pending).toBe('number');
    expect(typeof queue.failed).toBe('number');

    const conflicts = await (await ctx.get('/api/dashboard/conflicts')).json();
    expect(typeof conflicts.count).toBe('number');
    expect(Array.isArray(conflicts.conflicts)).toBeTruthy();
  });
});

test.describe('cloud sync push + WebSocket', () => {
  test('sync push products broadcasts a sync_event over /ws/sync-events/', async ({ page }) => {
    // Open the WebSocket on the cloud API origin first.
    await page.goto(`${CLOUD_API}/health`);
    const { ack } = await connectSyncSocket(page, { branchCode: 'E2E001', nodeId: E2E_NODE_ID });

    // identify → identify_ack contract.
    expect(ack).toMatchObject({
      type: 'identify_ack',
      branch_code: 'E2E001',
      node_id: E2E_NODE_ID,
      status: 'registered',
    });

    // Trigger a branch sync push from the HTTP side.
    const ctx = await cloudRequest();
    const push = await syncPush(ctx, 'products', productPayload(E2E_NODE_ID, 2));
    expect(push.ok()).toBeTruthy();
    expect(await push.json()).toMatchObject({ status: 'received', synced: 2 });

    // The broadcast frame arrives on the same daphne process.
    const frame = await waitForSyncEvent(page, 'products');
    expect(frame.entity_type).toBe('products');
    expect(frame.synced).toBe(2);
    expect(frame.node_id).toBe(E2E_NODE_ID);
  });

  test('sync push sales is accepted and reflected in the activity feed', async () => {
    const ctx = await cloudRequest();
    const push = await syncPush(ctx, 'sales', salePayload(E2E_NODE_ID, 1));
    expect(push.ok()).toBeTruthy();
    expect(await push.json()).toMatchObject({ status: 'received', synced: 1 });

    const activity = await (await ctx.get('/api/dashboard/activity?limit=50')).json();
    expect(Array.isArray(activity.entries)).toBeTruthy();
    expect(activity.entries.some((e: any) => e.entity_type === 'sales')).toBeTruthy();
  });

  test('sync push with unknown node returns 404', async () => {
    const ctx = await cloudRequest();
    const res = await syncPush(ctx, 'products', productPayload('no-such-node', 1));
    expect(res.status()).toBe(404);
  });
});
