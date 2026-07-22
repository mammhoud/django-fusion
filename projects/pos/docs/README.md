# POS — Point of Sale System

> Structa Cloud multi-edition POS platform: Tauri + React + Rust

## Editions

| Edition | Package | Branch | Description |
|---------|---------|--------|-------------|
| **pos-full** | Cloud Master | `generic` | Full-featured cloud POS with Django sidecar |
| **pos-solo** | Solo | `solo` | Standalone single-device POS |
| **pos-mini** | Mini | `mini` | Lightweight minimal POS |

## Quick Links

- [Architecture Overview](architecture/pos-architecture.md)
- [Editions Comparison](architecture/editions.md)
- [Getting Started](guides/quick-start.md)
- [API Reference](api/rest-api.md)

## Tech Stack

- **Frontend:** React + TypeScript + Vite + TailwindCSS
- **Backend:** Rust (Tauri) + Python (Robyn/Django sidecar)
- **State:** RTK Query + Pinia
- **Desktop:** Tauri v2

## Directory Structure

```
projects/pos/
├── pos-full/          # Cloud master edition
├── pos-solo/          # Standalone edition
├── pos-mini/          # Minimal edition
├── pos-client/        # Shared client library
├── shared/            # Cross-edition shared modules
├── docs/              # This documentation
├── assets/            # Shared assets
└── tests/             # Integration tests
```
