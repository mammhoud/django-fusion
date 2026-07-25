---
# yaml-language-server: $schema=schemas/page.schema.json
Object type: Guide
Tags: pos-mini, pos-solo, pos-full, setup
Status: Published
Category: Setup
---

# Guides — Setup & Quick Start

> **Type:** Guide 📘
> **Environment setup for all POS editions with project color references.**

---

## Project Color Guide

Each edition has a distinct color identity reflected in its UI theme:

| Edition | Primary Color | Hex | Vibe |
|---------|--------------|-----|------|
| **pos-mini** | Rust Red | `#f7524a` | Fast, minimal, lightweight — like the Rust language it's built on |
| **pos-solo** | Deep Teal | `#0d9488` | Balanced, reliable, standalone — Python/Django green influence |
| **pos-full** | Gold | `#eab308` | Premium, scalable, enterprise — representing business value |
| **pos-cloud** | Sky Blue | `#0ea5e9` | Cloud-native, connected, SaaS — accessible from anywhere |

When setting up, the theme system will use these as the base accent colors.

---

## pos-mini Setup

**Color:** Rust Red (#f7524a) — lightweight and minimal

```
cd projects/pos/pos-mini

# Install frontend deps
pnpm install

# Seed database
pnpm db:seed

# Dev (browser only — no Tauri APIs)
pnpm dev

# Dev (full desktop app)
pnpm dev:desktop

# TypeScript check
npx tsc --noEmit
```

The Mini edition uses SQLite locally with no sync. Perfect for food trucks, kiosks, and pop-up shops where simplicity is key.

---

## pos-solo Setup

**Color:** Deep Teal (#0d9488) — balanced and standalone

```
cd projects/pos/pos-solo

# Frontend
pnpm install

# Sidecar (Python + uv)
cd sidecar
uv sync          # Install Python deps
uv run pytest    # Run tests

# Dev
cd ..
pnpm dev          # Frontend only
pnpm dev:desktop  # Full app + sidecar
```

The Solo edition adds a Python sidecar (Django ORM + Robyn API) for LAN sync. Suitable for single restaurants with multiple POS terminals.

---

## pos-full Setup

**Color:** Gold (#eab308) — premium and enterprise

```
cd projects/pos/pos-full

# Same as pos-solo:
pnpm install
cd sidecar && uv sync
cd .. && pnpm dev:desktop
```

The Full edition extends Solo with cloud sync, multi-branch management, and CRM integration.

---

## Sidecar Quick Start (uv)

```bash
# Sidecar uses uv for Python dependency management
cd projects/pos/pos-{solo,full}/sidecar

uv sync                          # Install from pyproject.toml
uv run python3 server.py          # Start sidecar
uv run pytest                     # Run tests
uv add django                     # Add dependency
uv add --dev pytest               # Add dev dependency
```

### pyproject.toml Structure

```toml
[project]
name = "pos-sidecar"
dependencies = [
    "django>=5.1,<6",
    "robyn>=0.60,<1",
]
requires-python = ">=3.11"
```

---

## Environment Check

```bash
# Verify setup
python3 --version    # ≥ 3.11
uv --version         # uv package manager
node --version       # ≥ 18
pnpm --version       # ≥ 8
cargo --version      # Rust (Tauri builds)
```

---

## Related Docs

- → `development.md` — Development workflow
- → `theming.md` — Theme customization with color palettes
- → `deployment.md` — Deployment guide
- → `install/macos.md` — macOS install guide
- → `install/linux.md` — Linux install guide
- → `install/windows.md` — Windows install guide
- → `../architecture/editions.md` — Choose your edition
- → `../README.md` — Master index
