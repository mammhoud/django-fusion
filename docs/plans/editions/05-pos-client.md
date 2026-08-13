# pos-client Edition — Design, Architecture & Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the pos-client edition (`formintC/`) by documenting its design, architecture, and data model (the separate branch of the extension chain) and hardening it with shop-API test coverage and a green verification gate.

**Architecture:** A separate product branch, not an upgrade of formint-pos. Three layers in one package: a Vue 3 + Pinia desktop client (`src/` + `src-tauri/`, Rust/Diesel), a plain-Django purchase-app backend (`backend/`, `employee` + `shop` apps), and an Astro storefront (`frontend/`) served over django-fusion. The shop backend already implements the full cycle: catalog API, cart add/update/remove, checkout, `place_order`, order confirmation, my-orders, and the fusion render-mode contract.

**Tech Stack:** TypeScript (Vue 3, Pinia, vue-i18n, Astro 5), Rust (Tauri 2, Diesel), Python (Django 5.2, django-fusion), pytest, oxlint.

## Global Constraints

- All changes live under `projects/formints/formintC/` only.
- **No new dependencies.** Tests use Django's test client and stdlib only.
- Vue client port 1420; shop backend runs via `backend/manage.py`.
- Test commands: Django `cd projects/formints/formintC/backend && python -m pytest` · client `cd projects/formints/formintC && pnpm lint && pnpm build`.
- The shop backend is plain Django (no Ninja, no bolt) — do not introduce Ninja/bolt here.
- No Robyn.
- **Feature inheritance (branch exception):** pos-client is a separate branch, not a tier above Cloud — it does not inherit the Community → Standard → Pro → Cloud chain. Its feature set is self-contained (Vue client + Django shop); the parity rule applies downward only (Cloud inherits Pro, Pro inherits Standard, Standard inherits Community).

---

## Design

**Audience:** a small shop that wants a desktop client (menu, orders, settings) plus a web storefront with cart/checkout, all from one vendor package.

**What exists (verified):** `catalog_api`, `auth_status_api`, `products_fragment`, `cart_count_fragment`, `cart_drawer_fragment`, `cart_add/update/remove`, `CheckoutPageView`, `OrderConfirmationPageView`, `MyOrdersPageView`, `place_order`, and the fusion contract (`render_mode`, `branding`, `navigation`, `assets`). The Astro storefront (`pages/index.astro`) is "a single shop page: menu, cart, checkout, and order status".

**The gap this plan closes:** the shop API has **no test suite** — `backend/` ships no tests at all. That is the concrete completion item: lock the catalog/cart/auth contracts with Django test-client tests, then run the client's own lint/build gate.

**Copy register:** view names already follow the interface voice ("Order ahead, pick up fast."); tests keep endpoint names as-is.

## Architecture

```
Vue 3 client (src/ + src-tauri/)         Astro storefront (frontend/)
  Dashboard · Menu · Orders · Settings     index.astro → django-fusion fragments
  Pinia stores · vue-i18n (en/zh-CN)       HtmxBootstrap, CartDrawer, LoginModal
        │  Tauri commands (Rust/Diesel)            │  HTMX/JSON
        ▼                                          ▼
Django purchase-app (backend/)
  shop/     catalog_api · cart_* · checkout · place_order · Order/OrderItem
  employee/ employee + fusion components
```

Data flow: Vue client reads/writes its own Diesel SQLite; the storefront calls the Django shop over HTTP; `place_order` creates `Order` + `OrderItem` rows.

## Data model (separate branch — extends nothing upward)

Two independent stores:

| Layer | Entities | Notes |
|-------|----------|-------|
| Vue client (Rust/Diesel) | client-local tables | desktop app's own SQLite |
| Shop (Django, `backend/`) | `Category`, `Product`, `Cart`, `CartItem`, `Order`, `OrderItem` (+ `employee.Employee`) | catalog + cart + order lifecycle |

The shop schema is the branch's canonical data model — it does not reuse `pos_full`/`pos_cloud` tables.

---

## Task D1: Shop API test suite

**Files:**
- Create: `formintC/backend/tests/__init__.py`
- Create: `formintC/backend/tests/test_shop_api.py`
- Test runner: `cd projects/formints/formintC/backend && python -m pytest tests/ -q`

**Interfaces:**
- Consumes: `shop.views.{catalog_api, auth_status_api, cart_count_fragment}` (all exist).
- Produces: a repeatable regression suite for the shop API — consumed by the verification gate in Task D2.

