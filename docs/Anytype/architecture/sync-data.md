---
# yaml-language-server: $schema=schemas/feature.schema.json
Object type:
    - Feature
Backlinks:
    - Task
    - POS
Tags:
    - sync
    - data
    - pos-solo
    - pos-full
Status: Complete
Edition: Solo, Full
Links:
    - CRM
---

# Sync Data — Cross-Device Data Synchronization

> **Type:** Feature ✨
> **Description:** Data synchronization engine — keeps POS devices in sync across LAN (Solo) and Cloud (Full) networks.

---

## Overview

Sync Data manages the queue-based synchronization between POS devices:

| Sync Mode | Edition | Pattern | Latency |
|-----------|---------|---------|---------|
| **LAN Poll** | pos-solo | Devices poll master server over local network | Near-real-time |
| **Cloud API** | pos-full | Devices sync via central cloud HTTPS API | Real-time |
| **Offline Queue** | mini/solo/full | Transactions queued locally, sync when reconnected | On reconnect |

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Edition** | Solo (LAN), Full (Cloud) |
| **Color** | Teal (#14b8a6) / Cyan (#06b6d4) — representing data flow and synchronization |
| **Core Models** | SyncQueue, Node, SyncLog |
| **Conflict Resolution** | Last-write-wins with merge for non-conflicting fields |

---

## Color Palette: Sync Teal

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#14b8a6` (Teal-500) | Sync status, active transfers |
| Surface | `#f0fdfa` / `#134e4a` | Sync panels (light/dark) |
| Accent | `#06b6d4` (Cyan-500) | Queue items, pending transfers |
| Success | `#22c55e` (Green-500) | Synced / complete |
| Warning | `#eab308` (Yellow-500) | Queue pending |
| Danger | `#ef4444` (Red-500) | Sync error / conflict |

---

## Related Docs

- → `sync-architecture.md` — Full sync architecture and data models
- → `editions.md` — Edition comparison
- → `../features/pos-integration.md` — System connectivity
- → `../references/database-schema.md` — SyncQueue, Node models
- → `../README.md` — Master index
