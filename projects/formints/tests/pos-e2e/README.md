# POS E2E Testing Guide

Shared Playwright E2E test suite for all POS editions: **full**, **solo**, **mini**, **client**, and **cloud**.

## Quick Start

```bash
# Install dependencies
cd projects/pos/pos-e2e
npm install
npx playwright install chromium

# Run all tests across all editions
npm run test:e2e

# Run tests for a specific edition
npm run test:e2e:full        # pos-full only
npm run test:e2e:solo        # pos-solo only
npm run test:e2e:mini        # pos-mini only

# Run only API tests (bolt pattern — no browser)
npm run test:api

# Interactive debugging
npm run test:e2e:ui

# View HTML report
npm run test:e2e:report
```

## Architecture

```
pos-e2e/
├── playwright.config.ts     # Central config with 5 Playwright projects
├── fixtures/
│   └── auth.ts              # Shared auth fixtures (mocks Fusion server + API)
├── pages/                   # Page Object Models (POMs)
│   ├── BasePage.ts          # Shared selectors: nav, layout, loading/error/empty
│   ├── HomePage.ts          # Dashboard page
│   ├── SalePage.ts          # POS sale/transaction page
│   ├── InventoryPage.ts     # Inventory management page
│   └── index.ts             # Barrel exports
├── helpers/
│   ├── api.ts               # API helpers for bolt-pattern testing
│   └── utils.ts             # Console error capture, Fusion fragment waiter
├── tests/
│   ├── e2e/                 # Browser-based tests (render first)
│   │   ├── auth.spec.ts     # Auth + role-based access
│   │   ├── home.spec.ts     # Dashboard smoke tests
│   │   ├── sale.spec.ts     # POS transaction interface
│   │   └── inventory.spec.ts # Inventory management
│   └── api/                 # API-only tests (bolt pattern)
│       └── pos-api.spec.ts  # Server health, auth, CRUD
└── README.md                # This file
```

## Two Testing Strategies

### 1. Render First (Browser E2E)

Tests navigate pages in a real Chromium browser. Use these for:
- UI layout and responsiveness
- User interactions (clicks, forms, navigation)
- Visual regression (screenshots)
- Cross-edition consistency

```ts
import { test, expect } from '../../fixtures/auth';
import { HomePage } from '../../pages';

test('dashboard renders', async ({ adminPage }) => {
  const home = new HomePage(adminPage);
  await home.goto();
  await expect(home.sideNav).toBeVisible();
});
```

### 2. Bolt Pattern (API E2E)

Tests call backend APIs directly — no browser. Use these for:
- Fast backend validation
- Auth token flows
- CRUD operation correctness
- Error handling (401, 403, 404)

```ts
import { test, expect } from '@playwright/test';
import { createApiContext, apiLogin } from '../../helpers/api';

test('login returns token', async () => {
  const ctx = await createApiContext();
  const { token } = await apiLogin(ctx);
  expect(token).toBeDefined();
});
```

## Auth Mocking

POS editions use a Fusion server (port 8765) and RTK Query API (port 8766). The test fixtures **mock** these services so tests run without a real backend.

```ts
// fixtures/auth.ts provides custom fixtures:
test('admin action', async ({ adminPage }) => { ... });
test('cashier action', async ({ cashierPage }) => { ... });
test('manager action', async ({ managerPage }) => { ... });
```

Each fixture mocks:
- `GET /fusion/health` → `{ status: 'ok' }`
- `GET /api/auth/status` → authenticated profile
- `GET /api/auth/me` → user profile

Mock users defined in `fixtures/auth.ts`:
| Fixture | Role | Permissions |
|---------|------|-------------|
| `adminPage` | admin | `*` (all) |
| `cashierPage` | cashier | `pos.sale`, `pos.inventory.view` |
| `managerPage` | manager | `pos.*`, `reports.*` |

## Adding a New Page Test

1. Create a Page Object Model in `pages/YourPage.ts`
2. Extend `BasePage` for shared selectors
3. Write tests in `tests/e2e/your-feature.spec.ts`

```ts
// pages/YourPage.ts
export class YourPage extends BasePage {
  readonly table;
  constructor(page: Page) {
    super(page);
    this.table = page.locator('table');
  }
  async goto() { await super.goto('/your-path'); }
}

// tests/e2e/your-feature.spec.ts
import { test, expect } from '../../fixtures/auth';
import { YourPage } from '../../pages';

test('your feature', async ({ adminPage }) => {
  const p = new YourPage(adminPage);
  await p.goto();
  await expect(p.table).toBeVisible();
});
```

## POS Editions

| Edition | Port | Pages | Notes |
|---------|:----:|:-----:|-------|
| `pos-full` | 1420 | 24 | Tauri + Redux, primary edition |
| `pos-solo` | 1421 | 24 | Robyn server variant |
| `pos-mini` | 1422 | 23 | No Redux, no Notes page |
| `pos-client` | 1423 | views | `views/` architecture instead of `pages/` |
| `pos-cloud` | 1424 | — | Scaffolded; tests skipped until `src/` is built |

## CI Integration

```yaml
# GitHub Actions example
- name: Install Playwright
  run: |
    cd projects/pos/pos-e2e
    npm ci
    npx playwright install chromium --with-deps

- name: Run E2E tests
  run: |
    cd projects/pos/pos-e2e
    npx playwright test --project=pos-full
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Tests timeout on `networkidle` | Increase timeout in `playwright.config.ts` |
| Server not mocked | Ensure `setupAuth()` is called in the fixture |
| Port conflict | Editions use strict ports (1420-1424). Kill existing dev servers first |
| `ERR_CONNECTION_REFUSED` | Dev server not started. Check `webServer` config |
| Role-based page shows wrong content | Check the fixture role matches the page's expected role |
