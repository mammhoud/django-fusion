---
# yaml-language-server: $schema=schemas/feature.schema.json
Object type:
    - Feature
Backlinks:
    - POS
Tags:
    - integration
    - crm
    - payments
Status: Planned
Links:
    - CRM
---

# Integration — External System Connectivity

> **Type:** Feature ✨
> **Description:** External system integration — CRM connections, payment gateways, accounting software, and third-party API bridges.

---

## Overview

The Integration layer connects POS to external business systems:

| System | Integration Type | Status |
|--------|-----------------|--------|
| **CRM** | Customer data sync — create/update contacts from sales | Planned |
| **Payments** | Stripe, Square, PayPal payment gateway integration | Planned |
| **Accounting** | QuickBooks, Xero invoice/transaction export | Planned |
| **Email** | Transactional emails — receipts, invoices, notifications | Planned |
| **SMS** | Order status updates, promotional messaging | Planned |

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Edition** | Full and Cloud |
| **Color** | Indigo (#6366f1) / Violet (#8b5cf6) — representing bridges and connections |
| **CRM Source** | Custom Form submissions + POS sales data |
| **Auth** | API tokens per integration |

---

## Color Palette: Integration Indigo

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#6366f1` (Indigo-500) | Integration status, connection badges |
| Surface | `#eef2ff` / `#1e1b4b` | Integration panels (light/dark) |
| Accent | `#8b5cf6` (Violet-500) | Active integration indicators |
| Success | `#22c55e` (Green-500) | Connected / syncing |
| Danger | `#ef4444` (Red-500) | Disconnected / error |

---

## Related Docs

- → `custom-form.md` — Form builder for CRM data collection
- → `pos-cloud-integrations.md` — Cloud-specific integrations
- → `../../plans/product-development.md` — Integration roadmap
- → `../README.md` — Master index
