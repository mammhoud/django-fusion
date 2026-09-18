# Formints Community

> Free & open-source desktop point of sale — offline-first, single terminal.

<p align="center">
  <img src="https://img.shields.io/badge/license-AGPL--3.0-blue" alt="License"/>
  <img src="https://img.shields.io/badge/version-0.1.0-green" alt="Version"/>
</p>

**Formints Community** is the open-source, offline-first edition of the
Formints point of sale. Everything runs on one device — no server, no server,
no cloud. Your data stays in a local SQLite database (`restaurant.db`).

Built with **Tauri 2 + Rust/Diesel + React 19**.

## Editions

This repository ships the **Community** edition only. The commercial editions
(Standard, Pro, Cloud) live at [structa.cloud](https://structa.cloud) and add an
embedded Python server, multi-terminal cloud sync, a cloud CRM master, and
hosted operations.

## Features

- Offline-first mode — data stays on this device
- Sales, receipting + inventory
- Refunds & returns
- Payment types: cash, card, split
- ESC/POS thermal printer support
- Invoice PDF generation + advanced receipt templates
- i18n: English, French, Arabic (+ more locales)
- Role-based access control — 5 default roles
- Theme system — 5 variants with a Theme Studio
- KDS (Kitchen Display System)

## Quick start

```bash
pnpm install
cd src-tauri && cargo fetch && cd ..
pnpm dev          # Vite dev server at localhost:1420
pnpm dev:desktop  # Full Tauri desktop app
```

Seed the demo database:

```bash
pnpm db:seed   # or: make seed
```

## Testing

```bash
pnpm test                 # Vitest unit tests
pnpm test:e2e             # Playwright e2e
cd src-tauri && cargo test  # Rust tests
```

## Build

```bash
pnpm build:desktop  # .dmg / .msi / .AppImage
```

## License

**AGPL-3.0** — see [LICENSE](LICENSE). The Community edition is free and open
source; the commercial editions are sold separately at
[structa.cloud](https://structa.cloud).

## Links

- Website: https://structa.cloud
- Source: https://github.com/mammhoud/formint-community
