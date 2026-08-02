# Forge POS — Page Options Reference

> What search / filter / sort / view / action options exist on each major page.

---

## Shared Building Blocks

| Block | Component | Pages |
|-------|-----------|-------|
| Compact search bar | `ProductFilterBar` (shared) | ProductManager, Sale |
| Debounced search hook | `useDebouncedSearch` | ProductManager, Sale, Customers, Suppliers |
| Category pills | `CategoryFilterPills` (shared) | ProductManager, Sale |
| DataTable | `DataTable` | ProductManager, Transactions, Inventory, Customers, Suppliers, Employees |
| Status toasts | `useStatusToast` / alert toasts | Sale, ProductManager, … |
| Keyboard shortcut help | `KeyboardShortcutsModal` | Sale, ProductManager, … |

---

## Sale (POS) — `src/pages/pos/Sale.tsx`

### Compact search bar (shared `ProductFilterBar`)
- **Search** — debounced product search (name) with loading spinner + clear button
- **Product type select** — All / Products / Combos / Add-ons
- **Sort select** — Newest / A→Z / Z→A / $↑ / $↓
- **View toggle** — Standard grid / Compact grid (segmented control)
- **Live-update badge** — pulses when `product-updated` fires
- **Category pills** — colored tag pills with counts, hover tooltips + expandable color legend
- **Result counter** — `filtered / total` bottom-right, auto-hidden when no filter active

### Order card (mobile + desktop sidebar)
- **Order types** — Dine-in / Takeaway / Delivery / Extra Order / Dated Order (keys `1/2/3`; flex layout)
- **Dine-in** — Table select + Employee select **side by side**
- **Delivery** — Delivery Type + Zone selects **side by side**, Distance, Address, fee estimator (cap warning beyond zone max)
- **Employee assignment** — server/cashier select
- **Order notes** — free text + Quick Notes (selectable notes that append), quick-add new note
- **Receipt template** — pick a `category='receipt'` note appended to footer

### Cart & checkout
- Cart summary with per-item quantity +/- , inline item notes
- Subtotal / delivery fee / total breakdown
- **Amount card** — centered total with wallet icon + items badge (mobile & sidebar)
- Complete Sale (Enter), PDF receipt download, Invoice PDF (7 invoice types), print

---

## ProductManager — `src/pages/pos/ProductManager.tsx`

### Compact search bar (shared `ProductFilterBar`)
- **Search** — debounced search over name + barcode + category name
- **Sort select** — Newest / A→Z / Z→A / $↑ / $↓ (grid view only)
- **View toggle** — Grid / Table
- **Add product button** — opens the product modal (`A` shortcut)
- **Category pills** — colored pills + Manage categories button + clear-filter ×

### Stats row
- Total products + visible (filtered) count

### Product grid / table
- ProductCard grid (unique per-product accent colors, toggleable in Settings) or DataTable
- Table: sortable columns, inline edit (name/price/barcode), CSV export, mobile card renderer
- Per-product actions: edit, delete (confirm dialog)

### Modals
- Product add/edit modal (image picker, type tiles, available order types, price+unit, prep time, barcode, description, category)
- Category CRUD modal (name + palette/custom color picker, existing categories list)
- Delete confirmations (danger variant)

---

## Transactions — `src/pages/pos/Transactions.tsx`

- Search (customer/employee/notes), filters: date range, payment status, order type, zone
- Time-bucketed KPIs (Today / Week / Month / Outstanding) — StatCard rows
- DataTable with sorting, row selection, CSV export, pagination
- Receipt dialog + PDF per transaction, invoice generation

---

## Inventory — `src/pages/pos/Inventory.tsx`

- Ingredient list with low-stock badges, search, category filter
- DataTable + stock movement (in/out) log
- Ingredient CRUD modal (unit, min stock, supplier, cost)

---

## Recipes — `src/pages/pos/Recipes.tsx`

- Recipe cards + ingredient linking, per-recipe cost calc
- Search, category filter, sort

---

## Reports & Analytics

- **Analytics** — Recharts: revenue, orders, product distribution, time filters
- **Reports** — tabs (overview/sales/inventory/…), order-type breakdown, delivery-only view, Excel/CSV export

---

## Admin pages

| Page | Options |
|------|---------|
| **Settings** | General / Business / Dining / Appearance tabs, theme variant picker, currency, Theme Studio link, Theme Preview modal, SMTP support config, reset DB |
| **Employees** | Employee CRUD, types, DataTable, search, roles |
| **Customers / Suppliers** | CRUD + search + DataTable + export |
| **Roles** | Permission catalog + matrix editor |
| **Notes** | Note CRUD + category (`receipt` / selectable flags) |
| **ReceiptTemplates** | Template editor + category filter |
| **TaxReports** | Period reports + export |
| **Payroll / Schedules** | Periods, statuses, shift grids |

---

## References

- [`docs/shared-components.md`](shared-components.md) — the shared `ProductFilterBar` + how to add it anywhere
- [`docs/tables-grid.md`](tables-grid.md) — DataTable & grid usage
- [`docs/forms.md`](forms.md) — form fields & validation
- Per-page test files in `src/test/pages/` — behavioural specs for the options above