- [ ] **Step 1: Write the failing test**

Create `formintC/backend/tests/__init__.py` (empty) and `formintC/backend/tests/test_shop_api.py`:

```python
import json

from django.test import TestCase
from django.urls import reverse

from shop.models import Category, Product


class CatalogApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Coffee")
        Product.objects.create(name="Latte", price="4.50", category=cat)

    def test_catalog_api_returns_products(self):
        resp = self.client.get(reverse("shop_catalog_api"))
        assert resp.status_code == 200
        payload = json.loads(resp.content)
        names = [item.get("name") for item in payload.get("items", payload if isinstance(payload, list) else [])]
        assert "Latte" in names

    def test_catalog_api_empty_shop(self):
        Product.objects.all().delete()
        resp = self.client.get(reverse("shop_catalog_api"))
        assert resp.status_code == 200

    def test_auth_status_api_responds(self):
        resp = self.client.get(reverse("shop_auth_status_api"))
        assert resp.status_code == 200

    def test_cart_count_fragment_responds(self):
        resp = self.client.get(reverse("shop_cart_count_fragment"))
        assert resp.status_code == 200
```

> The `reverse()` names above assume the `name=` values in `shop/urls.py`. If the url names differ, read `formintC/backend/shop/urls.py` and use the actual names — keep the assertions (200 + JSON contains "Latte") unchanged.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintC/backend && python -m pytest tests/test_shop_api.py -q`
Expected: FAIL — `NoReverseMatch` (url names) or missing `tests` package. Fix the url names from `shop/urls.py` if needed, then confirm the failure is real (wrong/missing behavior), not a test bug.

- [ ] **Step 3: Adjust to the real contract (if the failure was only names)**

If Step 2 failed only on `reverse()` names, correct them in the test and re-run. Expected: the tests now pass against the existing views — this task is about locking the contract, not changing behavior.

If any assertion fails against real behavior (e.g., `catalog_api` does not return a JSON list/dict containing the product name), fix the smallest thing in `shop/views.py` that makes the contract match the storefront's usage and re-run.

- [ ] **Step 4: Run the full test suite**

Run: `cd projects/formints/formintC/backend && python -m pytest tests/ -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add projects/formints/formintC/backend/tests/
git commit -m "test(pos-client): shop API contract tests for catalog, auth status, cart"
```

---

## Task D2: Client verification gate

**Files:**
- No code changes unless a check fails.

- [ ] **Step 1: Run the Vue client lint + build**

Run: `cd projects/formints/formintC && pnpm lint && pnpm build`
Expected: oxlint passes; `vue-tsc && vite build` produces `dist/`.

- [ ] **Step 2: Run the storefront check**

Run: `cd projects/formints/formintC/frontend && pnpm build` (or the `astro check` equivalent in `frontend/package.json`)
Expected: build succeeds.

- [ ] **Step 3: Fix any failure found (only if a check fails)**

Fix the smallest code change that makes the failing check pass; re-run until green.

- [ ] **Step 4: Commit**

```bash
git add projects/formints/formintC/
git commit -m "test(pos-client): green verification gate (lint + build + shop API suite)"
```

---

## Task D3: pos-client docs parity

**Files:**
- Modify: `projects/formints/docs/architecture/editions.md` (pos-client section)
- Modify: `projects/formints/CHANGELOG.md`

- [ ] **Step 1: Confirm the pos-client section is accurate**

In `projects/formints/docs/architecture/editions.md`, the pos-client section must describe: Vue 3 client (4 views, en/zh-CN), Django purchase-app backend (shop + employee, 6 models), Astro storefront on django-fusion. Fix any line that contradicts the code.

- [ ] **Step 2: Add a CHANGELOG entry**

Under `## Unreleased`:

```markdown
### Added (pos-client — formintC)
- Shop API contract test suite (catalog, auth status, cart)
- Verification gate green: oxlint + vue build + Astro build
```

- [ ] **Step 3: Commit**

```bash
git add projects/formints/docs/architecture/editions.md projects/formints/CHANGELOG.md
git commit -m "docs: pos-client edition parity + changelog"
```

---

# Cross-cutting enhancements (pos-client)

## Task D4: Playwright e2e for the storefront

**Files:**
- Create: `formintC/playwright.config.ts`
- Create: `formintC/e2e/storefront.spec.ts`

**Interfaces:**
- Consumes: the shop backend (`backend/manage.py runserver`, catalog + cart endpoints from `shop/views.py`).
- Produces: a standalone pos-client e2e suite covering catalog render + add-to-cart.

