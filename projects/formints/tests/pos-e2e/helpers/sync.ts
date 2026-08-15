import { APIRequestContext, request as pwRequest } from '@playwright/test';

/**
 * Cloud sync contract helpers — REST sync push + WebSocket sync-events.
 *
 * These target the Formint Cloud Django backend (daphne :8767), which owns the
 * REST/API surface and the `/ws/sync-events/` WebSocket stream after the Robyn
 * server was removed. They complement the backend pytest parity tests
 * (`apps/test_ws_parity_contract.py`, `apps/test_dashboard_contract.py`) with
 * a live, cross-process E2E pass.
 */

export const CLOUD_API = process.env.CLOUD_API_URL ?? 'http://127.0.0.1:8767';
export const CLOUD_ADMIN = process.env.CLOUD_ADMIN_URL ?? 'http://127.0.0.1:8082';

/** The branch node the tests push from (seeded via `manage.py shell`). */
export const E2E_NODE_ID = process.env.E2E_NODE_ID ?? 'e2e-node-1';
export const E2E_BRANCH_CODE = process.env.E2E_BRANCH_CODE ?? 'E2E001';

/** Create a Playwright API request context bound to the cloud API. */
export function cloudRequest(baseURL: string = CLOUD_API): Promise<APIRequestContext> {
  return pwRequest.newContext({ baseURL });
}

/** Push a sync payload to `/api/sync/push/{entityType}`. */
export async function syncPush(
  ctx: APIRequestContext,
  entityType: 'products' | 'sales' | 'inventory' | 'heartbeat',
  payload: Record<string, unknown>,
) {
  return ctx.post(`/api/sync/push/${entityType}`, { data: payload });
}

/** A product payload usable with `syncPush('products', …)`. */
export function productPayload(nodeId: string = E2E_NODE_ID, n = 1) {
  return {
    node_id: nodeId,
    products: Array.from({ length: n }, (_, i) => ({
      id: `e2e-prod-${i}`,
      name: `E2E Product ${i}`,
      sku: `E2E-SKU-${i}`,
      price: 9.99 + i,
      category_name: 'E2E',
      stock_quantity: 10,
      is_active: true,
    })),
  };
}

/** A sale payload usable with `syncPush('sales', …)`. */
export function salePayload(nodeId: string = E2E_NODE_ID, n = 1) {
  return {
    node_id: nodeId,
    sales: Array.from({ length: n }, (_, i) => ({
      id: `e2e-sale-${i}`,
      customer_name: 'E2E Customer',
      total_amount: 19.99 + i,
      payment_method: 'cash',
      item_count: 1,
      items: [],
    })),
  };
}

/**
 * Connect a WebSocket to `/ws/sync-events/`, send `identify`, and resolve with
 * the `identify_ack`. Frames received after the ack are appended to
 * `window.__syncFrames` so the test can wait for broadcast `sync_event`s.
 *
 * The page must already be on the cloud API origin (`page.goto(CLOUD_API + …)`)
 * so the WebSocket handshake is same-origin.
 */
export async function connectSyncSocket(
  page: import('@playwright/test').Page,
  { branchCode = E2E_BRANCH_CODE, nodeId = E2E_NODE_ID } = {},
) {
  const wsUrl = CLOUD_API.replace(/^http/, 'ws') + '/ws/sync-events/';
  return page.evaluate(
    async ({ wsUrl, branchCode, nodeId }) => {
      (window as any).__syncFrames = [];
      return new Promise<{ ack: Record<string, unknown> }>((resolve, reject) => {
        const ws = new WebSocket(wsUrl);
        const timer = setTimeout(() => reject(new Error('ws identify timeout')), 8000);
        ws.onopen = () =>
          ws.send(JSON.stringify({ type: 'identify', payload: { branch_code: branchCode, node_id: nodeId } }));
        ws.onmessage = (ev) => {
          let frame: any;
          try {
            frame = JSON.parse(ev.data);
          } catch {
            return;
          }
          if (frame.type === 'identify_ack') {
            clearTimeout(timer);
            resolve({ ack: frame });
          } else {
            (window as any).__syncFrames.push(frame);
          }
        };
        ws.onerror = () => {
          clearTimeout(timer);
          reject(new Error('ws error'));
        };
      });
    },
    { wsUrl, branchCode, nodeId },
  );
}

/** Wait until a broadcast `sync_event` frame of the given entity_type arrives. */
export async function waitForSyncEvent(page: import('@playwright/test').Page, entityType: string) {
  await page.waitForFunction(
    (et) => (window as any).__syncFrames?.some((f: any) => f.entity_type === et),
    entityType,
    { timeout: 8000 },
  );
  return page.evaluate((et) => (window as any).__syncFrames.find((f: any) => f.entity_type === et), entityType);
}
