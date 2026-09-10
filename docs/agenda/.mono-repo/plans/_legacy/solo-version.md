---
Object type: Plan
Tags: pos, solo, version, legacy
Status: In Development
---

# SOLO Version — Standalone POS Edition

> **Type:** Workspace 🏢
> **Emoji:** 🎋
> **Description:** The standalone, single-branch POS edition — full desktop application with LAN sync and embedded Python sidecar.

> **Legacy:** Archived with the deprecated version labels (`pos-mini` / `pos-solo` / `pos-full`). See `../../architecture/editions.md` for current edition scope.

---

## Overview

POS Solo is the middle-tier edition bridging Mini and Full:

| Aspect | Detail |
|--------|--------|
| **Platform** | Desktop (Tauri) + Sidecar (Python/Robyn) |
| **Database** | SQLite (local) |
| **Sync** | LAN — branch devices poll master server |
| **Tech Stack** | Rust (Tauri shell) → TypeScript (React UI) → Python (Django ORM + Robyn API) |

---

## Architecture Breakdown

### Rust Layer
Tauri desktop shell — window management, native file dialogs, system tray, and bridging to TypeScript frontend via Tauri commands.

### Python Sidecar (Django ORM + Robyn API)
Business logic layer — Django models for POS entities (Product, Sale, Employee), Robyn HTTP server exposing REST endpoints at port 8766. Handles all data persistence and LAN sync.

### TypeScript Frontend (React + Tauri)
UI layer built with React 19, connected to the sidecar via HTTP and to Tauri via `@tauri-apps/api`. State management via Redux, styling via Tailwind CSS v4 with theme system.

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Repopath** | `projects/pos/pos-solo/` |
| **Color** | Django Green (#0c4a6e deep teal) / Python Blue (#306998) — representing the Python/Django backend foundation |
| **Ports** | Sidecar: 8766, Tauri dev: 1420 |
| **Key Files** | `sidecar/server.py`, `src/App.tsx`, `src-tauri/src/lib.rs` |

---

## Color Palette: Solo Teal

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#0d9488` (Teal-600) | Solo branding, active states |
| Surface | `#f0fdfa` / `#134e4a` | Dashboard panels (light/dark) |
| Accent | `#14b8a6` (Teal-500) | Sidecar status indicators |
| Python Blue | `#306998` | Python/sidecar badge |
| Rust Orange | `#dea584` | Rust/Tauri badge |

---

## Related Docs

- → `free-version.md` — Free community version
- → `full-version.md` — Enterprise version
- → `../../architecture/editions.md` — Current editions
- → `../../architecture/editions.md` — Edition comparison
- → `../../guides/_index.md` — Guides index
- → `../../README.md` — Master index
