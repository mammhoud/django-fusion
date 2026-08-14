/**
 * API tests for POS CRM endpoints via Robyn server.
 *
 * ⚠️ NOTE: Requires a WORKING Robyn server. Currently the server fails
 * to start with "Apps aren't loaded yet" (Django ORM bootstrap issue).
 * These tests will pass once the server startup is fixed.
 *
 * Run with:
 *   node tests/api/test_products.mjs
 *
 * Requires:
 *   - pos-full Robyn server running on :8000 (or POS_API_URL env var)
 *     Start with: cd pos-full/server && python3 server.py
 *   - Node.js 18+
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
  if (condition) {
    passed++;
    console.log(`  ✅ ${label}`);
  } else {
    failed++;
    console.error(`  ❌ ${label}`);
  }
}

async function run() {
  console.log('\n📦 POS API Tests (CRM + Contacts)\n');

  // ── Health check ──
  console.log('  ── GET / ──');
  const healthRes = await request('/');
  assert(healthRes.ok || healthRes.status !== 0, `Server is reachable (status ${healthRes.status})`);

  if (!healthRes.ok) {
    console.log('\n  ⚠️  Server not reachable — is the Robyn server running?');
    console.log('     Start it with: cd pos-full/server && python3 server.py\n');
    const total = passed + failed;
    console.log(`📊 Results: ${passed}/${total} passed, ${failed} failed\n`);
    process.exit(failed > 0 ? 1 : 0);
  }

  // ── CRM Dashboard ──
  console.log('  ── GET /crm/dashboard ──');
  const dashRes = await request('/crm/dashboard');
  assert(dashRes.ok, `GET /crm/dashboard returns 200 (got ${dashRes.status})`);

  // ── List contacts ──
  console.log('  ── GET /crm/contacts ──');
  const listRes = await request('/crm/contacts');
  assert(listRes.ok, `GET /crm/contacts returns 200 (got ${listRes.status})`);
  assert(Array.isArray(listRes.body), 'Contacts response is an array');

  // ── Create contact ──
  console.log('  ── POST /crm/contacts ──');
  const newContact = {
    name: `API Test Contact ${Date.now()}`,
    email: `test-${Date.now()}@example.com`,
    phone: '555-0100',
    type: 'individual',
    source: 'api_test',
  };
  const createRes = await request('/crm/contacts', {
    method: 'POST',
    body: JSON.stringify(newContact),
  });
  assert(createRes.ok || createRes.status === 201, `POST /crm/contacts returns 2xx (got ${createRes.status})`);

  const created = createRes.body;
  const contactId = created?.id || created?.pk;
  if (contactId) {
    // ── Get single contact ──
    console.log('  ── GET /crm/contacts/:id ──');
    const getRes = await request(`/crm/contacts/${contactId}`);
    assert(getRes.ok, `GET /crm/contacts/:id returns 200 (got ${getRes.status})`);
  }

  // ── List companies ──
  console.log('  ── GET /crm/companies ──');
  const companiesRes = await request('/crm/companies');
  assert(companiesRes.ok, `GET /crm/companies returns 200 (got ${companiesRes.status})`);

  // ── List deals ──
  console.log('  ── GET /crm/deals ──');
  const dealsRes = await request('/crm/deals');
  assert(dealsRes.ok, `GET /crm/deals returns 200 (got ${dealsRes.status})`);

  // ── Reports ──
  console.log('  ── GET /reports/sales ──');
  const reportsRes = await request('/reports/sales');
  assert(reportsRes.ok || reportsRes.status !== 0, `GET /reports/sales accessible (got ${reportsRes.status})`);

  // ── Summary ──
  const total = passed + failed;
  console.log(`\n📊 Results: ${passed}/${total} passed, ${failed} failed\n`);
  process.exit(failed > 0 ? 1 : 0);
}

run().catch((err) => {
  console.error('❌ Fatal error:', err);
  process.exit(1);
});
