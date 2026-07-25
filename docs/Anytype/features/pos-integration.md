---
# yaml-language-server: $schema=schemas/feature.schema.json
Object type:
    - Feature
Backlinks:
    - Task
    - POS
Tags:
    - integration
    - pos-solo
    - pos-full
    - sync
Status: In Development
Edition: Solo, Full
---

# POS Integration — System Connectivity & APIs

> **Type:** Feature ✨
> **Description:** Integration points between POS editions — sidecar APIs, database sync, CRM linkage, and external system connectivity.

---

## Overview

POS Integration covers all connectivity between POS components:

| Integration | Source | Target | Protocol |
|-------------|--------|--------|----------|
| Frontend ↔ Sidecar | Tauri React UI | Python Robyn server | HTTP REST (port 8766) |
| Sidecar ↔ Database | Django ORM | SQLite / PostgreSQL | Django models |
| Solo ↔ Master | Branch device | Master server | HTTP poll |
| Full ↔ Cloud | Branch device | Cloud API | HTTPS + WebSocket |
| POS ↔ CRM | POS sales data | Customer records | API sync |

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Edition** | Solo and Full |
| **Color** | Sky (#0ea5e9) / Blue (#3b82f6) — representing connectivity and data flow |
| **Sidecar Port** | `8766` |
| **Sync Protocol** | HTTP REST with JSON payloads |

---

## Color Palette: Integration Sky

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#0ea5e9` (Sky-500) | API endpoints, connection status |
| Surface | `#f0f9ff` / `#0c4a6e` | Integration panels (light/dark) |
| Accent | `#3b82f6` (Blue-500) | Active sync indicators |
| Success | `#22c55e` (Green-500) | Connected status |
| Warning | `#eab308` (Yellow-500) | Reconnecting status |

---

## Related Docs

- → `pos-cloud-integrations.md` — Cloud integration details
- → `external-integration.md` — CRM integration
- → `../../architecture/sync-architecture.md` — Sync engine
- → `../../references/database-schema.md` — Sync models
- → `../../references/sidecar-api.md` — Sidecar API reference
- → `../README.md` — Master index
