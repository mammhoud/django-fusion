# POS — Point of Sale System

> Structa Cloud multi-edition POS platform: Tauri + React + Rust

## Editions

| Edition | Package | Branch | Description |
|---------|---------|--------|-------------|
| **pos-full** | Cloud Master | `generic` | Full-featured cloud POS with Django sidecar |
| **pos-solo** | Solo | `solo` | Standalone single-device POS |
| **pos-mini** | Mini | `mini` | Lightweight minimal POS |
| **formint-pos** | Formint POS Professional | `generic` | **Merged package** (pos-full + pos-solo) — Django Ninja + ninja-extra API with django-fusion encoder/decoder and data components (tables + forms) |

> **Formint** is the canonical Professional POS product name. `formint-pos/` is the
> new product boundary (Astro shell + Django data/API layer + Tauri). See
> [`../formint-pos/README.md`](../formint-pos/README.md) and
> [`../formint-pos/migration/compatibility-manifest.json`](../formint-pos/migration/compatibility-manifest.json).

## Quick Links

- [Architecture Overview](architecture/pos-architecture.md)
- [Editions Comparison](architecture/editions.md)
- [Getting Started](guides/quick-start.md)
- [API Reference](api/rest-api.md)
- [Formint POS Package](../formint-pos/README.md)
- [Migration Manifest](../formint-pos/migration/compatibility-manifest.json)

## Tech Stack

- **Frontend:** React + TypeScript + Vite + TailwindCSS (editions) / Astro + Alpine + HTMX (formint-pos)
- **Backend:** Rust (Tauri) + Python (Robyn/Django sidecar)
- **API (formint-pos):** Django Ninja + ninja-extra, django-fusion encoder/decoder
- **State:** RTK Query + Pinia
- **Desktop:** Tauri v2

## Directory Structure

```
projects/pos/
├── pos-full/          # Cloud master edition
├── pos-solo/          # Standalone edition
├── pos-mini/          # Minimal edition
├── formint-pos/       # Merged package (Django Ninja API + fusion data components)
├── pos-client/        # Shared client library
├── shared/            # Cross-edition shared modules
├── docs/              # This documentation
├── assets/            # Shared assets
└── tests/             # Integration tests
```
