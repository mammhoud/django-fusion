# Community Edition — Design, Architecture & Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the Community edition (`formintA/`) by shipping refunds & returns and the offline-first mode indicator, with design, architecture, and data model documented as the base of the extension chain.

**Architecture:** Offline-first desktop POS. Astro 5 (25 pages) + React 19 components call Tauri commands (`invoke`) that hit Rust/Diesel functions backed by embedded SQLite (`restaurant.db`). No Django, no sidecar, no cloud. Refunds mutate the existing `sales.status` column ("refunded") via a new `refund_sale` command; offline-first is a UI state surfaced by a `useOfflineMode` hook.

**Tech Stack:** Rust (diesel 2.2, diesel_migrations 2.2, tauri 2) · TypeScript (React 19, Astro 5, Vitest, @testing-library/react). No new dependencies.

## Global Constraints

- All changes live under `projects/formints/formintA/` only.
- **No new runtime dependencies.** Rust uses only diesel + diesel_migrations (already in `src-tauri/Cargo.toml`).
- Tauri port stays 1420. Commands are snake_case (`refund_sale`).
- **No schema migration needed for refunds:** `sales.status` already exists and accepts `"refunded"`.
- **Feature inheritance (base tier):** Community is the root of the extension chain — every higher edition (Standard, Pro, Cloud) must include ALL Community features. No upward inheritance applies here.
- Test commands: Rust `cd projects/formints/formintA/src-tauri && cargo test` · frontend `cd projects/formints/formintA && pnpm test`.
- AGPL-3.0; keep existing code style and docstrings.

---

## Design

**Audience:** a single terminal operator (cashier/manager) running one offline device — no network, no multi-terminal.

**Refunds & returns.** The operator opens **Transactions**, sees a completed sale, clicks **Refund**, confirms in a dialog, and the sale flips to a visually distinct `Refunded` state. Rules:

- Only `completed` sales can be refunded (never `pending`, `refunded`, `cancelled`).
- A sale can be refunded only once — the command is idempotent and returns a clear error on a second attempt.
- The refund is recorded in the existing `sales` row (`status = "refunded"`); the history row stays visible so the transaction trail is preserved. No data is deleted.

**Offline-first mode.** Because Community has no network dependency at all, "offline-first" is surfaced as a calm, explicit state: a fixed top banner reading "Offline mode — data stays on this device" appears only when the OS reports the device offline. It is informational, non-blocking, and dismissible-by-time (auto-styled, no close button needed).

**Copy register:** plain, concrete verbs ("Refund", "Confirm refund", "Refunding…"). Errors say what happened ("Sale #42 is already refunded").

## Architecture

```
Astro page (Transactions.astro)
  └── React component (Transactions.tsx)
        ├── invoke('get_sales') → Rust sales::get_sales
        ├── invoke('refund_sale', { saleId }) → Rust sales::refund_sale
        └── UI state: refundTarget (confirm dialog), refunding (busy flag)

AppShell.tsx
  └── useOfflineMode() hook → fixed banner when offline
        ├── window 'offline' / 'online' events
        └── navigator.onLine initial value
```

Data flow: `Transactions.tsx` → `invoke` → `lib.rs` handler → `operations/sales.rs::refund_sale` → Diesel UPDATE on `sales` → `Sale` returned → UI refreshes the list.

## Data model (base of the extension chain)

Diesel schema `src-tauri/src/db/schema.rs`, DB `restaurant.db`. Relevant entities:

| Table | Key columns | Notes |
|-------|-------------|-------|
| `sales` | `id`, `total_amount`, `currency`, `status`, `payment_method`, `employee_id`, `customer_id`, `created_at` | `status` accepts `completed` / `refunded` / `cancelled` / `pending` |
| `sale_items` | `id`, `sale_id`, `product_id`, `quantity`, `unit_price` | line items |
| `products` | `id`, `name`, `price`, `unit`, `product_type` | no stock column at this tier (inventory via `ingredients`) |

**Extension delta:** nothing is added to the schema in this plan — refunds reuse `sales.status`, offline-first is UI-only. Later tiers (Standard) add the Django `full_*` schema on top of these domain concepts.

---

## Task A1: Rust `refund_sale` command