- [ ] **Step 1: Write the config + spec**

Create `formintC/playwright.config.ts` (mirror `formintA/playwright.config.ts`, baseURL `http://127.0.0.1:8000` — the shop backend's dev port, or the port `backend/manage.py runserver` uses):

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: { baseURL: 'http://127.0.0.1:8000' },
});
```

Create `formintC/e2e/storefront.spec.ts`:

```ts
import { test, expect } from '@playwright/test';

test('storefront lists the catalog', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Latte')).toBeVisible();
});

test('adds an item to the cart', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /add|cart/i }).first().click();
  await expect(page.locator('[data-cart-count]')).toHaveText(/[1-9]/);
});
```

> Seed the shop first (`cd formintC/backend && python manage.py shell -c "from shop.models import Category, Product; c, _ = Category.objects.get_or_create(name='Coffee'); Product.objects.get_or_create(name='Latte', defaults={'price': '4.50', 'category': c})"`). Adjust selectors to match the storefront's actual markup if `data-cart-count` differs.

- [ ] **Step 2: Run the e2e suite**

Run: `cd projects/formints/formintC && pnpm exec playwright test`
Expected: PASS — both specs green.

- [ ] **Step 3: Commit**

```bash
git add formintC/playwright.config.ts formintC/e2e/
git commit -m "test(pos-client): Playwright e2e for the storefront catalog and cart"
```

## Task D5: django-fusion My Orders fragment

**Files:**
- Modify: `formintC/backend/shop/views.py` (add `my_orders_fragment` mirroring `products_fragment`)
- Modify: `formintC/backend/shop/urls.py` (wire `/fragments/my-orders/`)
- Test: `formintC/backend/tests/test_shop_api.py` (add fragment test)

**Interfaces:**
- Consumes: `Order`/`OrderItem` models, `MyOrdersPageView` (exists), the `products_fragment` pattern in `shop/views.py`.
- Produces: `my_orders_fragment(request)` — an HTMX fragment listing the current user's recent orders, rendered in the storefront drawer.

- [ ] **Step 1: Write the failing test**

Append to `formintC/backend/tests/test_shop_api.py`:

```python
def test_my_orders_fragment_responds(self):
    resp = self.client.get(reverse("shop_my_orders_fragment"))
    assert resp.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintC/backend && python -m pytest tests/test_shop_api.py -q`
Expected: FAIL — `NoReverseMatch` for `shop_my_orders_fragment`

- [ ] **Step 3: Write the fragment**

In `formintC/backend/shop/views.py`, add (mirroring the structure of `products_fragment`, using the same template directory and naming convention):

```python
def my_orders_fragment(request: HttpRequest):
    """HTMX fragment listing the current user's recent orders."""
    orders = Order.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(request, "shop/fragments/my_orders.html", {"orders": orders})
```

> If `Order` stores the customer differently (no `user` FK), filter on the field `MyOrdersPageView.get_context_data` uses — read `shop/views.py` ~line 222-242 and mirror its query.

In `formintC/backend/shop/urls.py`, next to the other fragment routes, add:

```python
path("fragments/my-orders/", my_orders_fragment, name="shop_my_orders_fragment"),
```

Create the template `formintC/backend/shop/templates/shop/fragments/my_orders.html` listing `{{ order.id }}`, `{{ order.total }}`, and status, following the markup style of the existing fragment templates.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd projects/formints/formintC/backend && python -m pytest tests/test_shop_api.py -q`
Expected: PASS — full shop suite green.

- [ ] **Step 5: Commit**

```bash
git add formintC/backend/shop/views.py formintC/backend/shop/urls.py formintC/backend/shop/templates/shop/fragments/my_orders.html formintC/backend/tests/test_shop_api.py
git commit -m "feat(pos-client): django-fusion My Orders fragment for the storefront"
```

---

## Self-Review

1. **Spec coverage:** pos-client's completion = contract coverage (D1) + verification gate (D2) + doc parity (D3). No capability markers remain for pos-client in `editions.md` (it never had any).
2. **Placeholder scan:** D1's conditional note (url names) names the exact file to read and keeps assertions fixed. No TBDs.
3. **Type consistency:** view names (`catalog_api`, `auth_status_api`, `cart_count_fragment`) match the verified `shop/views.py` function names; model names match `shop/models.py`.

## Execution Handoff

**Plan complete and maintained at `docs/plans/editions/05-pos-client.md`.** Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
