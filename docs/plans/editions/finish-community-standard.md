# Finish Community, Standard & Cloud Editions — Implementation Plan

> **ARCHIVED / SUPERSEDED (14 Aug 2026):** This working file was split into the
> per-edition plans in [`docs/plans/editions/`](README.md) (`01-community.md`,
> `02-standard.md`, `03-pro.md`, `04-cloud.md`), which are now the canonical
> Formints plans and reference the current `formint-community`,
> `formint-standard`, `formint-pro`, and `formint-cloud` paths. The task code
> below is retained for history only — do not execute it; its retired
> `formintA/`, `formint/`, and `formintB/` paths no longer exist.
>
> **Note (9 Aug 2026):** this plan was split into per-edition plans with design, architecture, and data-model sections — see [`docs/plans/editions/`](README.md) (`01-community.md`, `02-standard.md`, `04-cloud.md`). **Part C (Cloud) was added here on request** and mirrors `04-cloud.md`. The task code below remains valid.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the last capability gaps in the Community (`formintA/`), Standard (merged into `formint/`), and Cloud (`formintB/`) POS editions so every feature the docs and landing site claim actually exists and is tested.

**Architecture:** Three independent subsystems, executed separately:
- **Part A — Community (`formintA/`):** Astro 5 + React 19 desktop app over Tauri 2 + Rust/Diesel (SQLite, `restaurant.db`). Work happens in Rust commands (`src-tauri/src/`) and React pages (`src/app/pages/`). Adds **refunds & returns** (Rust `refund_sale` command + UI) and an **offline-first mode** indicator.
- **Part B — Standard (gated tier inside `formint/sidecar/`):** full Django setup (Ninja + ninja-extra controllers, django-fusion, Unfold admin). Adds **multi-currency**, **tax profiles**, **custom roles & permissions enforcement**, and **CSV/JSON data export**.
- **Part C — Cloud (`formintB/backend/`, `pos-cloud`):** hosted multi-tenant SaaS master (apps/core + apps/domain + apps/handlers, Channels ASGI). Adds **automatic backups** (`BackupRun` model + `backup_db` management command) and **monitoring** (`/monitor/status` endpoint).

Parts A, B, and C never touch each other's files. Each part is independently testable.

**Tech Stack:** Rust (diesel 2.2, tauri 2), TypeScript (React 19, Vitest), Python (Django 5.2, ninja-extra, channels, pytest). No new third-party dependencies are required for any task (Cloud backups use stdlib `sqlite3`).

**Canonical path:** `docs/plans/editions/finish-community-standard.md`

## Global Constraints

- **Edition boundaries (hard):** Community work lives ONLY under `projects/formints/formintA/`. Standard work lives ONLY under `projects/formints/formint/sidecar/`. Cloud work lives ONLY under `projects/formints/formintB/backend/`. Never edit another subsystem in the same task.
- **No new runtime dependencies.** Rust uses only diesel + diesel_migrations (already in `formintA/src-tauri/Cargo.toml`); Django uses only stdlib `csv`/`json`/`sqlite3` + existing packages.
- **No Robyn.** The Django sidecar is the only server. Never reintroduce `server.py`/`routes/` Robyn files.
- **Version/ports stay unchanged:** Community Tauri port 1420 · Pro backend 8767 / frontend 4321 / bolt 8766 · Cloud API 8767 / admin 8082.
- **Naming conventions (copy verbatim):** Pro/Standard Django models use `app_label = "pos_full"`, `db_table = "full_<name>"`, and the sync-tracking fields `is_synced` / `synced_at` / `sync_status` (choices `pending|synced|failed`). Cloud models mirror `apps/core/models.py` (plain `class Meta`, Django infers `app_label="core"`). Tauri commands are snake_case (`refund_sale`).
- **Test commands:** Community Rust: `cd projects/formints/formintA/src-tauri && cargo test`. Community frontend: `cd projects/formints/formintA && pnpm test`. Standard: `cd projects/formints/formint/sidecar && make test` (runs `pytest tests/ -q -k "not rust_db"`). Cloud: `cd projects/formints/formintB/backend && make test`.
- **Migrations:** generated with `python manage.py makemigrations <app>` then applied with `make migrate` (sidecar: `pos_full`; cloud: `core`).
- **AGPL-3.0** license; keep existing file headers and docstring style.
- **Docs sync:** every completed feature removes its `(… capability, landing sync Aug 2026)` marker from `docs/architecture/editions.md` and adds a CHANGELOG entry.

---

# PART A — Community (`formintA/`): refunds & returns + offline-first

## Task A1: Rust `refund_sale` command

**Files:**
- Modify: `formintA/src-tauri/src/operations/sales.rs` (add `refund_sale` + inline test module)
- Modify: `formintA/src-tauri/src/lib.rs` (register the command in `invoke_handler`)

**Interfaces:**
- Consumes: `crate::db::{models::*, open_conn}`, `crate::db::schema::sales::dsl`, `crate::db::run_migrations` (all exist; see `operations/sales.rs` and `db/mod.rs`).
- Produces: `pub fn refund_sale(db_path: &PathBuf, sale_id: i32) -> Result<Sale, String>` — later consumed by Task A2's UI via `invoke('refund_sale', { saleId })`.

- [ ] **Step 1: Write the failing test**

Append this module to `formintA/src-tauri/src/operations/sales.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    /// Unique temp DB per test — tests run in parallel and WAL switching needs
    /// exclusive access (same pattern as `db/mod.rs` tests).
    fn temp_db_path(tag: &str) -> std::path::PathBuf {
        let mut path = std::env::temp_dir();
        path.push(format!("formint-pos-refund-test-{}-{}.db", std::process::id(), tag));
        let _ = std::fs::remove_file(&path);
        crate::db::run_migrations(&path).expect("migrations should succeed");
        path
    }

    fn seed_sale(db_path: &PathBuf) -> Sale {
        add_sale(
            db_path,
            NewSale {
                total_amount: 25.0,
                currency: "USD".to_string(),
                date: None,
                time: None,
                order_type: "dine_in".to_string(),
                status: "completed".to_string(),
                table_number: Some(1),
                delivery_type_id: None,
                delivery_zone_id: None,
                delivery_address: None,
                employee_id: None,
                customer_id: None,
                discount_code: None,
                discount_amount: 0.0,
                payment_method: "cash".to_string(),
            },
            vec![],
        )
        .expect("add_sale should succeed")
        .0
    }

    #[test]
    fn refund_sale_marks_sale_refunded() {
        let db_path = temp_db_path("ok");
        let sale = seed_sale(&db_path);
        let refunded = refund_sale(&db_path, sale.id).expect("refund should succeed");
        assert_eq!(refunded.status, "refunded");
        let _ = std::fs::remove_file(&db_path);
    }

    #[test]
    fn refund_sale_rejects_double_refund() {
        let db_path = temp_db_path("double");
        let sale = seed_sale(&db_path);
        refund_sale(&db_path, sale.id).expect("first refund should succeed");
        let err = refund_sale(&db_path, sale.id).expect_err("second refund must fail");
        assert!(err.contains("already refunded"), "unexpected error: {err}");
        let _ = std::fs::remove_file(&db_path);
    }

    #[test]
    fn refund_sale_rejects_missing_sale() {
        let db_path = temp_db_path("missing");
        let err = refund_sale(&db_path, 999_999).expect_err("missing sale must fail");
        assert!(err.contains("not found"), "unexpected error: {err}");
        let _ = std::fs::remove_file(&db_path);
    }
}
```

