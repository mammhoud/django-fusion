---
# yaml-language-server: $schema=schemas/feature.schema.json
Object type:
    - Feature
Backlinks:
    - Task
    - POS
    - pre-installed
    - offline
Tags:
- pre-installed
    - offline
    - pos-mini
    - pos-solo
Status: Complete
Edition: Mini, Solo, Full
---

# POS Offline — Air-Gapped Operation Mode

> **Type:** Feature ✨
> **Emoji:** 🔐
> **Description:** Full POS functionality without internet connectivity — critical for food trucks, temporary events, and remote locations.

---

## Overview

POS Offline enables complete sales processing without an internet connection. All data is stored locally and synced when connectivity is restored.

### Key Modes

| Mode | Edition | Description |
|------|---------|-------------|
| **Air-Gapped** | pos-mini | Fully offline — no sync capability by design |
| **Resilient** | pos-solo | LAN-connected but internet-independent |
| **Sync Queue** | pos-full | Offline transactions queued, synced when online |

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Edition** | All editions (mini, solo, full) |
| **Color** | Slate (#475569) / Stone (#78716c) — representing reliability and resilience |
| **Database** | Local SQLite (all editions) |
| **Sync Engine** | SyncQueue model (solo/full), no sync (mini) |

---

## Color Palette: Offline Slate

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#64748b` (Slate-500) | Offline mode indicator, queue status |
| Surface | `#f8fafc` / `#0f172a` | Offline UI panels (light/dark) |
| Accent | `#78716c` (Stone-500) | Queue item backgrounds |
| Warning | `#f59e0b` (Amber-500) | Pending sync indicator |

---

## Offline Capabilities

| Feature | Offline Support | Details |
|---------|----------------|---------|
| Sales Processing | ✅ Full | Create, void, and complete sales |
| Product Lookup | ✅ Full | Local product catalog cache |
| Inventory | ✅ Full | Stock tracking offline |
| Employee Login | ✅ Full | Local auth cache |
| Price Updates | ✅ Partial | Cached from last sync |
| Customer Lookup | ✅ Partial | Cached records |
| Cloud Reports | ❌ None | Only available online |

---

## Related Docs

- → `pos-mini.md` — Mini edition offline features
- → `pos-solo.md` — Solo edition LAN sync
- → `pos-full.md` — Full edition cloud sync
- → `../../architecture/sync-architecture.md` — Sync engine design
- → `../../references/database-schema.md` — SyncQueue model
- → `../README.md` — Master index