**Files:**
- Modify: `formintA/src-tauri/src/operations/sales.rs` (add `refund_sale` + inline test module)
- Modify: `formintA/src-tauri/src/lib.rs` (register in `invoke_handler`)

**Interfaces:**
- Consumes: `crate::db::{models::*, open_conn}`, `crate::db::schema::sales::dsl`, `crate::db::run_migrations` (all exist).
- Produces: `pub fn refund_sale(db_path: &PathBuf, sale_id: i32) -> Result<Sale, String>` — consumed by Task A2 via `invoke('refund_sale', { saleId })`.

- [ ] **Step 1: Write the failing test**

Append to `formintA/src-tauri/src/operations/sales.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;

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

> If `add_sale` with an empty `items` vec fails in your checkout (kitchen-ticket creation), seed the sale with a single `NewSaleItem` constructed exactly as in `Sale.tsx` (fields `product_id`, `quantity`, `unit_price`, `name` — confirm against `db::models::NewSaleItem` at `models.rs` ~line 251).

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

- [ ] **Step 4: Register the command**

In `formintA/src-tauri/src/lib.rs`, add `refund_sale,` to the existing `tauri::generate_handler![...]` list that already contains `add_sale`, `update_sale`, `delete_sale`, `get_sales`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd projects/formints/formintA/src-tauri && cargo test refund_sale`
Expected: PASS — `test result: ok. 3 passed`

- [ ] **Step 6: Run the full Rust suite**

Run: `cd projects/formints/formintA/src-tauri && cargo test`
Expected: all pass (existing + 3 new).

- [ ] **Step 7: Commit**

```bash
git add projects/formints/formintA/src-tauri/src/operations/sales.rs projects/formints/formintA/src-tauri/src/lib.rs
git commit -m "feat(formintA): refund_sale command marks a sale refunded (idempotent)"
```

---

## Task A2: Refund & return UI (Transactions page)

**Files:**
- Modify: `formintA/src/app/pages/pos/Transactions.tsx`
- Test: `formintA/src/test/pages/Transactions.test.tsx` (create — mirror `src/test/pages/Sale.test.tsx`)

**Interfaces:**
- Consumes: `refund_sale` from Task A1 via `invoke('refund_sale', { saleId })`.
- Produces: `handleRefund()` + a `refunded` status chip.

- [ ] **Step 1: Write the failing test**

Create `formintA/src/test/pages/Transactions.test.tsx`:

```tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Transactions from '@/app/pages/pos/Transactions';
import { invoke } from '@tauri-apps/api/core';

vi.mock('@tauri-apps/api/core', () => ({ invoke: vi.fn() }));

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
Expected: FAIL — no refund button rendered (or module resolution error, fine at this stage)

- [ ] **Step 3: Implement the refund action**

In `formintA/src/app/pages/pos/Transactions.tsx`:

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

Add the button to the row actions (only for `completed` sales), the confirm dialog (reuse `ConfirmDialog` from `@/components/ui`), and map `sale.status` to badges with a distinct amber `refunded` chip:

```tsx
{sale.status === 'completed' && (
  <button type="button" className="btn btn-sm btn-outline" onClick={() => setRefundTarget(sale)}>
    Refund
  </button>
)}

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

- [ ] **Step 4: Run test to verify it passes**

Run: `cd projects/formints/formintA && pnpm vitest run src/test/pages/Transactions.test.tsx`
Expected: PASS

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
- Modify: `formintA/src/components/AppShell.tsx`
- Test: `formintA/src/test/hooks/useOfflineMode.test.ts`

**Interfaces:**
- Produces: `export function useOfflineMode(): boolean` — `true` while offline. Consumed by `AppShell.tsx`.

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

In `formintA/src/components/AppShell.tsx`:

```tsx
import { useOfflineMode } from '@/hooks/useOfflineMode';

const offline = useOfflineMode();

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

# Cross-cutting enhancements (Community)

> Community is Rust/Diesel-only — the modular TS SDK (06-js-sdk.md) targets the Django-backed editions, and django-fusion does not apply. The e2e suite locks the UI contract instead.

## Task A4: Playwright e2e for the refund flow

**Files:**
- Create: `formintA/e2e/refund.spec.ts`
- Modify: `formintA/playwright.config.ts` (add the spec to `testMatch` if it is not already covered)

**Interfaces:**
- Consumes: the refund UI from Task A2 (Refund button + Confirm dialog + `refunded` chip).
- Produces: a repeatable e2e regression for the refund flow; run separately from every other edition's suite.

- [ ] **Step 1: Write the failing spec**

Create `formintA/e2e/refund.spec.ts`, mirroring the bootstrap/mocking conventions of the existing `formintA/e2e/auth-visual.spec.ts` and its `e2e/mocks/` helpers:

```ts
import { test, expect } from '@playwright/test';

// Bootstrap the app exactly like auth-visual.spec.ts (same URL, same mock wiring).
test.beforeEach(async ({ page }) => {
  // Seed the mocked sale list with one completed sale (follow e2e/mocks helpers).
  await page.route('**/get_sales', async (route) => {
    await route.fulfill({
      json: [
        { id: 1, total_amount: 25, currency: 'USD', status: 'completed', payment_method: 'cash' },
      ],
    });
  });
});

test('refunds a completed sale end to end', async ({ page }) => {
  await page.goto('/transactions');
  await expect(page.getByRole('button', { name: 'Refund' })).toBeVisible();
  await page.getByRole('button', { name: 'Refund' }).click();
  await expect(page.getByRole('button', { name: 'Confirm refund' })).toBeVisible();
  await page.getByRole('button', { name: 'Confirm refund' }).click();
  await expect(page.getByText(/refunded/i)).toBeVisible();
});

test('does not show refund for an already refunded sale', async ({ page }) => {
  await page.route('**/get_sales', async (route) => {
    await route.fulfill({
      json: [{ id: 2, total_amount: 10, currency: 'USD', status: 'refunded', payment_method: 'cash' }],
    });
  });
  await page.goto('/transactions');
  await expect(page.getByText(/refunded/i)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Refund' })).toHaveCount(0);
});
```

> If the existing e2e suite drives the app through a different entry point or mock strategy, follow that exact convention (URL, mock helper) — the assertions above are the contract.

- [ ] **Step 2: Run spec to verify it fails**

Run: `cd projects/formints/formintA && pnpm exec playwright test e2e/refund.spec.ts`
Expected: FAIL — no Refund button (UI from A2 not present yet, or spec not matching).

- [ ] **Step 3: Implement (or align) the UI per Task A2**

Ensure the Transactions page renders the Refund button + confirm dialog exactly as specified in Task A2 (Step 3). Re-run the spec.

- [ ] **Step 4: Run the full Community e2e suite**

Run: `cd projects/formints/formintA && pnpm exec playwright test`
Expected: PASS — refund spec + existing specs green.

- [ ] **Step 5: Commit**

```bash
git add projects/formints/formintA/e2e/refund.spec.ts projects/formints/formintA/playwright.config.ts
 git commit -m "test(formintA): Playwright e2e for the refund flow"
```

## Task A5: SDK applicability note

**Files:**
- Modify: `projects/formints/docs/architecture/editions.md` (Community section)

- [ ] **Step 1: Document the boundary**

In the Community section of `editions.md`, add one line under Features:

```markdown
- **API surface:** Tauri `invoke` commands (Rust/Diesel) — the `@formints/client` TS bundle applies to the Django-backed editions (Standard/Cloud), not this edition
```

- [ ] **Step 2: Commit**

```bash
git add projects/formints/docs/architecture/editions.md
git commit -m "docs: note Community's invoke-only API surface vs the TS client bundle"
```

---

## Self-Review

1. **Spec coverage:** Community capability markers (refunds & returns, offline-first) both map to tasks (A1+A2, A3). No other Community markers remain.
2. **Placeholder scan:** Only one conditional instruction (A1 note re: `NewSaleItem` construction if empty-items fails) — it names the exact file and fields to mirror.
3. **Type consistency:** `refund_sale(db_path: &PathBuf, sale_id: i32) -> Result<Sale, String>` defined in A1 is invoked as `invoke('refund_sale', { saleId })` in A2 (Tauri maps `saleId` → `sale_id`). `useOfflineMode(): boolean` matches its test usage.

## Execution Handoff

**Plan complete and maintained at `docs/plans/editions/01-community.md`.** Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