> If `add_sale` with an empty `items` vec fails in your checkout (kitchen-ticket creation), seed the sale with a single `NewSaleItem` constructed exactly as in `Sale.tsx` (fields: `product_id`, `quantity`, `unit_price`, `name` — confirm against `db::models::NewSaleItem` at `models.rs` around line 251).

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintA/src-tauri && cargo test refund_sale`
Expected: FAIL — `error[E0425]: cannot find function 'refund_sale' in this scope`

- [ ] **Step 3: Write the minimal implementation**

Add after the existing `update_sale` function in `formintA/src-tauri/src/operations/sales.rs`:

```rust
/// Mark a sale as refunded. The `status` column already exists on `sales`
/// and accepts "refunded" — no schema change is required. A sale can only
/// be refunded once.
pub fn refund_sale(db_path: &PathBuf, sale_id: i32) -> Result<Sale, String> {
    let mut conn = open_conn(db_path)?;
    use crate::db::schema::sales::dsl::*;

    let sale: Sale = sales
        .filter(id.eq(sale_id))
        .first(&mut conn)
        .map_err(|e| format!("sale {sale_id} not found: {e}"))?;
    if sale.status == "refunded" {
        return Err(format!("sale {sale_id} is already refunded"));
    }

    diesel::update(sales.filter(id.eq(sale_id)))
        .set(status.eq("refunded"))
        .returning(Sale::as_returning())
        .get_result(&mut conn)
        .map_err(|e| format!("failed to refund sale {sale_id}: {e}"))
}
```

- [ ] **Step 4: Register the command in the Tauri handler**

In `formintA/src-tauri/src/lib.rs`, find the existing `invoke_handler` (the `tauri::generate_handler![...]` list that already contains `add_sale`, `update_sale`, `delete_sale`, `get_sales`). Add `refund_sale` to that list, e.g.:

```rust
tauri::generate_handler![
    // ... existing commands ...
    refund_sale,
]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formintA/src-tauri && cargo test refund_sale`
Expected: PASS — `test result: ok. 3 passed`

- [ ] **Step 6: Run the full Rust suite**

Run: `cd projects/formints/formintA/src-tauri && cargo test`
Expected: all tests pass (existing + 3 new). Fix any unrelated pre-existing failures before committing only if they were caused by this change.

- [ ] **Step 7: Commit**

```bash
git add projects/formints/formintA/src-tauri/src/operations/sales.rs projects/formints/formintA/src-tauri/src/lib.rs
git commit -m "feat(formintA): refund_sale command marks a sale refunded (idempotent)"
```

---

## Task A2: Refund & return UI (Transactions page)

**Files:**
- Modify: `formintA/src/app/pages/pos/Transactions.tsx` (add Refund action)
- Test: `formintA/src/test/pages/Transactions.test.tsx` (create if missing — mirror `src/test/pages/Sale.test.tsx` structure)

**Interfaces:**
- Consumes: `refund_sale(db_path, sale_id)` from Task A1 (via `invoke('refund_sale', { saleId })`).
- Produces: A `handleRefund(sale)` function and a `Refunded` status chip reused by the receipt flow.

- [ ] **Step 1: Write the failing test**

Create `formintA/src/test/pages/Transactions.test.tsx` (adjust imports to match `Sale.test.tsx` conventions in the same folder):

```tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Transactions from '@/app/pages/pos/Transactions';
import { invoke } from '@tauri-apps/api/core';

vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));

const mockSales = [
  {
    id: 1,
    total_amount: 25,
    currency: 'USD',
    date: '2026-08-01',
    time: '12:00',
    order_type: 'dine_in',
    status: 'completed',
    payment_method: 'cash',
  },
];

beforeEach(() => {
  vi.mocked(invoke).mockReset();
  vi.mocked(invoke).mockImplementation(async (cmd: string) => {
    if (cmd === 'get_sales') return mockSales;
    if (cmd === 'refund_sale') return { ...mockSales[0], status: 'refunded' };
    throw new Error(`unexpected command ${cmd}`);
  });
});

