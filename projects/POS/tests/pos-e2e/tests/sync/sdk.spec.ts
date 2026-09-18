import { test, expect } from '@playwright/test';
import { createClient, getMonitorStatus, exportUrl } from '../../../../packages/formints-client/dist/index.js';
import { CLOUD_API } from '../../helpers/sync';

/**
 * Live `@formints/client` SDK integration.
 *
 * The SDK is built from `packages/formints-client` (`pnpm build`). This spec
 * exercises the one SDK module whose contract is served by the cloud master
 * (`monitor` → GET /monitor/status). `currencies`, `tax-profiles`, and
 * `exports` target the Standard/Pro API surfaces and are covered by the SDK's
 * unit suite (`packages/formints-client/tests`) until those backends are
 * bootable in CI.
 */

test.describe('@formints/client SDK (live cloud)', () => {
  test('getMonitorStatus reads /monitor/status', async () => {
    const client = createClient(CLOUD_API);
    const status = await getMonitorStatus(client);
    expect(['ok', 'error']).toContain(status.database);
    expect(typeof status.sync_queue_depth).toBe('number');
    expect(status.last_backup === null || typeof status.last_backup === 'object').toBeTruthy();
  });

  test('createClient throws ApiError on 404', async () => {
    const client = createClient(CLOUD_API);
    await expect(client.request('/definitely-missing')).rejects.toMatchObject({
      name: 'ApiError',
      status: 404,
    });
  });

  test('exportUrl builds the documented download links', () => {
    expect(exportUrl(CLOUD_API, 'products', 'csv')).toBe(`${CLOUD_API}/export/products.csv`);
    expect(exportUrl(CLOUD_API, 'sales', 'json')).toBe(`${CLOUD_API}/export/sales.csv?format=json`);
  });
});
