# Formint Standard — Documentation

> **Version:** 0.1.0 | **Stack:** Tauri 2 + React 19 + Rust/Diesel + SQLite
> **Repository:** [github.com/mammhoud/POS](https://github.com/mammhoud/POS)
> **Edition identity:** `formint-standard` (historically `formintA`)

<!-- AI-generated: review needed -->

## One docs project per edition

The Standard and Community editions share the same Tauri + React + Rust frontend,
so their documentation is **one shared docs project**. The canonical copy lives
in [`formint-community/docs/`](../formint-community/docs/); this directory keeps
only the edition-specific files and points at the shared docs.

## Edition-specific files (kept here)

| Document | Description |
|----------|-------------|
| **[Guides](guides.md)** | Setup, customization, deployment, troubleshooting (Standard bundle id `com.mammhoud.pos`) |
| **[i18n Gaps](i18n-gaps.md)** | Translation coverage report for this edition's locale files |
| **[Mobile concept](mobile-concept.html)** | Static mobile UI preview |

## Shared documentation (canonical in formint-community/docs/)

| Document | Description |
|----------|-------------|
| [Architecture](../formint-community/docs/architecture.md) | System design, data flow diagrams, FlyonUI integration, theme system |
| [Styling & UI Packages](../formint-community/docs/styling.md) | Full styling catalog — Tailwind v4, FlyonUI, Iconify, Framer Motion, themes |
| [Color Palette](../formint-community/docs/color-palette.md) | Theme variants, OKLCH tokens, custom color actions |
| [Forms & Inputs](../formint-community/docs/forms.md) | BEM `.field` system, inputs, selects, validation states |
| [Tables & Grids](../formint-community/docs/tables-grid.md) | `DataTable` component + responsive grid utilities |
| [Page Options](../formint-community/docs/pages-options.md) | Search/filter/sort/view options per page |
| [Shared Components](../formint-community/docs/shared-components.md) | `ProductFilterBar` and how to add it anywhere |
| [Modals](../formint-community/docs/modals.md) | Extended `Modal` + `useModal`/`ModalProvider`, htmx / Alpine.js option |
| [Database Schema](../formint-community/docs/database.md) | ERD, table reference, migration guide, seed presets |
| [Invoke Methods](../formint-community/docs/invoke-methods.md) | Complete Tauri `invoke()` catalog |
| [File Structure](../formint-community/docs/file-structure.md) | Full project tree with descriptions |
| [Commands](../formint-community/docs/commands.md) | Makefile, Tauri CLI, and dev commands reference |
| [Calculations](../formint-community/docs/calculations.md) | Sales, tax, delivery, payroll, loyalty formulas |
| [Roles & Permissions](../formint-community/docs/roles-permissions.md) | Permission flags, default roles, UI visibility rules |
| [Rust Code](../formint-community/docs/rust-code.md) | Diesel ORM schema, operation modules, hardware integration |
| [Customization](../formint-community/docs/customization.md) | Theme variants, product colors, receipts, i18n, presets |

## Project at a Glance

```
formint-standard/          (historically formintA)
├── src/                    # React 19 frontend
│   ├── components/         # 16 reusable UI components
│   ├── pages/              # 22 route-level pages
│   ├── contexts/           # React contexts (Theme, Auth, Language)
│   ├── hooks/              # Custom React hooks
│   ├── api/                # Tauri invoke wrappers
│   ├── i18n/               # Internationalization (5 languages)
│   └── test/               # Vitest tests
├── src-tauri/              # Rust/Tauri backend
│   ├── src/                # Rust source (lib.rs, operations/, db/)
│   ├── migrations/         # SQLite migrations
│   └── binaries/           # Server binaries
└── docs/                   # Edition-specific docs only (shared docs in community)
```

## Remarks & Notes

- The 18 shared docs (architecture, styling, database, commands, …) were
  byte-identical copies of the Community edition's docs and were deleted here;
  the Community directory is the single source. Edit them there.
- Do not re-copy shared docs into this directory — link to
  `../formint-community/docs/` instead.
- Edition identity and bundle identifiers differ per edition (`guides.md`
  documents Standard's); the shared docs are edition-agnostic.