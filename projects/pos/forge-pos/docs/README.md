# Forge POS — Documentation

> **Version:** 0.1.0 | **Stack:** Tauri 2 + React 19 + Rust/Diesel + SQLite
> **Repository:** [github.com/mammhoud/POS](https://github.com/mammhoud/POS)

## Overview

Forge POS is a lightweight, offline-first Point of Sale desktop application built with **Tauri**, **React 19**, and **Rust/Diesel ORM**. It uses an embedded **SQLite** database — no external server or sidecar required.

---

## Documentation Index

| Document | Description |
|----------|-------------|
| **[Architecture](architecture.md)** | System design, data flow diagrams, FlyonUI integration, theme system |
| **[Styling & UI Packages](styling.md)** | Full styling catalog — Tailwind v4, FlyonUI, Iconify, Framer Motion, themes, bundle analysis |
| **[Database Schema](database.md)** | ERD, table reference, migration guide, seed presets |
| **[Invoke Methods](invoke-methods.md)** | Complete Tauri `invoke()` catalog — frontend calls & Rust handlers |
| **[File Structure](file-structure.md)** | Full project tree with descriptions |
| **[Commands](commands.md)** | Makefile, Tauri CLI, and dev commands reference |
| **[Guides](guides.md)** | Setup, customization, deployment, troubleshooting |
| **[Calculations](calculations.md)** | All formulas: sales, tax, delivery, payroll, loyalty |
| **[Roles & Permissions](roles-permissions.md)** | Permission flags, default roles, UI visibility rules |
| **[Rust Code](rust-code.md)** | Diesel ORM schema, operation modules, hardware integration |
| **[Customization](customization.md)** | Theme variants, product colors, receipts, i18n, presets |

---

## Quick Links

- **Getting Started:** See [Guides → Setup](guides.md#setup)
- **Architecture Overview:** See [Architecture → Data Flow](architecture.md#data-flow)
- **Database ERD:** See [Database → Entity Relationship Diagram](database.md#entity-relationship-diagram)
- **All Tauri Commands:** See [Invoke Methods](invoke-methods.md)
- **Makefile Commands:** See [Commands](commands.md)

---

## Project at a Glance

```
forge-pos/
├── src/                    # React 19 frontend
│   ├── components/         # 16 reusable UI components
│   ├── pages/              # 22 route-level pages
│   ├── contexts/           # React contexts (Theme, Auth, Language)
│   ├── hooks/              # Custom React hooks (2)
│   ├── api/                # Tauri invoke wrappers (chat, data, sidecar)
│   ├── utils/              # Utilities (invoice PDF, export)
│   ├── i18n/               # Internationalization (5 languages)
│   └── test/               # Vitest tests
├── src-tauri/              # Rust/Tauri backend
│   ├── src/                # Rust source
│   │   ├── lib.rs          # 80+ Tauri command registrations
│   │   ├── operations/     # 27 CRUD operation modules
│   │   └── db/             # Diesel models + schema
│   ├── migrations/         # SQLite migrations
│   └── binaries/           # Sidecar binaries
├── docs/                   # This documentation
└── scripts/                # Build, dev, CI scripts
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Desktop Shell** | Tauri 2 | Native window, file dialogs, system menus |
| **Frontend** | React 19 + TypeScript | UI components, routing, state |
| **Styling** | Tailwind CSS v4 + FlyonUI | Utility-first CSS with semantic components |
| **Animation** | Framer Motion v12 | Page transitions, micro-interactions |
| **i18n** | react-i18next + i18next | Multi-language support (5 languages) |
| **Charts** | Recharts | Analytics dashboards |
| **Backend** | Rust (Tauri commands) | Business logic, data access |
| **ORM** | Diesel | Type-safe SQLite queries |
| **Database** | SQLite (embedded) | Local data storage |
| **PDF** | jsPDF + jspdf-autotable | Receipt and invoice generation |

---

## Architecture Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                     Tauri Desktop App                             │
│                                                                   │
│  ┌─────────────────────────────────────┐  ┌────────────────────┐  │
│  │         React Frontend              │  │   Rust Backend     │  │
│  │                                     │  │                    │  │
│  │  ┌─────────┐  ┌──────────────────┐  │  │  ┌──────────────┐  │  │
│  │  │ Contexts │  │    Pages (22)    │  │  │  │  Operations  │  │  │
│  │  │ Auth     │  │  Home, Sale,     │  │  │  │  (27 modules)│  │  │
│  │  │ Theme    │  │  Settings, ...   │──┼──┼─>│              │  │  │
│  │  │ Language │  │                  │  │  │  │  ┌─────────┐ │  │  │
│  │  └─────────┘  └──────────────────┘  │  │  │  │  Diesel  │ │  │  │
│  │                                     │  │  │  │  ORM     │ │  │  │
│  │  ┌─────────┐  ┌──────────────────┐  │  │  │  └─────────┘ │  │  │
│  │  │  Hooks  │  │   Components     │  │  │  └──────────────┘  │  │
│  │  │ (2)     │  │   (16 reusable)  │  │  │                    │  │
│  │  └─────────┘  └──────────────────┘  │  │  ┌──────────────┐  │  │
│  │                                     │  │  │   SQLite DB  │  │  │
│  │  ┌─────────┐  ┌──────────────────┐  │  │  │ restaurant.db│  │  │
│  │  │ FlyonUI │  │  Tailwind CSS    │  │  │  └──────────────┘  │  │
│  │  │ JS/CSS  │  │  + Iconify       │  │  │                    │  │
│  │  └─────────┘  └──────────────────┘  │  └────────────────────┘  │
│  └─────────────────────────────────────┘                          │
└───────────────────────────────────────────────────────────────────┘
```
