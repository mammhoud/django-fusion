# Execution Plan — Remaining Forge POS Work
> **Tags:** #pos #forge-pos #planning #tauri
> **Updated:** 2026-08-04 — Forge is a migration source for Formint Professional; this file tracks remaining parity work and retirement gates, not a separate product scope.

> **Canonical destination:** [`formint-pos-professional-plan.md`](formint-pos-professional-plan.md). Do not remove Forge features until the Formint transfer gates below pass.

## Completed (archived)

- **UI Enhancement Master Plan** (17 sections: theme system, alignment, ThemeToggle select, circular images, dense grids, Notes/receipt enhancement, RTL DataTable, StatCard compact/skeleton, dashboard cards, translations, currency context, Iconify→Heroicons, preloading) — ✅ done, archived in [`../legacy/pos/forge-pos-ui-enhancement-master.md`](../legacy/pos/forge-pos-ui-enhancement-master.md)
- **Task Status snapshot** (roles/branding/merged pages/SideNav/theme/settings/auth/home/sale/UIUX) — ✅ done, archived in [`../legacy/pos/forge-pos-tasks-status.md`](../legacy/pos/forge-pos-tasks-status.md)
- **Enhancement Plan** (component reorg, migration runner) — ✅ Plan 1 & Plan 3 done, archived in [`../legacy/pos/forge-pos-enhancement.md`](../legacy/pos/forge-pos-enhancement.md)
- **KDS P2 batch** — time-elapsed progress bar, overdue badge, 'overdue-first' sort, mute 30 min, chime dropdown — ✅ all implemented in `KitchenDisplay.tsx`
- **Motion cleanup** — framer-motion fully removed; all dead `initial/animate/exit/transition` props stripped across ~20 files; spinners converted to `animate-spin` — ✅

## Formint transfer inventory — mandatory before removal

| Capability | Formint destination | Transfer evidence required | Forge status |
|---|---|---|---|
| KDS timers, overdue-first, chime/mute, stations, bump/recall | Formint KDS contract | Offline ticket, notification, second-screen, and visual tests | ✅ Source behavior documented; Formint implementation required |
| Loyalty/customer behavior | Formint loyalty ledger and customer profiles | Ledger idempotency, refund/reversal, consent, and branch tests | 🟡 Transfer required |
| Combo/composite items | Formint catalog/order-line snapshots | Required choices, substitutions, extras, tax, refund, KDS snapshot tests | 🟡 Transfer required |
| Modifiers and item extras | Formint modifier groups and extras | Price/quantity/offline retry and receipt/KDS parity tests | 🟡 Transfer required |
| Notes and receipt templates | Formint line/kitchen/customer/internal notes | Visibility, localization, receipt/KDS separation, migration tests | ✅ Source behavior documented; Formint implementation required |
| Semantic colors and responsive UI | Formint shared design tokens/assets | Light/dark, Arabic RTL, phone/tablet/desktop/second-screen visual matrix | ✅ Source baseline archived |
| Tauri native plugins | Formint Tauri shell | Platform smoke tests and capability audit | 🟡 Transfer required |

**Removal rule:** a Forge implementation can be deleted only after the matching Formint feature is implemented, migrated, tested, documented, archived, and available in a rollback release. “Documented” or “planned” alone is not sufficient.

## Latest Forge design baseline to preserve

- Semantic theme tokens instead of hardcoded colors; consistent primary/secondary/danger/ghost buttons and border colors.
- Light/dark/system modes, theme variants, high-contrast status states, Arabic RTL alignment, and reduced-motion behavior.
- Dense responsive grids and tables with mobile stacking, keyboard navigation, focus rings, skeletons, empty/error/offline states, and accessible labels.
- Circular product/avatar imagery, compact stat cards, currency context, consistent icon sizing, and print/receipt styling.
- KDS elapsed-time progress, overdue indicators, station columns, mute/chime controls, second-screen positioning, and touch-friendly controls.

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

> **Note:** Notes and receipt templates are not removable scope. They are transferred to Formint's note/template contract first; the archived Forge implementation remains until the transfer inventory passes.

## Forge retirement checklist

- [ ] Formint combo/composite items, modifiers, extras, notes, receipts, KDS, and loyalty implementations are available in a release build.
- [ ] Data and fixture migration preserves stable IDs, historical order-line snapshots, and receipt/KDS behavior.
- [ ] Formint light/dark/RTL/responsive visual regression matrix passes.
- [ ] Formint Tauri plugin equivalents pass platform and capability tests.
- [ ] POS Full/Solo/Forge compatibility and offline/reconnect tests pass.
- [ ] Dead-code report identifies no active dependency on the Forge paths being removed.
- [ ] Archive, deletion manifest, rollback installer, and release notes are complete.
