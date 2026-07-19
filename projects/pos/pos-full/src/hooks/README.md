# 📁 POS-KO Hooks (`src/hooks/`)

> **Related Names:** `hooks`, `useDebouncedSearch`, `useStatusToast`, `debounce`, `toast`, `notifications`
> **Tags:** #react #hooks #debounce #toast

2 custom React hooks for cross-component logic reuse.

```
hooks/
├── useDebouncedSearch.ts  # 🟢 Debounced search with 300ms default
└── useStatusToast.ts      # 🟢 Toast notification auto-dismiss manager
```

## Customization Tags

| Hook | Tag | How to customize |
|------|-----|-----------------|
| `useDebouncedSearch.ts` | 🟢 `customizable` | Change delay, add filters |
| `useStatusToast.ts` | 🟢 `customizable` | Add toast types, positions, durations |

## useDebouncedSearch

```typescript
const { query, setQuery, debouncedQuery } = useDebouncedSearch(300);

// query: immediate value (for input display)
// debouncedQuery: delayed value (for API calls)
// setQuery: update the search term
```

Used in pages with searchable tables: `Customers.tsx`, `Suppliers.tsx`, `ProductManager.tsx`, `Inventory.tsx`, `Transactions.tsx`.

## useStatusToast

```typescript
const { showToast, ToastContainer } = useStatusToast();

showToast({
  type: 'success',     // 'success' | 'error' | 'warning' | 'info'
  message: 'Saved!',
  duration: 3000,      // ms, default 3000
});
```

> 💡 **Tip:** Include `<ToastContainer />` in your page's JSX to render the toast UI.

## Reference

- [Pages →](../pages/README.md)
- [Components →](../components/README.md)
