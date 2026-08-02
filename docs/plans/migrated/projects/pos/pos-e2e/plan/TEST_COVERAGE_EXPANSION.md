# POS E2E — Test Coverage Expansion Plan

> **Plan file:** `projects/pos/pos-e2e/plan/TEST_COVERAGE_EXPANSION.md`
> **Created:** 2026-07-25 | **Branch:** `generic`

---

## Overview

The POS E2E suite currently has 21 Page Object Models but minimal actual test
files (`tests/api/pos-api.spec.ts` with `test.skip`). This plan expands test
coverage across all POS editions.

---

## Phase 1 — API Tests (Bolt Pattern — No Browser)

### 1.1 Health Check Tests

```typescript
// tests/api/sidecar-health.spec.ts
test.describe('Sidecar Health', () => {
  test('GET /fusion/health returns preference', async ({ request }) => { ... });
  test('GET /api/products returns 200', async ({ request }) => { ... });
  test('GET /api/categories returns 200', async ({ request }) => { ... });
  test('GET /api/customers returns 200', async ({ request }) => { ... });
});
```

### 1.2 CRUD API Tests

| Resource | Tests | Endpoints |
|----------|:-----:|-----------|
| Products | 6 | GET list/detail, POST create, PUT update, DELETE, search |
| Categories | 3 | GET list, POST create, PUT update |
| Customers | 5 | GET list/detail, POST create, PUT update, DELETE |
| Sales | 4 | GET list/detail, POST create, GET items |
| Inventory | 3 | GET ingredients, GET transactions, POST adjustment |
| Employees | 5 | GET list/detail, POST create, PUT update, DELETE |
| Settings | 2 | GET settings, PUT update |

**Total API tests:** ~28 per edition × 2 editions (pos-full, pos-solo) = 56 tests

---

## Phase 2 — Flow Tests (Browser Required)

### 2.1 Sale Flow

```typescript
// tests/flows/sale-flow.spec.ts
test.describe('Complete Sale Flow', () => {
  test('POS Full — Dine-in sale from product search to checkout');
  test('POS Full — Takeaway sale with custom quantity');
  test('POS Full — Delivery sale with address');
  test('POS Solo — Simple product add + checkout');
  test('POS Mini — Product add + checkout (no sidecar)');
});
```

### 2.2 Product Manager Flow

```typescript
// tests/flows/product-manager-flow.spec.ts
test.describe('Product Management', () => {
  test('Create product with custom border color');
  test('Edit product price and category');
  test('Delete product with confirmation');
  test('Search and filter products');
  test('Verify border_color column exists (migration applied)');
});
```

### 2.3 Employee Flow (POS Full Only)

```typescript
// tests/flows/employee-flow.spec.ts
test.describe('Employee Management', () => {
  test('Add employee with type and salary');
  test('Filter by type and status');
  test('Edit employee details');
  test('Deactivate employee');
  test('Add custom employee type');
});
```

### 2.4 Inventory Flow

```typescript
// tests/flows/inventory-flow.spec.ts
test.describe('Inventory Management', () => {
  test('View ingredient list with stock levels');
  test('Add inventory transaction');
  test('Manual adjustment');
  test('Low stock warning visible');
});
```

### 2.5 Auth Flow

```typescript
// tests/flows/auth-flow.spec.ts
test.describe('Authentication', () => {
  test('Login with valid credentials');
  test('Login fails with wrong password');
  test('Register new account');
  test('Verify email code');
});
```

**Total flow tests:** ~25 tests

---

## Phase 3 — Visual Regression Tests

### 3.1 Theme Regression

```typescript
// tests/visual/theme-regression.spec.ts
test.describe('CTC Teal Theme — Visual Regression', () => {
  const PAGES = [
    '/sale', '/customers', '/employees', '/analytics',
    '/reports', '/inventory', '/recipes', '/settings',
    '/roles', '/payroll', '/kitchen', '/transactions',
  ];

  for (const route of PAGES) {
    test(`${route} — no indigo/purple classes`, async ({ page }) => {
      await page.goto(route);
      const indigoCount = await page.locator('[class*="indigo-"]').count();
      const purpleCount = await page.locator('[class*="purple-"]').count();
      expect(indigoCount + purpleCount).toBe(0);
    });
  }
});
```

### 3.2 Screenshot Snapshots

```typescript
test('Dashboard page screenshot', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('pos-home.png', { fullPage: true });
});
```

---

## Phase 4 — CI Integration

Already done — `pos-e2e` job in `.github/workflows/js-test.yml` runs API tests.

Expand CI to run flow tests when a display is available:

> **Note:** Flow tests require a Tauri window (browser + dev server).
> In CI, Tauri can't render a display without `xvfb-run`.
> API tests (bolt pattern) are CI-safe — they use Playwright's `request` fixture.

```yaml
pos-e2e-flow:
  runs-on: ubuntu-latest
  if: github.event_name == 'pull_request'
  steps:
    - uses: actions/checkout@v4
    - name: Run flow tests (with virtual display)
      working-directory: projects/pos/pos-e2e
      run: |
        npx playwright install chromium --with-deps
        xvfb-run --auto-servernum npx playwright test tests/flows/ --project=pos-full
```

---

## Test Matrix

| Edition | API Tests | Flow Tests | Visual Tests | CI |
|---------|:---------:|:----------:|:------------:|:--:|
| pos-full | ✅ 28 planned | ✅ 15 planned | ✅ 12 planned | ✅ API done |
| pos-solo | ✅ 28 planned | ✅ 5 planned | ✅ 8 planned | ❌ |
| pos-mini | ❌ N/A (no API) | ✅ 3 planned | ✅ 5 planned | ❌ |

---

## POM Usage in Tests

All flow tests use the Page Object Models created in `pages/`:

```typescript
import { SalePage, CustomersPage, EmployeesPage } from '../pages';

test('Complete sale flow', async ({ page }) => {
  const salePage = new SalePage(page);
  await salePage.goto();
  await salePage.selectDineIn();
  await salePage.addProductToCart('Espresso');
  await salePage.checkout();
});
```

---

## Progress

| Phase | Tests Planned | Status | Effort |
|-------|:------------:|:------:|:------:|
| 1 — API Tests | 56 | 🟡 | 4h |
| 2 — Flow Tests | 25 | ⬜ | 6h |
| 3 — Visual Regression | 20 | ⬜ | 2h |
| 4 — CI Integration | 1 job | ✅ | 1h |

**Total:** ~90 tests, ~13 hours