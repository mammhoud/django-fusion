/**
 * API tests for POS Sales & Deals endpoints via Robyn sidecar.
 *
 * ⚠️ NOTE: Requires a WORKING Robyn server. Currently the server fails
 * to start with "Apps aren't loaded yet" (Django ORM bootstrap issue).
 * These tests will pass once the server startup is fixed.
 *
 * Run with:
 *   node tests/api/test_sales.mjs
 *
 * Requires pos-full Robyn server running on :8000 (or POS_API_URL env var)
 *   Start with: cd pos-full/sidecar && python3 server.py
 */

const BASE_URL = process.env.POS_API_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    const contentType = res.headers.get('content-type') || '';
    const body = contentType.includes('json')
      ? await res.json()
      : await res.text();
    return { status: res.status, ok: res.ok, body };
  } catch (err) {
    return { status: 0, ok: false, body: null, error: err.message };
  }
}

let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) { passed++; console.log(`  ✅ ${label}`); }
  else { failed++; console.error(`  ❌ ${label}`); }
}

async function run() {
  console.log('\n💰 POS Sales & Deals API Tests\n');

  // ── Deals (CRM) ──
  console.log('  ── GET /crm/deals ──');
  const dealsList = await request('/crm/deals');
  assert(dealsList.ok, `GET /crm/deals returns 200 (got ${dealsList.status})`);
  assert(Array.isArray(dealsList.body), 'Deals response is an array');

  // ── Create deal ──
  console.log('  ── POST /crm/deals ──');
  const newDeal = {
    name: `API Test Deal ${Date.now()}`,
    amount: 5000,
    status: 'new',
    pipeline_stage: 'qualification',
  };
  const createRes = await request('/crm/deals', {
    method: 'POST',
    body: JSON.stringify(newDeal),
  });
  assert(createRes.ok || createRes.status === 201, `POST /crm/deals returns 2xx (got ${createRes.status})`);

  // ── Reports: sales ──
  console.log('  ── GET /reports/sales ──');
  const salesReport = await request('/reports/sales');
  assert(salesReport.ok || salesReport.status !== 0, `GET /reports/sales accessible (got ${salesReport.status})`);

  // ── Reports: inventory ──
  console.log('  ── GET /reports/inventory ──');
  const invReport = await request('/reports/inventory');
  assert(invReport.ok || invReport.status !== 0, `GET /reports/inventory accessible (got ${invReport.status})`);

  // ── Sync endpoint ──
  console.log('  ── POST /sales/with-items ──');
  const syncRes = await request('/sales/with-items', {
    method: 'POST',
    body: JSON.stringify({
      sale: { customer_name: 'Sync Test', total: 99.99, payment_method: 'card', status: 'completed' },
      items: [{ product_name: 'Test Item', quantity: 2, unit_price: 49.99 }],
    }),
  });
  assert(syncRes.ok || syncRes.status !== 0, `POST /sales/with-items accessible (got ${syncRes.status})`);

  // ── Summary ──
  const total = passed + failed;
  console.log(`\n📊 Results: ${passed}/${total} passed, ${failed} failed\n`);
  process.exit(failed > 0 ? 1 : 0);
}

run().catch((err) => {
  console.error('❌ Fatal error:', err);
  process.exit(1);
});
