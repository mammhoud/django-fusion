---
Object type: Edition
Tags: edition, formint, community, free, pos, rust
Status: Completed
Related Features: pos-system, pos-offline
Related Plans: formint-pos-professional-plan
Related Research: pos-market-research
---

# Formint Community — Free Self-Hosted Core POS

> **Description:** The free/self-hosted restaurant POS core — Astro 5 + React 19 desktop app over Tauri 2 + Rust/Diesel (SQLite, `restaurant.db`), offline-first, no sidecar.

## Scope

- Refunds & returns (`refund_sale` Rust command + UI)
- Offline-first mode indicator
- Categories, products, sales, sale items, payments, ingredients/recipes, inventory, employees, payroll, loyalty, kitchen tickets
- 31-table SQLite schema (see diagram package for the ERD)

## Boundaries

- No Django sidecar (Community is the direct Rust/SQLite edition)
- No multi-currency, tax profiles, custom roles, or export — those are Standard+

## Evidence

- ✅ Done (per `docs/plans/editions/` chain status)
- `cargo test` + `pnpm test` green
- Plan: `../../../plans/editions/01-community.md`

## Related

- → `formint-standard.md` — Next tier in the chain
- → `../features/pos-system.md` — POS documentation method
- → `../../diagrams/rust-sqlite-er.md` — Diesel schema ERD
- → `../objects/edition.md` — Edition object type