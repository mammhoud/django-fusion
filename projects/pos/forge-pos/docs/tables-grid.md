# Forge POS — Tables & Grids Reference

> **Components:** `src/components/ui/DataTable.tsx` · **Utilities:** `.grid--auto*` in `assets/styles/index.css`

---

## Overview

Two layout systems cover the app's data-dense screens:

1. **DataTable** — sortable, paginated-free, CSV-exportable table with inline editing and row selection (used by ProductManager table view, Transactions, Inventory, Customers, …).
2. **CSS grids** — hand-rolled responsive `grid-cols-*` classes for product/card grids plus the auto-fill helpers `.grid--auto`, `.grid--auto-sm`, `.grid--auto-lg`.

---

## DataTable Component

### API

```tsx
<DataTable<Product>
  columns={columns}
  data={filteredProducts}
  keyExtractor={(p) => p.id}
  emptyMessage={t('productManager.noProducts')}
  onEditSave={handleInlineEdit}   // inline edit callback (optional)
  exportable                        // adds CSV export toolbar
  fileName="products"               // CSV filename
  mobileRender={mobileRender}       // responsive mobile row renderer
  selectable                        // row checkboxes
/>
```

| Prop | Type | Purpose |
|------|------|---------|
| `columns` | `Column<T>[]` | Column definitions (see below) |
| `data` | `T[]` | Rows |
| `keyExtractor` | `(row) => string \| number` | Unique row key |
| `emptyMessage` | `string` | Empty-state text |
| `onEditSave` | `(row, key, value) => void \| Promise` | Persist inline edits |
| `exportable` / `fileName` | `boolean` / `string` | CSV export toolbar |
| `mobileRender` | `(row) => ReactNode` | Mobile fallback renderer |
| `selectable` / `selectedIds` / `onSelectionChange` | — | Row selection |

### Column definition

```tsx
const columns: Column<Product>[] = [
  {
    key: 'name',
    label: t('productManager.productName'),
    sortable: true,
    editable: true,
    render: (p) => <span className="font-medium">{p.name}</span>,
  },
  {
    key: 'price',
    label: `Price (${currencySymbol})`,
    sortable: true,
    editable: true,
    editType: 'number',
    render: (p) => <span className="font-semibold text-primary">{formatPrice(p.price)}</span>,
  },
  {
    key: 'category_id',
    label: 'Category',
    sortable: true,
    hideOnMobile: true,           // hidden in desktop header when narrow? no — hidden on mobile
    render: (p) => <span className="badge badge-sm badge-ghost">{categoryMap[p.category_id]}</span>,
  },
  {
    key: '_actions',
    label: '',
    render: (p) => (
      <div className="flex items-center gap-1 justify-end">
        <button onClick={() => openEditModal(p)} className="p-1.5 rounded-md hover:text-primary">✎</button>
        <button onClick={() => openDeleteConfirmation(p)} className="p-1.5 rounded-md hover:text-error">🗑</button>
      </div>
    ),
  },
];
```

| Column field | Purpose |
|--------------|---------|
| `key` | Data accessor (or `_actions` for virtual columns) |
| `label` | Header text |
| `sortable` | Click-to-sort header |
| `editable` + `editType` | Inline edit (`text` or `number`) — saved via `onEditSave` |
| `hideOnMobile` | Column hidden in the mobile card layout |
| `colSpan` | Grid fraction for the column |
| `render` | Cell renderer |

### Inline editing

```tsx
const handleInlineEdit = async (product: Product, key: string, value: string) => {
  const update: UpdateProductPayload = {};
  if (key === 'name') update.name = value;
  else if (key === 'price') update.price = parseFloat(value) || 0;
  await invoke<Product>('update_product', { id: product.id, update });
};
```

Click an editable cell → input appears → `Enter` / blur confirms, `Esc` cancels. A saving spinner shows while `onEditSave`'s promise is pending.

### CSV export

With `exportable`, a toolbar renders a **CSV** button that streams the currently sorted rows to a `.csv` file. Columns marked `hideOnMobile` are excluded from the export.

---

## Responsive Card Grids

### Hand-rolled columns (product grids)

```tsx
<div className={`grid gap-3 sm:gap-4 ${
  viewMode === 'compact'
    ? 'grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-7 xl:grid-cols-8'
    : 'grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6'
}`}>
  {products.map(p => <ProductCard key={p.id} … />)}
</div>
```

### Auto-fill helpers (BEM)

`assets/styles/index.css` provides three auto-fill grids that always fill the container and collapse gracefully:

```css
.grid--auto    { grid-template-columns: repeat(auto-fill, minmax(min(100%, 12rem), 1fr)); }
.grid--auto-sm { grid-template-columns: repeat(auto-fill, minmax(min(100%, 9rem), 1fr)); }
.grid--auto-lg { grid-template-columns: repeat(auto-fill, minmax(min(100%, 15rem), 1fr)); }
```

```tsx
<div className="grid--auto">{products.map(p => <ProductCard key={p.id} … />)}</div>
```

### Form grids

- Two-column rows: `grid grid-cols-2 gap-3`
- Choice tiles: `grid grid-cols-2 sm:grid-cols-4 gap-2`
- Side-by-side selects: `grid grid-cols-1 sm:grid-cols-2 gap-3` (Sale order card)

---

## References

- `src/components/ui/DataTable.tsx` — component source (sorting, editing, export, selection)
- `src/pages/pos/ProductManager.tsx` — richest DataTable usage + grid/table toggle
- `assets/styles/index.css` — `.grid--auto*` utilities
- [`docs/forms.md`](forms.md) — form grids & layout patterns
- [`docs/pages-options.md`](pages-options.md) — which page uses which table/grid
