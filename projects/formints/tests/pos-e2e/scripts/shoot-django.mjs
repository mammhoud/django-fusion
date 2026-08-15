// Standalone screenshot harness for the Django-first Formint Pro server.
//
// Boots nothing itself — the daphne server must already be running on
// PRO_BASE (default http://127.0.0.1:8766). Captures the Unfold admin,
// Ninja API docs, and django-fusion fragment renders to
// projects/formints/docs/screenshots/django/.
//
// Usage:
//   node scripts/shoot-django.mjs

import { chromium } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const BASE = process.env.PRO_BASE ?? 'http://127.0.0.1:8766';
const OUT = process.env.SHOOT_DIR ?? join(__dirname, '..', '..', '..', 'docs', 'screenshots', 'django');
mkdirSync(OUT, { recursive: true });

const EMAIL = process.env.FORMINT_ADMIN_EMAIL ?? 'admin@formint.local';
const PASSWORD = process.env.FORMINT_ADMIN_PASSWORD ?? 'admin123';

const browser = await chromium.launch({
  headless: true,
  args: [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--no-zygote',
    '--disable-gpu',
    '--disable-software-rasterizer',
  ],
});
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

async function shoot(name, path = '/') {
  await page.goto(BASE + path, { waitUntil: 'networkidle' }).catch(() => {});
  await page.screenshot({ path: join(OUT, `${name}.png`), fullPage: false });
  console.log(`✓ ${name}.png`);
}

try {
  // 1. Admin login (Unfold dark theme)
  await shoot('admin-login', '/admin/login/');

  // 2. Admin dashboard (KPI cards via pos_dashboard_callback)
  await page.goto(BASE + '/admin/login/', { waitUntil: 'networkidle' }).catch(() => {});
  const usernameField = page.locator('input[name="username"]');
  if ((await usernameField.count()) > 0) {
    await usernameField.fill(EMAIL);
    await page.locator('input[name="password"]').fill(PASSWORD);
    await Promise.all([
      page.waitForURL('**/admin/**', { timeout: 15000 }).catch(() => {}),
      page.locator('button[type="submit"]').click(),
    ]);
    await page.waitForTimeout(1500);
    await page.screenshot({ path: join(OUT, 'admin-dashboard.png') });
    console.log('✓ admin-dashboard.png');
  } else {
    console.log('⚠ admin login form not found — skipping dashboard');
  }

  // 3. Ninja API docs (Swagger)
  await shoot('api-docs', '/api/v1/docs');

  // 4. django-fusion fragment render (dashboard)
  await shoot('fusion-dashboard', '/fusion/render/dashboard');

  // 5. django-fusion fragment render (suppliers)
  await shoot('fusion-suppliers', '/fusion/render/suppliers');

  // 6. Server stats (JSON text)
  await shoot('stats', '/stats');

  // 7. KDS stations (JSON text)
  await shoot('kds-stations', '/kds/stations/');
} finally {
  await browser.close();
}
console.log(`\nSaved ${OUT}`);
