# Execution Plan — All Feature Requests
> **Tags:** #pos #forge-pos #planning #tauri

## Priority Order (Expected Risk Reduction × Effort)

### P0 — Must fix before using pageTransition changes
- [ ] Remove unused `staggerItem` import from Home.tsx

### P1 — High-impact, low-effort
- [ ] React.memo on SideNav.tsx and ProductCard.tsx
- [ ] hover:scale-[1.02] active:scale-[0.97] CSS on 14 converted buttons

### P2 — High-impact, moderate-effort
- [ ] UseApiMutation hook (matches backend CRUD pattern, removes boilerplate)
- [ ] KDS time-elapsed progress bar (green→yellow→red fill)
- [ ] Overdue ticket count badge in KDS header
- [ ] 'Overdue first' sort option for KDS
- [ ] Mute 30min button for KDS

### P3 — Medium impact
- [ ] KDS notification-sound preference dropdown (3 chime variants)
- [ ] Extend events to customers/employees CRUD
- [ ] Live indicator badge in Sale.tsx (product-updated pulse)
- [ ] Replace motion.div dialog animations with CSS
- [ ] DataTable bulk actions (select + delete/change-category/change-type)
- [ ] DataTable inline category dropdown editor
- [ ] DataTable duplicate-product button

### P4 — Lower impact, higher effort
- [ ] preloadOnRoutePattern hook
- [ ] link rel=modulepreload tags
- [ ] Sidebar hover preloads
- [ ] Tauri notification plugin (OS notifications with action buttons)
- [ ] register_crud! on remaining 16 entities
- [ ] useApiMutation optimistic updates

> **Note:** The "Notes page / refactor receipt templates" task has been superseded by the comprehensive plan in [`forge-pos-ui-enhancement-master.md`](./forge-pos-ui-enhancement-master.md) (Section 6: Recipes Page → Notes Page Enhancement).

## Execution Order

Phase 1 — Stabilization (P0):
1. Remove unused staggerItem import

Phase 2 — Performance wins (P1):
3. SideNav.memo + ProductCard.memo
4. CSS hover/tap on converted buttons

Phase 3 — KDS enhancements (P2):
5. Time-elapsed progress bar
6. Overdue badge + sort + mute

Phase 4 — Data layer (P2-P3):
7. useApiMutation hook
8. Extend events
9. Bulk actions + inline editor
