---
Object type: Plan
Tags: formint-pos, tauri, desktop, native, plugins, kds, offline
Status: Planned
Type: Technical
Edition: Formint Professional
Related Plans: formint-pos-professional-plan, forge-migration
---

# Formint Desktop Tools

> **Description:** Native desktop capability plan for the Formint Tauri shell. This document describes tool responsibilities and user outcomes; dependency and permission details remain in the repository plan.

## Tool methods and use cases

| Tool | Method | Use case |
|---|---|---|
| Single instance | Focus the existing station and reject duplicate launches | Prevent two processes from writing the same local order database |
| Store | Persist device settings, drafts, window state, and preferences | Restore a waiter draft or KDS layout after restart without replacing SQLite |
| Notifications | Notify by category with permission-aware preferences | Alert kitchen staff about new tickets and managers about low stock |
| Global shortcuts | Register safe, configurable station actions | Open a sale, show KDS, lock a station, or reprint the last receipt quickly |
| System tray | Provide background status and quick actions | Keep a terminal available for alerts while allowing quick lock or quit |
| Window/menu controls | Manage native menus, fullscreen, always-on-top, and sizing | Put KDS on a dedicated second display and keep it visible |
| Positioning | Select a monitor and restore window placement | Move the kitchen display to the correct screen automatically |
| Logging | Collect structured, rotating support diagnostics | Resolve printer, sync, and station issues without collecting business data unnecessarily |
| Autostart | Launch a dedicated terminal at boot | Bring a cashier or kitchen station back after a power interruption |
| Localhost bridge | Offer a trusted local integration only when needed | Receive an order from a local device without becoming the cloud API |

## Guardrails

- Native tools call Formint domain services through typed commands; they do not become a second business-data store.
- SQLite and the sync ledger remain authoritative for local/offline operations.
- Cloud transport is outside this local plan and belongs only to `cloud.md`.
- Add a tool only after confirming Tauri version, capability permissions, platform support, licensing, and an acceptance test.
- Use reduced motion, keyboard access, Arabic RTL, touch sizing, and offline behavior in every relevant desktop workflow.

## Delivery order

1. Single instance, store migration, and notifications.
2. Shortcuts, tray, menus, and KDS second-screen behavior.
3. Logging, autostart, positioner, and persisted export scope.
4. Localhost bridge only after a real integration need is validated.

## Retirement gate

Forge native wiring is removable only after the selected Formint tools pass capability audits, platform smoke tests, frontend checks, offline draft recovery, visual tests, and one rollback release.

## Related

- → `formint-pos-professional-plan.md` — Product destination
- → `forge-migration.md` — Source parity gate
- → `cloud.md` — Cloud boundary
- → `../../../plans/editions/05-pos-client.md` — Detailed repository plan
- → `../objects/tool.md` — Tool object type
