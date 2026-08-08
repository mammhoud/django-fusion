# POS — Point of Sale

> **Status:** 🟢 Active development — desktop POS in four editions
> **Tags:** #pos #tauri #rust #react #desktop
> **Stack:** Tauri 2 + Rust + React 19 + TypeScript + SQLite

Formints is a desktop point-of-sale application built on Tauri 2 + Rust with a
React/Vite frontend and SQLite storage. Four editions share one codebase.

---

## Editions

| Edition | Price | Description |
|---------|:-----:|-------------|
| **Community** | Free | Offline-first single terminal, open source |
| **Standard** | $119 one-time | Standalone with embedded sidecar, F&B tools, analytics |
| **Pro** | $79/yr | Multi-terminal with cloud master, WebSocket streaming |
| **Cloud** | Custom | Fully hosted multi-terminal with managed CRM |

---

## Variants (Directories)

| Directory | Edition | Description |
|-----------|---------|-------------|
| `formint-pos/` | Community + Standard + Pro | Main codebase: Astro frontend + Django sidecar |
| `formintA/` | Standard/Pro | Tauri 2 + React 19 + Rust backend |
| `formintB/` | Community | Standalone Tauri app |
| `formintC/` | Cloud | Cloud-hosted variant |

---

## Quick Start

### Community (Tauri Desktop)

```bash
cd projects/formints/formintB
npm install
npm run tauri dev
```

### Standard/Pro (FormintA)

```bash
cd projects/formints/formintA
npm install
npm run dev          # React/Vite frontend
npm run tauri dev    # Full Tauri desktop
```

### Full Stack (formint-pos)

```bash
cd projects/formints/formint-pos
# Frontend (Astro)
cd frontend && npm install && npm run dev
# Sidecar (Django)
cd sidecar && uv run --project ../.. python manage.py runserver
```

---

## Architecture

```
┌─────────────────────────────────────┐
│          Tauri 2 Shell               │
│  ┌──────────────┐  ┌──────────────┐ │
│  │ React 19 UI   │  │ Rust Backend  │ │
│  │ (Vite)        │  │ (Diesel ORM)  │ │
│  └──────┬───────┘  └──────┬───────┘ │
│         │                 │          │
│  ┌──────┴─────────────────┴───────┐ │
│  │        SQLite Database          │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
         │ (Standard/Pro only)
         ▼
┌─────────────────────────────────────┐
│     Django Sidecar (Python)          │
│     API + WebSocket + Cloud Sync     │
└─────────────────────────────────────┘
```

---

## Key Features

- **Offline-first** — SQLite local storage, syncs when connected
- **Payment types** — Cash, card, split payments
- **Inventory** — Stock control, adjustments, F&B menu support
- **Kitchen display** — KDS for food & beverage operations
- **Multi-currency** — Per-terminal currency and tax profiles
- **i18n** — English, French, Arabic (React i18next)
- **Invoice PDF** — Rust-powered PDF generation
- **Loyalty & rewards** — Points, tiers, voucher redemption

---

## Related

| Resource | Link |
|----------|------|
| Formints docs | [`formints/README.md`](../formints/README.md) |
| FormintA docs | [`formints/formintA/README.md`](../formints/formintA/README.md) |
| Landing product page | [`../landing-fusion/`](../landing-fusion/) |
| POS docs | [`../../docs/pos/`](../../docs/pos/) |
