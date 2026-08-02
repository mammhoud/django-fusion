# Forge POS — Shared Components

> **Component:** `src/components/shared/ProductFilterBar.tsx`

---

## Overview

`ProductFilterBar` is the **shared compact search + filter + sort bar** extracted from the duplicated markup that previously lived in both **ProductManager** and **Sale**. One component now renders the same glassy rounded card on both pages:

```
┌─────────────────────────────────────────────────────────────┐
│ [ 🔍 Search… ] [type ▾] [sort ▾] [view] [＋ Add]  actions  │
│ [ All ] [ 🟠 Burgers ] [ 🟢 Sides ]   (category pills)     │
│ 12 / 40                                                   │
└─────────────────────────────────────────────────────────────┘
```

- **Search row** — `SearchInput` + any extra controls (`topRowActions`)
- **Pills row** — `CategoryFilterPills` + extra pills (`pillsChildren`)
- **Footer slot** — result counter / hints (`footer`)

---

## Why share it?

- Single source of truth for the visual design (rounded-2xl glass bar, hover pills, spinner/clear states).
- New pages get a consistent filter UX in ~20 lines instead of copying 100+ lines of JSX.
- Behaviour (debounce spinner, toggle-to-reset pills, legend) is guaranteed identical.

---

## API

```tsx
<ProductFilterBar
  searchValue={searchQuery}
  onSearchChange={setSearchQuery}
  searchPlaceholder={t('sale.searchProducts')}
  searchAriaLabel={t('sale.searchProducts')}
  searchTestId="sale-search-input"
  searchLoading={isSearching}
  searchDisabled={isLoading}
  topRowActions={<>{/* selects, view toggles, add buttons */}</>}
  categories={categories}
  selectedCategory={selectedCategory}
  onCategoryChange={setSelectedCategory}
  categoryAllLabel={t('sale.allCategories')}
  categoryTestIdPrefix="sale-category-filter"
  categoryCounts={categoryCounts}
  showLegend
  legendLabel={t('sale.categoryLegend')}
  pillsChildren={<>{/* manage-categories button etc. */}</>}
  footer={<div>…result counter…</div>}
/>
```

| Prop | Purpose |
|------|---------|
| `searchValue` / `onSearchChange` | Controlled search text |
| `searchPlaceholder` / `searchAriaLabel` | i18n strings |
| `searchTestId` | Stable test id → forwarded to `<input>` |
| `searchLoading` / `searchDisabled` | Spinner / disabled input |
| `topRowActions` | Extra controls in the top row |
| `categories` / `selectedCategory` / `onCategoryChange` | Pills state |
| `categoryAllLabel` / `categoryAriaLabel` | Pills i18n |
| `categoryTestIdPrefix` / `categoryAllTestId` | Pills test ids |
| `categoryCounts` / `showLegend` / `legendLabel` / `categoryTooltipFormatter` | Counts + legend |
| `pillsChildren` | Extra pills (e.g. Manage button, clear ×) |
| `footer` | Bottom row (result counter) |

---

## How ProductManager uses it

- Search: debounced, matches name + barcode + category name
- `topRowActions`: sort select (grid only), grid/table view toggle, **Add product** button
- `pillsChildren`: **Manage categories** button + clear-× when filtered
- No footer, no legend

## How Sale uses it

- Search: debounced product name search
- `topRowActions`: **product type + sort selects grouped side-by-side**, live-update badge, standard/compact view segmented control
- Pills: counts + **expandable color legend** with tooltips
- `footer`: `filtered / total` result counter (auto-hidden when no filter)

---

## Adding the bar to a new page

```tsx
import ProductFilterBar from '../components/shared/ProductFilterBar';

// 1. Debounced search state (shared hook)
const { query: search, setQuery: setSearch, debouncedQuery, isPending } = useDebouncedSearch();

// 2. Filter products in a useMemo using debouncedQuery
const filtered = useMemo(() => {
  const q = debouncedQuery.trim().toLowerCase();
  return items.filter(i => !q || i.name.toLowerCase().includes(q));
}, [items, debouncedQuery]);

// 3. Render the bar
<ProductFilterBar
  searchValue={search}
  onSearchChange={setSearch}
  searchPlaceholder={t('page.searchPlaceholder')}
  searchAriaLabel={t('page.searchPlaceholder')}
  searchTestId="page-search-input"
  searchLoading={isPending}
  categories={categories}
  selectedCategory={selectedCategory}
  onCategoryChange={setSelectedCategory}
  categoryAllLabel={t('common.allCategories')}
  categoryTestIdPrefix="page-category-filter"
  topRowActions={/* optional: sort select, view toggle, add button */}
  footer={
    <div className="min-h-[1.25rem] flex items-center justify-end">
      <span className="text-xs text-base-content/50 tabular-nums">{filtered.length} / {items.length}</span>
    </div>
  }
/>
```

> **Test ids:** keep `searchTestId` and `categoryTestIdPrefix` stable per page (`pm-…`, `sale-…`, `kds-…`) so existing tests and the e2e suite keep working.

---

## Other shared building blocks

| Component | Location | Used by |
|-----------|----------|---------|
| `SearchInput` | `components/ui/SearchInput.tsx` | ProductFilterBar, KDS, Notes, Roles |
| `CategoryFilterPills` | `components/pos/CategoryFilterPills.tsx` | ProductFilterBar, Home |
| `Card` | `components/ui/Card.tsx` | everywhere |
| `Modal` + `useModal` | `components/ui/Modal.tsx` / `ModalProvider.tsx` | see [modals.md](modals.md) |
| `DataTable` | `components/ui/DataTable.tsx` | see [tables-grid.md](tables-grid.md) |
| `useDebouncedSearch` | `hooks/useDebouncedSearch.ts` | any filterable page |

---

## References

- [`docs/pages-options.md`](pages-options.md) — per-page option inventory
- [`docs/tables-grid.md`](tables-grid.md) — grid classes used under the bar
- [`docs/forms.md`](forms.md) — the `.field field--sm` selects used in `topRowActions`
- `src/test/pages/ProductManager.test.tsx`, `src/test/pages/Sale.test.tsx` — behaviour specs
