# 📁 POS-KO Hooks (`src/hooks/`)

> **Related Names:** `hooks`, `useDebouncedSearch`, `useStatusToast`, `useApiMutation`, `useApi`, `debounce`, `toast`, `notifications`, `mutation`
> **Tags:** #react #hooks #debounce #toast #mutation

Custom React hooks for cross-component logic reuse.

```
hooks/
├── useDebouncedSearch.ts  # 🟢 Debounced search with 300ms default
├── useStatusToast.ts      # 🟢 Toast notification auto-dismiss manager
├── useApi.ts              # 🟢 Single + batch Tauri query hooks (loading/error/refetch)
└── useApiMutation.ts      # 🟢 Tauri CRUD mutation hook matching backend register_crud!
```

## Customization Tags

| Hook | Tag | How to customize |
|------|-----|-----------------|
| `useDebouncedSearch.ts` | 🟢 `customizable` | Change delay, add filters |
| `useStatusToast.ts` | 🟢 `customizable` | Add toast types, positions, durations |
| `useApi.ts` | 🟢 `customizable` | Add `listenTo` events, onSuccess/onError callbacks |
| `useApiMutation.ts` | 🟢 `customizable` | Override command names, create arg name, soft delete |

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

## useApiMutation

```typescript
const customerApi = useApiMutation<Customer>({
  singular: 'customer',   // → add_customer / update_customer / delete_customer
  createArg: 'customer',  // payload arg name (register_crud! macro uses 'data' by default)
  softDelete: false,      // true → soft_delete_{singular} instead of delete_{singular}
});

const saved = await customerApi.create(form, { onSuccess, onError });
const updated = await customerApi.update(id, form, { onSuccess, onError });
const ok = await customerApi.remove(id, { onSuccess, onError });

// In-flight + error state
const { isMutating, isCreating, isUpdating, isDeleting, error, resetError } = customerApi;
```

Derives `add_/update_/delete_{singular}` command names from the backend
`register_crud!` macro pattern and removes the repeated `try { invoke(...) }
catch { showError(...) }` boilerplate from CRUD pages. Used in `Customers.tsx`
and `Suppliers.tsx`.

## Reference

- [Pages →](../pages/README.md)
- [Components →](../components/README.md)
