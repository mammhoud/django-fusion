/**
 * Formint Client — full-stack end-to-end tests.
 *
 * Runs against the live stack served through the Astro dev proxy (:4322 →
 * Django :8075), so every assertion exercises the real integration: HTMX
 * fragments, the cart session, django-fusion endpoints, the allauth headless
 * login (including the CSRF token that Alpine now sends), the POS JSON APIs
 * (/api/catalog/, /api/orders/) and the CORS headers the Vue client relies
 * on when it calls the portal cross-origin.
 *
 * Usage:  cd frontend && pnpm test          (stack must be running)
 *         make e2e                          (boots the stack itself)
 */
import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

const BASE = process.env.E2E_BASE_URL || 'http://127.0.0.1:4322';

// ── Tiny cookie jar (login rotates the session + CSRF token) ───────────────
let cookies = new Map();

function storeCookies(res) {
  const setCookies = res.headers.getSetCookie?.() ?? [];
  if (!setCookies.length) {
    const raw = res.headers.get('set-cookie');
    if (raw) {
      setCookies.push(raw);
    }
  }
  for (const sc of setCookies) {
    const [pair] = sc.split(';');
    const idx = pair.indexOf('=');
    if (idx === -1) {
      continue;
    }
    cookies.set(pair.slice(0, idx).trim(), pair.slice(idx + 1).trim());
  }
}

function cookieHeader() {
  return [...cookies.entries()].map(([k, v]) => `${k}=${v}`).join('; ');
}

function csrfToken() {
  return cookies.get('csrftoken') || '';
}

async function request(path, { method = 'GET', headers = {}, body } = {}) {
  const init = {
    method,
    redirect: 'manual',
    headers: {
      // Close connections so the node --test runner can exit promptly.
      Connection: 'close',
      ...(cookieHeader() ? { Cookie: cookieHeader() } : {}),
      ...headers,
    },
  };
  if (body !== undefined) {
    init.body = body;
  }
  const res = await fetch(`${BASE}${path}`, init);
  storeCookies(res);
  return res;
}

const text = (res) => res.text();
const hx = { 'HX-Request': 'true' };
const json = { Accept: 'application/json' };

// ── Storefront (Astro SSR + seeded fallback catalog) ──────────────────────
describe('storefront', () => {
  test('homepage renders the seeded café', async () => {
    const res = await request('/');
    assert.equal(res.status, 200);
    const html = await text(res);
    assert.match(html, /Formint Café/);
    assert.match(html, /Espresso/);
    // Category pills from the catalog (Tea/Smoothies/Desserts added by seed).
    assert.match(html, />\s*Tea\s*<\/button>/);
    assert.match(html, />\s*Smoothies\s*<\/button>/);
    assert.match(html, />\s*Desserts\s*<\/button>/);
    // Footer version line from the fusion site contract.
    assert.match(html, /Fusion/);
  });

  test('fusion site contract endpoints respond', async () => {
    const nav = await request('/fusion/navigation/');
    assert.equal(nav.status, 200);
    const navBody = await nav.json();
    assert.equal(navBody.brand.label, 'Formint Café');
    assert.ok(Array.isArray(navBody.modules));

    const branding = await request('/fusion/branding/');
    assert.equal(branding.status, 200);
    assert.equal((await branding.json()).site.name, 'Formint Café');

    const assets = await request('/fusion/assets/');
    assert.equal(assets.status, 200);
    assert.ok((await assets.json()).version, 'fusion assets version non-empty');

    const mode = await request('/fusion/render-mode/');
    assert.equal(mode.status, 200);
    assert.ok(['data-api', 'fusion-render'].includes((await mode.json()).mode));
  });
});

