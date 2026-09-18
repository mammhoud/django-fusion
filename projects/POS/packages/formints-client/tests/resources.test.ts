import { describe, it, expect, vi, afterEach } from 'vitest';
import { createClient } from '../src/core';
import { listCurrencies, createCurrency } from '../src/currencies';
import { listTaxProfiles } from '../src/taxProfiles';
import { exportUrl } from '../src/exports';
import { getMonitorStatus } from '../src/monitor';

describe('resource modules', () => {
  afterEach(() => vi.restoreAllMocks());

  it('lists and creates currencies', async () => {
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ count: 1, items: [{ code: 'USD' }] }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ code: 'EUR' }), { status: 201 })));
    const client = createClient('http://api');
    const list = await listCurrencies(client);
    expect(list.items[0]?.code).toBe('USD');
    const created = await createCurrency(client, { code: 'EUR', name: 'Euro', symbol: '€', exchange_rate: '0.92' });
    expect(created.code).toBe('EUR');
  });

  it('lists tax profiles', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ count: 1, items: [{ name: 'Standard' }] }), { status: 200 })));
    const profiles = await listTaxProfiles(createClient('http://api'));
    expect(profiles.items[0]?.name).toBe('Standard');
  });

  it('builds export URLs for csv and json', () => {
    expect(exportUrl('http://api', 'products', 'csv')).toBe('http://api/export/products.csv');
    expect(exportUrl('http://api', 'sales', 'json')).toBe('http://api/export/sales.csv?format=json');
  });

  it('reads monitor status', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ database: 'ok', last_backup: null, sync_queue_depth: 0 }), { status: 200 })));
    const status = await getMonitorStatus(createClient('http://api'));
    expect(status.database).toBe('ok');
  });
});
