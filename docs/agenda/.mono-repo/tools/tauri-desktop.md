---
Object type: Tool
Tags: tool, tauri, rust, desktop
Status: Active
Category: Desktop
Related Features: pos-system
Related Plans: tauri-desktop
---

# Tauri 2 — Desktop Shell for POS Editions

> **Description:** The Tauri 2 + Rust desktop shell wrapping the Astro/React POS frontends, exposing native commands and local SQLite storage.

## Method

- Rust commands (`src-tauri/src/operations/*.rs`) handle sales, refunds, inventory, recipes, employees, payroll
- Diesel + SQLite (`restaurant.db`) with migrations on boot
- Community port 1420; Pro backend 8767 / frontend 4321 / bolt 8766

## Boundary

- No Robyn sidecar; the Django sidecar (Standard/Pro) is the only server
- Native behavior stays in each edition's `src-tauri/`

## Use case

Restaurant operator runs the offline-first POS desktop app; sales and inventory work with no network; sync queues flush when online.

## Related

- → `../plans/tauri-desktop.md` — Desktop tools plan
- → `../editions/formint-community.md` — Community edition
- → `../../diagrams/rust-sqlite-er.md` — Diesel schema ERD
- → `../objects/tool.md` — Tool object type