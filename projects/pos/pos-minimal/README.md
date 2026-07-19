# POS Minimal

> Offline-first desktop POS — no sidecar, no external dependencies.

This is the **minimal edition** of POS. It includes the core point-of-sale
application with React 19, Tauri 2, Rust, and SQLite. No Python sidecar or
external API server required.

## What's Included

- React 19 + TypeScript frontend (Vite 7, Tailwind CSS 4)
- Tauri 2 + Rust backend (Diesel ORM, SQLite)
- 29 database tables for complete POS operations
- i18n support (English, French, Arabic)
- 22 page components, 13 UI components
- All core modules: POS, inventory, analytics, employees, payroll, kitchen display, recipes, reports, settings

## What's NOT Included

- Python/Sanic sidecar server
- REST API endpoints
- Invoice PDF generation
- Chat support widget
- Django ORM models
- WebSocket chat
- Cross-device data sync

> Need these features? Use [pos-solo](../pos-solo/) or [pos-full](../pos-full/).

## Quick Start

```bash
pnpm install
cd src-tauri && cargo fetch && cd ..
pnpm dev          # Vite dev server at http://localhost:1420
pnpm dev:desktop  # Full Tauri desktop app with hot-reload
```

## Build

```bash
pnpm build:desktop    # Production desktop app
pnpm build:android    # Android APK
pnpm build:ios        # iOS app (macOS only)
```

## Database

```bash
cargo run --manifest-path src-tauri/Cargo.toml --bin seed  # Seed with PRESET=all
```

## Environment

Copy `.env.example` to `.env` and configure:
```bash
SUPERUSER_EMAIL=admin@pos.local
SUPERUSER_PASSWORD=changeme
DATABASE_URL=restaurant.db
```
