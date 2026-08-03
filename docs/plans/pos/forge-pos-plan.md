# Execution Plan — Remaining Forge POS Work
> **Tags:** #pos #forge-pos #planning #tauri
> **Updated:** 2026-08-02 — completed plans archived to `../legacy/pos/`; this file tracks only pending work.

## Completed (archived)

- **UI Enhancement Master Plan** (17 sections: theme system, alignment, ThemeToggle select, circular images, dense grids, Notes/receipt enhancement, RTL DataTable, StatCard compact/skeleton, dashboard cards, translations, currency context, Iconify→Heroicons, preloading) — ✅ done, archived in [`../legacy/pos/forge-pos-ui-enhancement-master.md`](../legacy/pos/forge-pos-ui-enhancement-master.md)
- **Task Status snapshot** (roles/branding/merged pages/SideNav/theme/settings/auth/home/sale/UIUX) — ✅ done, archived in [`../legacy/pos/forge-pos-tasks-status.md`](../legacy/pos/forge-pos-tasks-status.md)
- **Enhancement Plan** (component reorg, migration runner) — ✅ Plan 1 & Plan 3 done, archived in [`../legacy/pos/forge-pos-enhancement.md`](../legacy/pos/forge-pos-enhancement.md)
- **KDS P2 batch** — time-elapsed progress bar, overdue badge, 'overdue-first' sort, mute 30 min, chime dropdown — ✅ all implemented in `KitchenDisplay.tsx`
- **Motion cleanup** — framer-motion fully removed; all dead `initial/animate/exit/transition` props stripped across ~20 files; spinners converted to `animate-spin` — ✅

## Priority Order (Expected Risk Reduction × Effort)

### P2 — High-impact, moderate-effort
- [x] `useApiMutation` hook — implemented in `src/hooks/useApiMutation.ts` + tests; adopted by Customers.tsx & Suppliers.tsx

### P3 — Medium impact
- [ ] Extend events to customers/employees CRUD
- [ ] Live indicator badge in Sale.tsx (product-updated pulse)
- [x] DataTable bulk actions — implemented in `DataTable.tsx` (bulkActions prop) + ProductManager (delete/category/type)
- [ ] DataTable inline category dropdown editor
- [ ] DataTable duplicate-product button

### P4 — Lower impact, higher effort
- [ ] `preloadOnRoutePattern` hook
- [ ] `link rel=modulepreload` tags
- [ ] Tauri notification plugin (OS notifications with action buttons)
- [ ] `register_crud!` on remaining CRUD entities (currently only products/categories/ingredients/recipes use the macro)
- [ ] `useApiMutation` optimistic updates
- [x] SQLite WAL mode — enabled in `src-tauri/src/db/mod.rs` (journal_mode=WAL + synchronous=NORMAL + busy_timeout=5000 on every connection)

> **Note:** The old "Notes page / refactor receipt templates" task is complete — folded into the receipt-category system and the archived UI Enhancement Master Plan.