// ── HTMX fragments (cart grid, drawer, count) ──────────────────────────────
describe('htmx fragments', () => {
  test('product grid fragment swaps and filters by category', async () => {
    const all = await request('/shop/fragments/products/', { headers: hx });
    assert.equal(all.status, 200);
    assert.equal(all.headers.get('x-formintc-response-mode'), 'htmx-data-only');
    const grid = await text(all);
    assert.match(grid, /Espresso/);

    const tea = await request('/shop/fragments/products/?category=tea', { headers: hx });
    const teaGrid = await text(tea);
    assert.match(teaGrid, /Matcha Latte/);
    assert.doesNotMatch(teaGrid, /Espresso/);
  });

  test('fragments reject non-HTMX browsers', async () => {
    // GET fragments: rejected by the view's HTMX guard.
    const grid = await request('/shop/fragments/products/');
    assert.equal(grid.status, 406);
    // POST mutations: Django's CSRF middleware rejects them even earlier (403),
    // before the HTMX guard can answer 406.
    const add = await request('/shop/cart/add/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'product_id=1&quantity=1',
    });
    assert.equal(add.status, 403);
  });

  test('cart add/update/remove flow stays in sync', async () => {
    // Fresh session for an isolated cart.
    cookies = new Map();
    await request('/shop/fragments/products/', { headers: hx }); // seeds session + csrf
    const token = csrfToken();
    assert.ok(token, 'csrftoken cookie set by fragment response');

    const add = await request('/shop/cart/add/', {
      method: 'POST',
      headers: { ...hx, 'X-CSRFToken': token, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'product_id=1&quantity=1',
    });
    assert.equal(add.status, 200);
    assert.equal(add.headers.get('hx-trigger'), 'cartUpdated');
    const countBody = await text(add);
    assert.match(countBody, /data-cart-count="1"/);

    const add2 = await request('/shop/cart/add/', {
      method: 'POST',
      headers: { ...hx, 'X-CSRFToken': csrfToken(), 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'product_id=2&quantity=1',
    });
    assert.match(await text(add2), /data-cart-count="2"/);

    const drawer = await request('/shop/fragments/cart/drawer/', { headers: hx });
    const drawerHtml = await text(drawer);
    assert.match(drawerHtml, /Espresso/);
    assert.match(drawerHtml, /Flat White/);
    assert.match(drawerHtml, /Subtotal/);
    // Each line renders two update buttons (+/-), so dedupe the ids.
    const itemIds = [...new Set([...drawerHtml.matchAll(/shop\/cart\/update\/(\d+)\//g)].map((m) => m[1]))];
    assert.equal(itemIds.length, 2, 'drawer exposes both line-item ids');

    // Set the first line's quantity to 0 — the service deletes it.
    const update = await request(`/shop/cart/update/${itemIds[0]}/`, {
      method: 'POST',
      headers: { ...hx, 'X-CSRFToken': csrfToken(), 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'quantity=0',
    });
    assert.equal(update.status, 200);
    const afterUpdate = await text(update);
    assert.doesNotMatch(afterUpdate, /Espresso/);
    assert.match(afterUpdate, /Flat White/);

    // Remove the remaining line; the drawer shows its empty state.
    const remainingId = [...new Set([...afterUpdate.matchAll(/shop\/cart\/update\/(\d+)\//g)].map((m) => m[1]))];
    assert.equal(remainingId.length, 1, 'one line remains after the update');
    const remove = await request(`/shop/cart/remove/${remainingId[0]}/`, {
      method: 'POST',
      headers: { ...hx, 'X-CSRFToken': csrfToken(), 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    assert.match(await text(remove), /cart is empty/);

    const count = await request('/shop/fragments/cart/count/', { headers: hx });
    assert.match(await text(count), /data-cart-count="0"/);
  });
});

// ── POS API endpoints (Django portal JSON APIs) ────────────────────────────
describe('pos api endpoints (Django portal)', () => {
  test('/api/catalog/ returns the seeded catalog contract', async () => {
    const res = await request('/api/catalog/', { headers: json });
    assert.equal(res.status, 200);
    assert.match(res.headers.get('content-type') || '', /application\/json/);

    const data = await res.json();
    assert.equal(data.shop.name, 'Formint Café');
    assert.equal(typeof data.shop.tagline, 'string');
    assert.ok(Array.isArray(data.shop.order_types) && data.shop.order_types.length >= 3);

    assert.ok(data.categories.length >= 7, 'at least the 7 seeded categories');
    const slugs = new Set(data.categories.map((c) => c.slug));
    for (const expected of ['coffee', 'pastries', 'breakfast', 'lunch', 'tea', 'smoothies', 'desserts']) {
      assert.ok(slugs.has(expected), `category ${expected} seeded`);
    }

    assert.ok(data.products.length >= 24, 'at least the 24 seeded products');
    const featured = data.products.filter((p) => p.is_featured);
    assert.equal(featured.length, 14, 'seed marks the first 2 products of each category as featured');

    const espresso = data.products.find((p) => p.slug === 'espresso');
    assert.ok(espresso);
    assert.equal(espresso.price, '3.50', 'prices are decimal strings (safe across the wire)');
    assert.equal(espresso.category, 'coffee');
    assert.equal(espresso.unit, 'cup');
    assert.ok(Array.isArray(espresso.tags) && espresso.tags.length > 0);

    // compare_at_price promo field survives the serialization.
    const mocha = data.products.find((p) => p.slug === 'mocha');
    assert.equal(mocha?.compare_at_price, '5.80');
    // image_url from the seed is present on at least a few products.
    assert.ok(data.products.some((p) => p.image_url), 'seeded products carry image URLs');
  });

  test('/api/orders/<id>/ returns full customer + totals detail', async () => {
    const list = await request('/api/orders/', { headers: json });
    const { orders } = await list.json();
    assert.ok(orders.length >= 1, 'list has orders to look up');
    const first = orders[0];

    const res = await request(`/api/orders/${first.id}/`, { headers: json });
    assert.equal(res.status, 200);
    const detail = await res.json();
    assert.equal(detail.id, first.id);
    assert.equal(detail.reference, first.reference);
    assert.equal(detail.total_amount, first.total_amount);
    assert.ok(detail.customer_name);
    assert.equal(typeof detail.customer_email, 'string');
    assert.equal(typeof detail.customer_phone, 'string');
    assert.equal(typeof detail.notes, 'string');
    assert.match(detail.subtotal, /^\d+\.\d{2}$/);
    assert.match(detail.tax, /^\d+\.\d{2}$/);
    assert.ok(Array.isArray(detail.items) && detail.items.length >= 1);
    // Totals reconcile: subtotal + tax = total.
    assert.equal(Number(detail.subtotal) + Number(detail.tax), Number(detail.total_amount));

    // Unknown orders 404.
    const missing = await request('/api/orders/999999/', { headers: json });
    assert.equal(missing.status, 404);
  });

  test('/api/orders/ returns the seeded demo orders with line items', async () => {
    const res = await request('/api/orders/', { headers: json });
    assert.equal(res.status, 200);

    const data = await res.json();
    assert.ok(Array.isArray(data.orders));
    assert.ok(data.orders.length >= 3, 'at least the 3 seeded demo orders');
    assert.ok(data.orders.some((o) => o.status === 'completed'), 'a completed order exists');

    for (const o of data.orders) {
      assert.match(o.reference, /^[A-Z0-9]{6}$/, `reference ${o.reference} looks like an order ref`);
      assert.ok(['pending', 'confirmed', 'preparing', 'ready', 'completed', 'cancelled'].includes(o.status));
      assert.ok(['dine_in', 'takeaway', 'delivery'].includes(o.order_type));
      assert.equal(o.currency, '$');
      assert.match(o.total_amount, /^\d+\.\d{2}$/, 'total_amount is a decimal string');
      assert.ok(!Number.isNaN(Date.parse(o.created_at)), 'created_at parses as an ISO date');
      assert.ok(Array.isArray(o.items));
      for (const item of o.items) {
        assert.ok(item.product_name);
        assert.ok(item.quantity >= 1);
        assert.match(item.subtotal, /^\d+\.\d{2}$/);
      }
    }
  });
});

// ── CORS (django-cors-headers — the Vue client calls :8075 cross-origin) ───
describe('cors headers (django-cors-headers)', () => {
  const allowed = 'http://localhost:1420';

  test('allowed origin receives ACAO + credentials on catalog', async () => {
    const res = await request('/api/catalog/', { headers: { ...json, Origin: allowed } });
    assert.equal(res.status, 200);
    assert.equal(res.headers.get('access-control-allow-origin'), allowed);
    assert.equal(res.headers.get('access-control-allow-credentials'), 'true');
  });

  test('disallowed origin gets no ACAO header', async () => {
    const res = await request('/api/catalog/', {
      headers: { ...json, Origin: 'http://evil.example' },
    });
    assert.equal(res.status, 200);
    assert.equal(res.headers.get('access-control-allow-origin'), null);
  });

  test('POST preflight on /fusion/session-mode/ is allowed', async () => {
    const res = await request('/fusion/session-mode/', {
      method: 'OPTIONS',
      headers: {
        Origin: allowed,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type',
      },
    });
    // django-cors-headers answers successful preflights with 204 No Content.
    assert.ok([200, 204].includes(res.status), `preflight succeeded (got ${res.status})`);
    assert.equal(res.headers.get('access-control-allow-origin'), allowed);
    const methods = res.headers.get('access-control-allow-methods') || '';
    assert.match(methods, /POST/);
    assert.match(methods, /DELETE/);
  });
});

// ── Auth (allauth headless + CSRF) ─────────────────────────────────────────
describe('auth flow', () => {
  test('login without CSRF token is rejected (403)', async () => {
    cookies = new Map();
    await request('/shop/fragments/products/', { headers: hx });
    const res = await request('/api/auth/browser/v1/auth/login', {
      method: 'POST',
      headers: { ...json, 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'customer@formintcafe.example', password: 'coffee123' }),
    });
    assert.equal(res.status, 403);
  });

  test('login + logout with CSRF token succeeds', async () => {
    cookies = new Map();
    await request('/shop/fragments/products/', { headers: hx });

    const login = await request('/api/auth/browser/v1/auth/login', {
      method: 'POST',
      headers: { ...json, 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
      body: JSON.stringify({ email: 'customer@formintcafe.example', password: 'coffee123' }),
    });
    assert.equal(login.status, 200);
    assert.equal((await login.json()).meta.is_authenticated, true);

    const status = await request('/apis/auth/status/', { headers: json });
    assert.equal((await status.json()).authenticated, true);

    // Login rotated the CSRF token — re-read it from the cookie jar.
    const logout = await request('/api/auth/browser/v1/auth/session', {
      method: 'DELETE',
      headers: { ...json, 'X-CSRFToken': csrfToken() },
    });
    assert.equal(logout.status, 401); // 401 + is_authenticated:false = session destroyed
    assert.equal((await logout.json()).meta.is_authenticated, false);
  });
});
