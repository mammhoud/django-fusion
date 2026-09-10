---
Object type: Plan
Tags: formint-pos, pos, professional, restaurant, product, roadmap, migration, arabic-first
Status: Active
Type: Roadmap
Edition: Formint Professional
Related Features: pos-system, pos-offline, integrations
---

# Formint POS — Professional Edition

> **Description:** Canonical Anytype summary of the Professional restaurant POS. The repository plan remains the detailed engineering source; this object records product boundaries, methods, use cases, and release gates.

## Product intent

Formint is the commercial successor to POS Full and the destination for POS Solo and Forge parity. It serves restaurants, cafés, cloud kitchens, chains, and franchises with Arabic-first, RTL, offline-capable operations.

## Edition contract

| Area | Community | Formint Professional | POS Cloud |
|---|---|---|---|
| Core POS, catalog, inventory, reports | Included | Included | Included |
| Multi-branch, KDS, QR Menu | — | Included | Included |
| Loyalty, API access, mobile waiter | — | Included | Included |
| Hosted billing, backups, tenant controls | — | Optional | Included |

## Methods and use cases

| Method | Responsibility | Use case |
|---|---|---|
| Branch management | Publish catalogs, permissions, stock, and reports by branch | A chain manager compares branches while each branch can keep selling offline |
| KDS workflow | Route tickets to stations; track queued, preparing, ready, and recalled states | Kitchen staff finish orders without returning to the cashier |
| Menu publishing | Version localized menus and expose branch/table QR links | Guests scan a current Arabic or English menu |
| Loyalty ledger | Record earn, redeem, expiry, refund, and reversal events immutably | A customer receives correct rewards after an offline retry or refund |
| API access | Expose versioned, scoped resources and webhooks | A delivery, accounting, or analytics partner integrates without database access |
| Mobile waiter | Manage tables, drafts, modifiers, notes, and kitchen handoff | Waiters take orders from a phone or tablet during service |
| Restaurant catalog | Preserve combos, required choices, modifiers, extras, taxes, and snapshots | A meal deal remains correct on the receipt and KDS after its catalog changes |
| Notes and templates | Separate line, kitchen, customer, internal, receipt, and preparation notes | Kitchen instructions do not leak onto a customer receipt |
| Offline sync | Queue idempotent events and surface conflicts | A branch reconnects after an outage without duplicate sales |

## Rendering and asset boundary

- Astro owns page shells, section structure, preloaders, skeletons, empty/error/offline states, transitions, and responsive layout.
- Alpine.js owns local interaction state such as carts, dialogs, table selection, and filters.
- HTMX requests narrowly scoped Django data fragments; Django does not return full layouts or loading components.
- Django and django-fusion own domain rules, permissions, forms, tables, routing, and lean data responses. Formint does not depend on Wagtail.
- A shared `assets/` directory sits beside `frontend/` and `backend/`; it contains canonical images, icons, fonts, styles, scripts, manifests, and visual fixtures.

## Design contract

Semantic color tokens, light/dark/system modes, high-contrast statuses, Arabic RTL, reduced motion, keyboard focus, touch targets, responsive tables, KDS second-screen layouts, and print/receipt styling are release requirements. Use Astro-owned skeletons and stable HTMX targets for loading behavior.

## Migration and removal gate

Forge and legacy Solo code remain available until each Formint contract has an implementation, migration fixture, acceptance test, visual evidence, rollback release, and dead-code report. Required parity includes KDS, loyalty, combos, modifiers, extras, notes, receipts, responsive design, semantic colors, and selected Tauri desktop capabilities.

## Related

- → `../../../plans/editions/03-pro.md` — Detailed repository plan
- → `forge-migration.md` — Forge transfer and retirement gates
- → `tauri-desktop.md` — Native desktop tools and use cases
- → `cloud.md` — Cloud-only transport boundary
- → `pos-market-research.md` — Edition market research
- → `../architecture/editions.md` — Edition architecture
- → `../objects/edition.md` — Edition object type
