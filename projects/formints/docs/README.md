# POS — Point of Sale System

> Structa Cloud multi-edition POS platform: Tauri + React/Rust
> **Last Updated:** 9 August 2026

## Editions

| Edition | Package | Directory | Description |
|---------|---------|-----------|-------------|
| **Community** | Formint (`formint-pos`) | [`formintA/`](../../formintA/) | Offline-first desktop POS — Astro 5 + React 19 + Tauri + Rust/Diesel, no sidecar |
| **Standard** | (merged into Pro) | `formint/` | Standalone tier — Django sidecar + cloud sync client (gated by config) |
| **Pro** | Formint POS Professional (`formint-pos`) | [`formint/`](../../formint/) | **Merged package** — Astro + Alpine + HTMX frontend, Django Ninja sidecar (48 models), django-bolt, Channels WebSockets, Unfold admin, Tauri shell |
| **Cloud** | pos-cloud | [`formintB/`](../../formintB/) | Hosted multi-terminal SaaS cloud master — full Django setup (viewsets + fusion + bolt), Astro + React 19 frontend |
| **pos-client** | POS Client | [`formintC/`](../../formintC/) | Vue 3 + Tauri desktop client + Django purchase-app backend + Astro (django-fusion) storefront |

> ⚠️ The former `pos-full` (Cloud Master) and `pos-solo` (Standalone) editions
> were merged into `formint/` (legacy React UIs removed; the Astro frontend is
> canonical). **Formint** is the canonical Professional POS product name. The
> repo layout is `formintA` / `formint` / `formintB` / `formintC` — the old
> `forge-pos`, `formint-pos`, `pos-client` and `pos-cloud` directory names are
> gone. See [`architecture/editions.md`](architecture/editions.md) for the full
> per-edition analysis.

## Quick Links

- [Architecture Overview](architecture/pos-architecture.md)
- [Editions Comparison](architecture/editions.md)
- [Getting Started](GETTING_STARTED.md)
- [Commands Reference](COMMANDS.md)
- [Sidecar v2](SIDECAR_V2.md)
- [Formint POS Package](../formint/README.md)
- [Migration Manifest](../formint/migration/compatibility-manifest.json)

## Tech Stack

- **Frontend:** Astro 5 + React 19 (Community / Cloud) · Astro + Alpine + HTMX (Pro) · Vue 3 (pos-client)
- **Backend:** Rust (Tauri/Diesel) + Python (Django sidecar / pos-cloud)
- **API (Pro):** Django Ninja + ninja-extra, django-bolt, django-fusion encoder/decoder
- **State:** zustand / RTK Query / Pinia
- **Desktop:** Tauri v2

## Directory Structure

```
projects/formints/
├── formintA/       # Community edition — Astro 5 + React 19 + Tauri + Rust/Diesel (offline-first)
├── formint/        # Pro edition (merged Standard) — Astro frontend + full Django sidecar + Tauri shell
├── formintB/       # Cloud edition (pos-cloud) — hosted Django master + Astro/React frontend
├── formintC/       # pos-client — Vue 3 desktop client + Django purchase-app + Astro storefront
├── docs/           # This documentation (docsify)
└── tests/          # Integration tests
```