describe('Transactions refund flow', () => {
  it('refunds a completed sale and refreshes the list', async () => {
    render(<Transactions />);
    await waitFor(() => expect(screen.getByText('25')).toBeTruthy());

    const refundButton = await screen.findByRole('button', { name: /refund/i });
    await userEvent.click(refundButton);
    const confirm = await screen.findByRole('button', { name: /confirm refund/i });
    await userEvent.click(confirm);

    await waitFor(() =>
      expect(vi.mocked(invoke)).toHaveBeenCalledWith('refund_sale', { saleId: 1 }),
    );
    await waitFor(() => expect(screen.getByText(/refunded/i)).toBeTruthy());
  });

  it('does not offer refund for an already refunded sale', async () => {
    vi.mocked(invoke).mockImplementation(async (cmd: string) => {
      if (cmd === 'get_sales') return [{ ...mockSales[0], status: 'refunded' }];
      throw new Error(`unexpected command ${cmd}`);
    });
    render(<Transactions />);
    await waitFor(() => expect(screen.getByText(/refunded/i)).toBeTruthy());
    expect(screen.queryByRole('button', { name: /refund/i })).toBeNull();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintA && pnpm vitest run src/test/pages/Transactions.test.tsx`
Expected: FAIL — no refund button rendered (or file/module resolution error, which is fine at this stage)

- [ ] **Step 3: Implement the refund action in Transactions.tsx**

In `formintA/src/app/pages/pos/Transactions.tsx`:
1. Add imports if missing: `import { invoke } from '@tauri-apps/api/core';`
2. After the sales-list state, add the refund handler and confirm dialog state:

```tsx
const [refundTarget, setRefundTarget] = useState<Sale | null>(null);
const [refunding, setRefunding] = useState(false);

const handleRefund = async () => {
  if (!refundTarget) return;
  setRefunding(true);
  try {
    await invoke('refund_sale', { saleId: refundTarget.id });
    await refreshSales(); // existing loader used after add_sale/delete_sale
    setRefundTarget(null);
  } finally {
    setRefunding(false);
  }
};
```

3. In the row rendering, only for `sale.status === 'completed'`, render a Refund button next to the existing actions:

```tsx
{sale.status === 'completed' && (
  <button
    type="button"
    className="btn btn-sm btn-outline"
    onClick={() => setRefundTarget(sale)}
  >
    Refund
  </button>
)}
```

4. Render a confirm dialog when `refundTarget` is set (reuse the existing `ConfirmDialog` from `@/components/ui`):

```tsx
{refundTarget && (
  <ConfirmDialog
    title="Refund sale"
    description={`Refund sale #${refundTarget.id} for $${refundTarget.total_amount}?`}
    confirmLabel={refunding ? 'Refunding…' : 'Confirm refund'}
    onConfirm={handleRefund}
    onCancel={() => setRefundTarget(null)}
  />
)}
```

5. Render the status with a `refunded` chip: map `sale.status` values (`pending`, `completed`, `refunded`, `cancelled`) to badges, and style `refunded` distinctly (e.g., amber outline).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd projects/formints/formintA && pnpm vitest run src/test/pages/Transactions.test.tsx`
Expected: PASS — both tests green

- [ ] **Step 5: Run the full frontend suite**

Run: `cd projects/formints/formintA && pnpm test`
Expected: all existing tests still pass

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formintA/src/app/pages/pos/Transactions.tsx projects/formints/formintA/src/test/pages/Transactions.test.tsx
git commit -m "feat(formintA): refund action on the Transactions page with confirm dialog"
```

---

## Task A3: Offline-first mode indicator

**Files:**
- Create: `formintA/src/hooks/useOfflineMode.ts`
- Modify: `formintA/src/components/AppShell.tsx` (render the banner)
- Test: `formintA/src/test/hooks/useOfflineMode.test.ts`

**Interfaces:**
- Produces: `export function useOfflineMode(): boolean` — `true` while the device is offline (or before first online event). Consumed by `AppShell.tsx`.

- [ ] **Step 1: Write the failing test**

Create `formintA/src/test/hooks/useOfflineMode.test.ts`:

```ts
import { describe, it, expect, vi, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useOfflineMode } from '@/hooks/useOfflineMode';

function setOnline(value: boolean) {
  Object.defineProperty(window.navigator, 'onLine', {
    configurable: true,
    value,
  });
  window.dispatchEvent(new Event(value ? 'online' : 'offline'));
}

describe('useOfflineMode', () => {
  afterEach(() => {
    setOnline(true);
    vi.restoreAllMocks();
  });

  it('returns false when the device is online', () => {
    setOnline(true);
    const { result } = renderHook(() => useOfflineMode());
    expect(result.current).toBe(false);
  });

  it('returns true when the device goes offline', () => {
    setOnline(true);
    const { result } = renderHook(() => useOfflineMode());
    act(() => setOnline(false));
    expect(result.current).toBe(true);
  });

  it('returns false again when back online', () => {
    setOnline(true);
    const { result } = renderHook(() => useOfflineMode());
    act(() => setOnline(false));
    act(() => setOnline(true));
    expect(result.current).toBe(false);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintA && pnpm vitest run src/test/hooks/useOfflineMode.test.ts`
Expected: FAIL — cannot find module `@/hooks/useOfflineMode`

- [ ] **Step 3: Write the hook**

Create `formintA/src/hooks/useOfflineMode.ts`:

```ts
import { useEffect, useState } from 'react';

/**
 * True while the device is offline (or before the first online event).
 * Community is offline-first by design — this surfaces that state in the UI.
 */
export function useOfflineMode(): boolean {
  const [offline, setOffline] = useState(
    () => typeof navigator !== 'undefined' && !navigator.onLine,
  );

  useEffect(() => {
    const goOffline = () => setOffline(true);
    const goOnline = () => setOffline(false);
    window.addEventListener('offline', goOffline);
    window.addEventListener('online', goOnline);
    return () => {
      window.removeEventListener('offline', goOffline);
      window.removeEventListener('online', goOnline);
    };
  }, []);

  return offline;
}
```

- [ ] **Step 4: Render the banner in AppShell**

In `formintA/src/components/AppShell.tsx` (the layout shell component): import the hook and render a fixed, non-blocking banner at the top of the layout when offline:

```tsx
import { useOfflineMode } from '@/hooks/useOfflineMode';

const offline = useOfflineMode();

// inside the returned layout, above the main content:
{offline && (
  <div className="pointer-events-none fixed inset-x-0 top-0 z-40 flex justify-center pt-3">
    <span className="rounded-full border border-amber-300/60 bg-amber-50/90 px-3 py-1 text-xs font-medium text-amber-800 shadow-sm">
      Offline mode — data stays on this device
    </span>
  </div>
)}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formintA && pnpm vitest run src/test/hooks/useOfflineMode.test.ts && pnpm test`
Expected: PASS — hook tests green, full suite still green

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formintA/src/hooks/useOfflineMode.ts projects/formints/formintA/src/components/AppShell.tsx projects/formints/formintA/src/test/hooks/useOfflineMode.test.ts
git commit -m "feat(formintA): offline-first mode indicator in the app shell"
```

---

# PART B — Standard (gated tier in `formint/sidecar/`): money, tax, roles, export

> All Part B tasks share this pattern for adding a model: create the domain file under `models/`, register it in `models/models.py`, expose it via `formint/models` re-exports (the import list at the top of `formint/controllers.py`), generate a migration, and register admin.

## Task B1: Multi-currency support

**Files:**
- Create: `formint/sidecar/models/money.py`
- Modify: `formint/sidecar/models/models.py` (register `Currency`)
- Modify: `formint/sidecar/formint/controllers.py` (import + add to `ALL_CONTROLLERS`)
- Modify: `formint/sidecar/admin.py` (register if it uses explicit registrations)
- Test: `formint/sidecar/tests/test_currency.py`

**Interfaces:**
- Produces: `Currency` model (fields `code`, `name`, `symbol`, `exchange_rate`, `is_default`, `is_active` + standard sync/audit fields) and `CurrencyController` mounted at `/api/v1/currencies`. Consumed by Task B2 (tax rates per currency) and the frontend (currency picker on sale).

- [ ] **Step 1: Write the failing test**

Create `formint/sidecar/tests/test_currency.py` (mirror the import/DB setup of an existing test in `tests/`):

```python
import pytest
from django.test import TestCase

from models.money import Currency


class CurrencyModelTest(TestCase):
    def test_create_currency(self):
        c = Currency.objects.create(
            code="EUR", name="Euro", symbol="€", exchange_rate="0.92",
        )
        assert str(c) == "EUR (€)"
        assert c.is_active is True

    def test_only_one_default_currency(self):
        Currency.objects.create(code="USD", name="US Dollar", is_default=True)
        c2 = Currency.objects.create(code="EUR", name="Euro")
        c2.is_default = True
        c2.save()
        assert Currency.objects.filter(is_default=True).count() == 1
        assert Currency.objects.get(code="USD").is_default is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_currency.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'models.money'`

- [ ] **Step 3: Write the model**

Create `formint/sidecar/models/money.py`:

```python
"""Money models — multi-currency support (Standard tier)."""

from django.db import models


class Currency(models.Model):
    """ISO-4217 currency with an optional cross-rate to the default currency."""

    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=64)
    symbol = models.CharField(max_length=8, blank=True, default="")
    exchange_rate = models.DecimalField(
        max_digits=12, decimal_places=6, default=1,
        help_text="Rate relative to the default currency (1.0 = base).",
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Sync tracking (copy existing convention)
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_currencies"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} ({self.symbol})"

    def save(self, *args, **kwargs):
        # Enforce a single default currency.
        if self.is_default:
            Currency.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
```

- [ ] **Step 4: Register the model**

In `formint/sidecar/models/models.py`, add after the `crm` import:

```python
from models.money import Currency  # noqa: F401 — discovered by Django
```

In `formint/sidecar/formint/controllers.py`, add `Currency` to the `from formint.models import (...)` import list, and after the `ALL_CONTROLLERS = [` opening (around line 314) append the controller (mirror an existing simple controller class such as `CategoryController`):

```python
@api_controller("/currencies", tags=["currencies"])
class CurrencyController(ModelControllerBase):
    model_config = ModelConfig(
        model=Currency,
        allowed_routes=["list", "create", "retrieve", "update", "partial_update", "delete"],
    )
```

Then add `CurrencyController,` to the `ALL_CONTROLLERS` list.

In `formint/sidecar/admin.py`, register the model the same way other models are registered in that file (if it uses `admin.site.register(Model, ...)`, add `Currency`; if it auto-discovers, skip — verify with `make check`).

- [ ] **Step 5: Generate and apply the migration**

Run:
```bash
cd projects/formints/formint/sidecar
python manage.py makemigrations pos_full
make migrate
```
Expected: a new migration `models/migrations/0002_currency.py` is created and applied.

- [ ] **Step 6: Seed default currencies**

In `formint/sidecar/models/management/commands/seed_demo.py`, add a block that creates `USD` (default), `EUR`, `GBP`, `MAD` if the table is empty, matching the existing seed style:

```python
from models.money import Currency

if not Currency.objects.exists():
    Currency.objects.create(code="USD", name="US Dollar", symbol="$", is_default=True)
    Currency.objects.create(code="EUR", name="Euro", symbol="€", exchange_rate="0.92")
    Currency.objects.create(code="GBP", name="British Pound", symbol="£", exchange_rate="0.79")
    Currency.objects.create(code="MAD", name="Moroccan Dirham", symbol="DH", exchange_rate="9.90")
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_currency.py -q`
Expected: PASS — 2 tests green. Then run the full suite: `make test` — all green.

- [ ] **Step 8: Commit**

```bash
git add projects/formints/formint/sidecar/models/money.py projects/formints/formint/sidecar/models/models.py projects/formints/formint/sidecar/formint/controllers.py projects/formints/formint/sidecar/admin.py projects/formints/formint/sidecar/models/migrations/ projects/formints/formint/sidecar/models/management/commands/seed_demo.py projects/formints/formint/sidecar/tests/test_currency.py
git commit -m "feat(sidecar): multi-currency support with single-default enforcement"
```

---

## Task B2: Tax profiles

**Files:**
- Modify: `formint/sidecar/models/money.py` (add `TaxProfile`)
- Modify: `formint/sidecar/models/pos.py` (add `tax_profile` FK to `Product` and `Sale`)
- Modify: `formint/sidecar/models/models.py`, `formint/sidecar/formint/controllers.py`, `formint/sidecar/admin.py` (register)
- Test: `formint/sidecar/tests/test_tax_profile.py`

**Interfaces:**
- Produces: `TaxProfile` model (fields `name`, `rate`, `is_default`, `is_active` + standard fields) and a pure helper `compute_tax(subtotal: Decimal, rate: Decimal) -> Decimal` in `formint/sidecar/formint/tax.py`. Consumed by the API/sale flow and by Task B4's export of tax rates.

- [ ] **Step 1: Write the failing test**

Create `formint/sidecar/tests/test_tax_profile.py`:

```python
from decimal import Decimal

from django.test import TestCase

from models.money import TaxProfile
from models.pos import Product, Sale, SaleItem
from formint.tax import compute_tax


class TaxProfileTest(TestCase):
    def test_compute_tax(self):
        assert compute_tax(Decimal("100.00"), Decimal("0.15")) == Decimal("15.00")
        assert compute_tax(Decimal("99.99"), Decimal("0.00")) == Decimal("0.00")

    def test_default_profile(self):
        TaxProfile.objects.create(name="Standard", rate="0.15", is_default=True)
        TaxProfile.objects.create(name="Reduced", rate="0.07")
        reduced = TaxProfile.objects.get(name="Reduced")
        reduced.is_default = True
        reduced.save()
        assert TaxProfile.objects.filter(is_default=True).count() == 1

    def test_product_can_carry_tax_profile(self):
        profile = TaxProfile.objects.create(name="Standard", rate="0.15", is_default=True)
        product = Product.objects.create(name="Latte", price="4.50", tax_profile=profile)
        assert product.tax_profile.rate == Decimal("0.15")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_tax_profile.py -q`
Expected: FAIL — import errors for `TaxProfile`, `formint.tax`

- [ ] **Step 3: Write the model + helper**

Append to `formint/sidecar/models/money.py`:

```python
class TaxProfile(models.Model):
    """Named tax rate applied to sales (Standard tier). Rate is a fraction."""

    name = models.CharField(max_length=100, unique=True)
    rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0,
        help_text="Tax rate as a fraction, e.g. 0.15 = 15%",
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_synced = models.BooleanField(default=False, db_index=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20, default="pending",
        choices=[("pending", "Pending"), ("synced", "Synced"), ("failed", "Failed")],
    )

    class Meta:
        app_label = "pos_full"
        db_table = "full_tax_profiles"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({float(self.rate) * 100:.2f}%)"

    def save(self, *args, **kwargs):
        if self.is_default:
            TaxProfile.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
```

Create `formint/sidecar/formint/tax.py`:

```python
"""Tax helpers (Standard tier)."""

from decimal import Decimal, ROUND_HALF_UP


def compute_tax(subtotal: Decimal, rate: Decimal) -> Decimal:
    """Return the tax amount for a subtotal at the given fractional rate."""
    if rate <= 0:
        return Decimal("0.00")
    return (subtotal * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

- [ ] **Step 4: Wire the FK + registrations**

In `formint/sidecar/models/pos.py`:
- Add to the `Product` model (around line 38): `tax_profile = models.ForeignKey("pos_full.TaxProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")`.
- Add to the `Sale` model (after `tax_amount`): `tax_profile = models.ForeignKey("pos_full.TaxProfile", on_delete=models.SET_NULL, null=True, blank=True, related_name="sales")`.

In `models/models.py`, extend the `money` import: `from models.money import Currency, TaxProfile  # noqa: F401`.

In `formint/controllers.py`: import `TaxProfile`, add a `TaxProfileController` mirroring `CurrencyController` (route `/tax-profiles`), and append it to `ALL_CONTROLLERS`.

In `admin.py`: register `TaxProfile` the same way as `Currency` (Task B1, Step 4).

- [ ] **Step 5: Migrate**

Run:
```bash
cd projects/formints/formint/sidecar
python manage.py makemigrations pos_full
make migrate
```

- [ ] **Step 6: Seed defaults**

In `seed_demo.py`, next to the currency seed (Task B1, Step 6):

```python
from models.money import TaxProfile

if not TaxProfile.objects.exists():
    TaxProfile.objects.create(name="Standard", rate="0.15", is_default=True)
    TaxProfile.objects.create(name="Reduced", rate="0.07")
    TaxProfile.objects.create(name="Zero-rated", rate="0")
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_tax_profile.py tests/test_currency.py -q && make test`
Expected: PASS — new tests green, full suite green

- [ ] **Step 8: Commit**

```bash
git add projects/formints/formint/sidecar/models/money.py projects/formints/formint/sidecar/models/pos.py projects/formints/formint/sidecar/models/models.py projects/formints/formint/sidecar/formint/tax.py projects/formints/formint/sidecar/formint/controllers.py projects/formints/formint/sidecar/admin.py projects/formints/formint/sidecar/models/migrations/ projects/formints/formint/sidecar/models/management/commands/seed_demo.py projects/formints/formint/sidecar/tests/test_tax_profile.py
git commit -m "feat(sidecar): tax profiles with product/sale linkage and compute_tax helper"
```

---

## Task B3: Custom roles & permissions enforcement

**Files:**
- Create: `formint/sidecar/formint/permissions.py`
- Modify: `formint/sidecar/formint/controllers.py` (gate `CurrencyController` writes)
- Test: `formint/sidecar/tests/test_permissions.py`

**Interfaces:**
- Consumes: `models.extra.Role` (already exists with `permissions = JSONField`).
- Produces: `require_permission(perm: str)` decorator for ninja-extra controllers. Consumed by `CurrencyController` writes in this task and reusable for any future write route.

- [ ] **Step 1: Write the failing test**

Create `formint/sidecar/tests/test_permissions.py`:

```python
from django.contrib.auth.models import User
from django.test import TestCase

from models.extra import Role
from formint.permissions import resolve_permissions


class PermissionHelperTest(TestCase):
    def test_superuser_has_all_permissions(self):
        user = User.objects.create_superuser("boss", "boss@example.com", "pw")
        assert "can_manage_products" in resolve_permissions(user)

    def test_role_permissions_are_resolved(self):
        role = Role.objects.create(
            name="Cashier",
            permissions={"can_manage_products": False, "can_issue_refunds": True},
        )
        user = User.objects.create_user("cashier", "cashier@example.com", "pw")
        perms = resolve_permissions(user, role=role)
        assert "can_issue_refunds" in perms
        assert "can_manage_products" not in perms

    def test_plain_user_gets_empty_permissions(self):
        user = User.objects.create_user("guest", "guest@example.com", "pw")
        assert resolve_permissions(user) == set()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_permissions.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'formint.permissions'`

- [ ] **Step 3: Write the helper**

Create `formint/sidecar/formint/permissions.py`:

```python
"""Permission resolution for the Standard tier (custom roles & permissions)."""

from __future__ import annotations

from functools import wraps
from typing import Iterable

from ninja_extra import HttpError

from models.extra import Role

# Canonical permission keys (keep in sync with Role.permissions JSON usage).
ALL_PERMISSIONS = {"can_manage_products", "can_issue_refunds", "can_manage_inventory"}


def resolve_permissions(user, role: Role | None = None) -> set[str]:
    """Return the effective permission keys for a user.

    Superusers bypass role checks. A role's JSON ``permissions`` dict lists
    flags; keys whose value is truthy are granted.
    """
    if user.is_superuser:
        return set(ALL_PERMISSIONS)
    if role is None:
        return set()
    return {key for key, granted in (role.permissions or {}).items() if granted}


def require_permission(permission: str):
    """Controller decorator that 403s when the request user lacks a permission."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            perms = resolve_permissions(request.user, role=getattr(request, "role", None))
            if permission not in perms:
                raise HttpError(403, f"Missing permission: {permission}")
            return func(self, request, *args, **kwargs)

        return wrapper

    return decorator
```

- [ ] **Step 4: Gate a write route**

In `formint/sidecar/formint/controllers.py`, apply the decorator to `CurrencyController`'s create and update methods (the new controller from Task B1) as the reference enforcement point:

```python
from formint.permissions import require_permission

@api_controller("/currencies", tags=["currencies"])
class CurrencyController(ModelControllerBase):
    model_config = ModelConfig(
        model=Currency,
        allowed_routes=["list", "create", "retrieve", "update", "partial_update", "delete"],
    )

    @require_permission("can_manage_inventory")
    def create(self, request, payload):
        return super().create(request, payload)

    @require_permission("can_manage_inventory")
    def update(self, request, id, payload):
        return super().update(request, id, payload)
```

> Confirm the exact create/update method signatures for `ModelControllerBase` (ninja-extra) in this codebase by checking an existing overridden controller method — if the base signatures differ, adapt the wrapper to match (the decorator contract stays the same).

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_permissions.py -q && make test`
Expected: PASS — helper tests green, full suite green (controller route tests unaffected)

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formint/sidecar/formint/permissions.py projects/formints/formint/sidecar/formint/controllers.py projects/formints/formint/sidecar/tests/test_permissions.py
git commit -m "feat(sidecar): permission helper and enforcement on currency writes"
```

---

## Task B4: CSV/JSON data export (Standard capability)

**Files:**
- Create: `formint/sidecar/formint/export.py`
- Modify: `formint/sidecar/configs/urls.py` (wire 4 routes)
- Test: `formint/sidecar/tests/test_export.py`

**Interfaces:**
- Consumes: `models.pos.{Product, Sale, Customer}`, `models.inventory.InventoryTransaction`.
- Produces: Django views `export_products`, `export_sales`, `export_customers`, `export_inventory` at `/export/<name>.csv` (and `?format=json` variant).

- [ ] **Step 1: Write the failing test**

Create `formint/sidecar/tests/test_export.py`:

```python
import json

from django.test import TestCase
from django.urls import reverse

from models.pos import Product


class ExportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Product.objects.create(name="Latte", price="4.50", tax_rate="standard")

    def test_products_csv(self):
        resp = self.client.get(reverse("export-products"))
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("text/csv")
        body = resp.content.decode()
        assert "id,name,price" in body
        assert "Latte" in body

    def test_products_json(self):
        resp = self.client.get(reverse("export-products") + "?format=json")
        assert resp.status_code == 200
        payload = json.loads(resp.content)
        assert payload["count"] == 1
        assert payload["items"][0]["name"] == "Latte"

    def test_sales_csv(self):
        resp = self.client.get(reverse("export-sales"))
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("text/csv")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_export.py -q`
Expected: FAIL — `django.urls.exceptions.NoReverseMatch` (routes not wired)

- [ ] **Step 3: Write the export views**

Create `formint/sidecar/formint/export.py`:

```python
"""CSV/JSON data export endpoints (Standard capability)."""

from __future__ import annotations

import csv

from django.http import HttpResponse, JsonResponse

from models.pos import Customer, Product, Sale
from models.inventory import InventoryTransaction


def _csv_response(filename: str, header: list[str], rows: list[list]) -> HttpResponse:
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(header)
    writer.writerows(rows)
    return response


def _json_response(items: list[dict]) -> JsonResponse:
    return JsonResponse({"count": len(items), "items": items})


def export_products(request):
    rows = [
        [p.id, p.name, str(p.price), p.tax_rate]
        for p in Product.objects.all().order_by("id")
    ]
    if request.GET.get("format") == "json":
        return _json_response(
            [{"id": r[0], "name": r[1], "price": r[2], "tax_rate": r[3]} for r in rows]
        )
    return _csv_response("products.csv", ["id", "name", "price", "tax_rate"], rows)


def export_sales(request):
    rows = [
        [s.id, s.sale_date.isoformat(), str(s.subtotal), str(s.tax_amount), str(s.total), s.status]
        for s in Sale.objects.all().order_by("-sale_date")
    ]
    if request.GET.get("format") == "json":
        return _json_response(
            [{"id": r[0], "sale_date": r[1], "subtotal": r[2], "tax_amount": r[3], "total": r[4], "status": r[5]} for r in rows]
        )
    return _csv_response("sales.csv", ["id", "sale_date", "subtotal", "tax_amount", "total", "status"], rows)


def export_customers(request):
    rows = [
        [c.id, c.name, c.phone or "", c.email or ""]
        for c in Customer.objects.all().order_by("id")
    ]
    if request.GET.get("format") == "json":
        return _json_response(
            [{"id": r[0], "name": r[1], "phone": r[2], "email": r[3]} for r in rows]
        )
    return _csv_response("customers.csv", ["id", "name", "phone", "email"], rows)


def export_inventory(request):
    rows = [
        [t.id, t.product_id, str(t.quantity), t.transaction_type, t.created_at.isoformat()]
        for t in InventoryTransaction.objects.all().order_by("-created_at")
    ]
    if request.GET.get("format") == "json":
        return _json_response(
            [{"id": r[0], "product_id": r[1], "quantity": r[2], "transaction_type": r[3], "created_at": r[4]} for r in rows]
        )
    return _csv_response("inventory.csv", ["id", "product_id", "quantity", "transaction_type", "created_at"], rows)
```

> Verify the actual field names of `Customer` (`phone`, `email`) and `InventoryTransaction` (`quantity`, `transaction_type`) in `models/pos.py` / `models/inventory.py` and adjust the tuples if they differ — the endpoint contract (route names, formats) stays the same.

- [ ] **Step 4: Wire the routes**

In `formint/sidecar/configs/urls.py`, add to the `urlpatterns` block that already contains the `htmx/*` paths (and import at the top):

```python
from formint.export import (
    export_customers,
    export_inventory,
    export_products,
    export_sales,
)

urlpatterns += [
    path("export/products.csv", export_products, name="export-products"),
    path("export/sales.csv", export_sales, name="export-sales"),
    path("export/customers.csv", export_customers, name="export-customers"),
    path("export/inventory.csv", export_inventory, name="export-inventory"),
]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formint/sidecar && unset DJANGO_SETTINGS_MODULE; python -m pytest tests/test_export.py -q && make test`
Expected: PASS — export tests green, full suite green

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formint/sidecar/formint/export.py projects/formints/formint/sidecar/configs/urls.py projects/formints/formint/sidecar/tests/test_export.py
git commit -m "feat(sidecar): CSV/JSON export endpoints for products, sales, customers, inventory"
```

---

## Task B5: Docs & changelog sync

**Files:**
- Modify: `projects/formints/docs/architecture/editions.md`
- Modify: `projects/formints/CHANGELOG.md`
- Modify: `projects/formints/CONTEXT.md` (only if terminology changed — verify)

- [ ] **Step 1: Update editions.md capability markers**

In `projects/formints/docs/architecture/editions.md`, remove the "landing sync Aug 2026" status from the now-shipped capabilities:
- Community section: "Offline-first mode + refunds & returns (Community capability, landing sync Aug 2026)" → "Offline-first mode + refunds & returns (Community capability)"
- Standard section: "Multi-currency & tax profiles (Standard capability, landing sync Aug 2026)", "Custom roles & permissions (Standard capability)", "Data export CSV/JSON (Standard capability)" → drop the parenthetical suffix.
- Cloud section markers stay as-is (out of scope for this plan).

Also refresh the `> **Last Updated:**` line to the date this plan is executed (format `9 August 2026`).

- [ ] **Step 2: Add CHANGELOG entries**

In `projects/formints/CHANGELOG.md`, under the `## Unreleased` section (or a new dated section at the top), add:

```markdown
### Added (Community — formintA)
- Refunds & returns — `refund_sale` Rust command + Transactions page refund action with confirm dialog
- Offline-first mode indicator — `useOfflineMode` hook + AppShell banner

### Added (Standard — formint sidecar)
- Multi-currency — `Currency` model + `/api/v1/currencies` controller + seed defaults
- Tax profiles — `TaxProfile` model + product/sale linkage + `compute_tax` helper
- Custom roles & permissions — `require_permission` decorator + `resolve_permissions` helper
- Data export — CSV/JSON endpoints for products, sales, customers, inventory
```

- [ ] **Step 3: Verify CONTEXT.md stays accurate**

Read `projects/formints/CONTEXT.md`. Confirm the "Sidecar" glossary entry says Django (it was updated Aug 2026) and does not claim refunds/multi-currency are missing. Only edit if a term is now contradicted (e.g., add "Standard tier: multi-currency, tax profiles, export" to the Edition entry).

- [ ] **Step 4: Full verification sweep**

Run, in order, and fix anything that fails:
```bash
cd projects/formints/formintA/src-tauri && cargo test
cd projects/formints/formintA && pnpm test && pnpm check
cd projects/formints/formint/sidecar && make check && make test
```
Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add projects/formints/docs/architecture/editions.md projects/formints/CHANGELOG.md projects/formints/CONTEXT.md
git commit -m "docs: mark Community and Standard capabilities shipped, update changelog"
```

---

# PART C — Cloud (`formintB/backend/`, pos-cloud): backups & monitoring

> Completes the last Cloud capability marker: "Automatic cloud backups + monitoring (Cloud capability, landing sync Aug 2026)". Mirrors [`docs/plans/editions/04-cloud.md`](docs/plans/editions/04-cloud.md).

## Task C1: `BackupRun` model + migration

**Files:**
- Modify: `formintB/backend/apps/core/models.py`
- Test: `formintB/backend/apps/test_backup.py` (create)

**Interfaces:**
- Produces: `BackupRun` (importable as `from apps.core.models import BackupRun`). Consumed by Task C2 (command) and Task C3 (monitor).

- [ ] **Step 1: Write the failing test**

Create `formintB/backend/apps/test_backup.py` (mirror `apps/test_surface.py` style):

```python
from django.test import TestCase

from apps.core.models import BackupRun


class BackupRunModelTest(TestCase):
    def test_create_and_stringify(self):
        run = BackupRun.objects.create(filename="pos_cloud-20260809-120000.db")
        assert run.status == "running"
        assert str(run) == f"BackupRun pos_cloud-20260809-120000.db (running)"

    def test_fail_and_success_states(self):
        run = BackupRun.objects.create(filename="a.db")
        run.status = "success"
        run.size_bytes = 42
        run.save()
        run.refresh_from_db()
        assert run.status == "success"
        assert run.size_bytes == 42
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: FAIL — `ModuleNotFoundError` / `BackupRun` import error.

> If the suite normally runs through `make test` with a specific settings module, use the same invocation the `Makefile` uses for `apps/test_surface.py`.

- [ ] **Step 3: Write the model**

Append to `formintB/backend/apps/core/models.py`:

```python
class BackupRun(models.Model):
    """Record of a database backup attempt (Cloud capability)."""

    filename = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[("running", "Running"), ("success", "Success"), ("failed", "Failed")],
        default="running",
    )
    size_bytes = models.BigIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "backup run"
        verbose_name_plural = "backup runs"
        ordering = ["-started_at"]

    def __str__(self):
        return f"BackupRun {self.filename} ({self.status})"
```

- [ ] **Step 4: Generate and apply the migration**

Run:
```bash
cd projects/formints/formintB/backend
python manage.py makemigrations core
make migrate
```
Expected: migration for `BackupRun` created and applied.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: PASS — 2 tests green.

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formintB/backend/apps/core/models.py projects/formints/formintB/backend/apps/core/migrations/ projects/formints/formintB/backend/apps/test_backup.py
git commit -m "feat(pos-cloud): BackupRun model records database backup attempts"
```

## Task C2: `backup_db` management command

**Files:**
- Create: `formintB/backend/apps/core/management/commands/backup_db.py`
- Modify: `formintB/backend/apps/test_backup.py` (add command test)

**Interfaces:**
- Consumes: `BackupRun` (Task C1), `settings.DATABASES["default"]["NAME"]`.
- Produces: `manage.py backup_db [--dest DIR]` — timestamped SQLite backup + `BackupRun` row. Consumed by Task C3.

- [ ] **Step 1: Write the failing test**

Append to `formintB/backend/apps/test_backup.py`:

```python
import os
import tempfile

from django.core.management import call_command

from apps.core.models import BackupRun


class BackupCommandTest(TestCase):
    def test_backup_db_creates_file_and_run(self):
        with tempfile.TemporaryDirectory() as dest:
            call_command("backup_db", dest=dest)
            run = BackupRun.objects.latest("started_at")
            assert run.status == "success"
            assert run.size_bytes is not None
            files = os.listdir(dest)
            assert len(files) == 1
            assert files[0].startswith("pos_cloud-")
            assert files[0].endswith(".db")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: FAIL — `CommandError: Unknown command: 'backup_db'`

- [ ] **Step 3: Write the command**

Create `formintB/backend/apps/core/management/commands/backup_db.py`:

```python
"""Backup the pos_cloud SQLite database (Cloud capability).

Usage:  python manage.py backup_db [--dest DIR]

Writes ``pos_cloud-YYYYMMDD-HHMMSS.db`` into the backup directory (default:
``<db-dir>/backups``) using SQLite's online backup API, and records the run
in ``BackupRun``.
"""

import os
import sqlite3
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.models import BackupRun


class Command(BaseCommand):
    help = "Create an online SQLite backup of the cloud database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dest", default=None,
            help="Backup directory (default: <database dir>/backups)",
        )

    def handle(self, *args, **options):
        db_path = settings.DATABASES["default"]["NAME"]
        dest_dir = options["dest"] or os.path.join(
            os.path.dirname(os.path.abspath(str(db_path))), "backups",
        )
        os.makedirs(dest_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = os.path.join(dest_dir, f"pos_cloud-{timestamp}.db")

        run = BackupRun.objects.create(filename=os.path.basename(dest))
        try:
            source = sqlite3.connect(str(db_path))
            target = sqlite3.connect(dest)
            try:
                source.backup(target)
            finally:
                target.close()
                source.close()
            run.status = "success"
            run.size_bytes = os.path.getsize(dest)
            run.finished_at = datetime.now()
            run.save(update_fields=["status", "size_bytes", "finished_at"])
            self.stdout.write(self.style.SUCCESS(f"backup written: {dest}"))
        except Exception as exc:  # noqa: BLE001 — record the failure and re-raise
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = datetime.now()
            run.save(update_fields=["status", "error_message", "finished_at"])
            self.stdout.write(self.style.ERROR(f"backup failed: {exc}"))
            raise
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_backup.py -q`
Expected: PASS — 3 tests green.

- [ ] **Step 5: Run the full suite**

Run: `cd projects/formints/formintB/backend && make test`
Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formintB/backend/apps/core/management/commands/backup_db.py projects/formints/formintB/backend/apps/test_backup.py
git commit -m "feat(pos-cloud): backup_db management command with online SQLite backup"
```

## Task C3: `/monitor/status` endpoint

**Files:**
- Modify: `formintB/backend/apps/handlers/surface.py` (add `monitor_status`)
- Modify: `formintB/backend/configs/urls.py` (wire route)
- Test: `formintB/backend/apps/test_monitor.py` (create)

**Interfaces:**
- Consumes: `BackupRun` (Task C1), `SyncQueueItem` (exists in `apps.core.models`).
- Produces: `monitor_status(request) -> JsonResponse` at `/monitor/status` — payload `{database, last_backup, sync_queue_depth}`.

- [ ] **Step 1: Write the failing test**

Create `formintB/backend/apps/test_monitor.py`:

```python
import json

from django.test import TestCase
from django.urls import reverse

from apps.core.models import BackupRun, SyncQueueItem


class MonitorStatusTest(TestCase):
    def test_healthy_with_no_backups(self):
        resp = self.client.get(reverse("monitor-status"))
        assert resp.status_code == 200
        payload = json.loads(resp.content)
        assert payload["database"] == "ok"
        assert payload["last_backup"] is None
        assert payload["sync_queue_depth"] == 0

    def test_reports_latest_backup(self):
        BackupRun.objects.create(
            filename="pos_cloud-20260809-120000.db",
            status="success",
            size_bytes=128,
        )
        resp = self.client.get(reverse("monitor-status"))
        payload = json.loads(resp.content)
        assert payload["last_backup"]["status"] == "success"
        assert payload["last_backup"]["size_bytes"] == 128

    def test_reports_queue_depth(self):
        SyncQueueItem.objects.create(payload={}, status="pending")
        SyncQueueItem.objects.create(payload={}, status="pending")
        resp = self.client.get(reverse("monitor-status"))
        payload = json.loads(resp.content)
        assert payload["sync_queue_depth"] == 2
```

> If `SyncQueueItem` requires extra required fields, mirror an existing `SyncQueueItem.objects.create(...)` call from `apps/test_surface.py` or `apps/domain/sync_queue.py` tests.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_monitor.py -q`
Expected: FAIL — `NoReverseMatch` for `monitor-status`

- [ ] **Step 3: Write the view**

In `formintB/backend/apps/handlers/surface.py`, add next to the existing `stats` function (matching its imports):

```python
def monitor_status(request: HttpRequest) -> JsonResponse:
    """Health summary for the cloud master: db reachability, last backup, queue depth."""
    from apps.core.models import BackupRun, SyncQueueItem

    database = "ok"
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # noqa: BLE001
        database = "error"

    latest = BackupRun.objects.order_by("-started_at").first()
    last_backup = None
    if latest is not None:
        last_backup = {
            "filename": latest.filename,
            "status": latest.status,
            "size_bytes": latest.size_bytes,
            "started_at": latest.started_at.isoformat(),
        }

    return JsonResponse({
        "database": database,
        "last_backup": last_backup,
        "sync_queue_depth": SyncQueueItem.objects.count(),
    })
```

- [ ] **Step 4: Wire the route**

In `formintB/backend/configs/urls.py`, import `monitor_status` from `apps.handlers.surface` (same import block as `stats`) and add next to the `path("stats", ...)` line (~1240):

```python
path("monitor/status", apps_handlers_surface_monitor_status, name="monitor-status"),
```

(Use the same import alias convention the file already uses for the surface module.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formintB/backend && unset DJANGO_SETTINGS_MODULE; python -m pytest apps/test_monitor.py -q && make test`
Expected: PASS — monitor tests green, full suite green

- [ ] **Step 6: Commit**

```bash
git add projects/formints/formintB/backend/apps/handlers/surface.py projects/formints/formintB/backend/configs/urls.py projects/formints/formintB/backend/apps/test_monitor.py
git commit -m "feat(pos-cloud): /monitor/status endpoint with db health, last backup, queue depth"
```

## Task C4: Cloud docs & changelog sync

**Files:**
- Modify: `projects/formints/docs/architecture/editions.md`
- Modify: `projects/formints/CHANGELOG.md`

- [ ] **Step 1: Update editions.md**

In `projects/formints/docs/architecture/editions.md`, change both occurrences of "Automatic cloud backups + monitoring (Cloud capability, landing sync Aug 2026)" → "Automatic cloud backups + monitoring (Cloud capability)".

- [ ] **Step 2: Add a CHANGELOG entry**

Under `## Unreleased`:

```markdown
### Added (Cloud — pos-cloud)
- Automatic backups — `BackupRun` model + `manage.py backup_db` (online SQLite backup with retention-ready records)
- Monitoring — `/monitor/status` endpoint (db health, last backup, sync queue depth)
```

- [ ] **Step 3: Commit**

```bash
git add projects/formints/docs/architecture/editions.md projects/formints/CHANGELOG.md
git commit -m "docs: mark Cloud backups + monitoring shipped, update changelog"
```

---

## Self-Review

**1. Spec coverage** — the capability gaps flagged "(landing sync Aug 2026)" in `editions.md` were the spec: Community refunds & returns (A1, A2) and offline-first mode (A3); Standard multi-currency (B1), tax profiles (B2), custom roles & permissions (B3), data export (B4); Cloud backups + monitoring (C1-C3); docs/changelog sync (B5, C4). Every remaining marker maps to a task. Nothing is out of scope anymore.

**2. Placeholder scan** — no "TBD"/"implement later" steps. The only conditional instructions are explicit, actionable ones: (a) A1 note about constructing a `NewSaleItem` if the empty-items path fails, (b) B3's note to confirm ninja-extra base signatures against an existing override, (c) B4's note to verify `Customer`/`InventoryTransaction` field names, (d) C3's note about `SyncQueueItem` required fields. Each names the exact file to check and what to keep stable.

**3. Type consistency** — `refund_sale(db_path: &PathBuf, sale_id: i32) -> Result<Sale, String>` is defined in A1 and invoked as `invoke('refund_sale', { saleId })` in A2 (Tauri maps `saleId` → `sale_id`). `Currency`/`TaxProfile` models defined in B1/B2 are referenced identically in `models/models.py`, `controllers.py`, and tests. `compute_tax(subtotal: Decimal, rate: Decimal) -> Decimal` is defined in B2 and used only there. Export view names match the URL `name=` values used by `reverse()` in B4 tests. `BackupRun` fields (`filename`, `status`, `size_bytes`, `error_message`, `started_at`, `finished_at`) are identical across C1 (model), C2 (command), C3 (monitor payload), and their tests; route name `monitor-status` matches `reverse()` in C3 tests.

---

## Execution Handoff

**Plan complete and maintained at `docs/plans/editions/finish-community-standard.md`** — Parts A (Community), B (Standard), C (Cloud). Per-edition mirrors with design/architecture/data-model sections live in `docs/plans/editions/`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
