---
title: Formint POS — Feature Tracking
description: Feature lifecycle for Formint POS — shipped launch scope across the community, standard, professional, and cloud editions
navigation:
  title: Formint POS
  icon: i-lucide-store
object:
  type: "guide"
  id: "agenda.feature-tracking.formint-pos"
attributes:
  source_path: "agenda/feature-tracking/formint-pos.md"
  canonical_route: "/docs/en/agenda/feature-tracking/formint-pos"
  source_of_truth: "repository-markdown"
  owner: "workspace"
  status: "active"
tags:
  - structa-cloud
  - feature-tracking
  - pos
  - formints
links:
  - label: "Feature Tracking hub"
    to: "/agenda/feature-tracking"
    icon: "i-lucide-target"
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
---

# 🎯 Formint POS — Feature Tracking

> **Scope:** Feature lifecycle for the Formint POS editions (desktop, Android, iOS, cloud master).
> **Last updated:** 2026-09-12
> **Hub:** [`feature-tracking.md`](../feature-tracking.md) — lifecycle, status definitions, and the per-product index.

---

## ✅ Shipped — Launch Scope

**Multi-branch Management**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P0 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Offline branch operation, idempotent sync, permissions, and transfers — foundation for multi-location POS.

**Scope:** Branch model, offline operation, sync protocol, permission system.

**Acceptance criteria:**
- [ ] Multiple branches supported
- [ ] Offline operation with sync on reconnect
- [ ] Idempotent sync operations
- [ ] Branch-level permissions
- [ ] Item transfers between branches

**Notes:** Core multi-branch feature, shipped in Professional edition.

**Case study:** [`case-studies/pos-multi-terminal-sync.md`](../case-studies/pos-multi-terminal-sync.md)

---

**Kitchen Display System**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P0 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Station routing, ticket lifecycle, timers, and metrics — improves kitchen efficiency and order tracking.

**Scope:** KDS UI, station routing, ticket lifecycle states, timer tracking, kitchen metrics.

**Acceptance criteria:**
- [ ] Orders route to correct kitchen station
- [ ] Ticket lifecycle: new → preparing → ready → served
- [ ] Timer tracking per ticket
- [ ] Kitchen metrics displayed

**Notes:** Shipped in Professional edition.

---

**QR Menu**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P0 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Versioned localized menu, preview/publish workflow, branch/table QR codes — modern menu delivery.

**Scope:** Menu versioning, localization, preview/publish, QR code generation per branch/table.

**Acceptance criteria:**
- [ ] Menu versions managed
- [ ] Multiple languages supported
- [ ] Preview before publish
- [ ] QR codes per branch and table

**Notes:** Shipped in Professional edition.

**Case study:** [`case-studies/pos-qr-menu.md`](../case-studies/pos-qr-menu.md)

---

**Loyalty System**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Immutable points ledger, rewards, consent management, and reversals — customer retention.

**Scope:** Points ledger, reward definitions, consent capture, points reversal.

**Acceptance criteria:**
- [ ] Points earned per transaction
- [ ] Rewards redeemable
- [ ] Consent captured per regulations
- [ ] Points reversals handled

**Notes:** Shipped in Professional edition.

---

**API Access**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Versioned `/api/v1/` schemas, scoped API keys, sliding-window rate limits, webhooks — external integration capability.

**Scope:** API versioning, scoped keys, rate limiting, webhook delivery.

**Acceptance criteria:**
- [ ] `/api/v1/` endpoints documented
- [ ] API keys with scopes
- [ ] Rate limiting with sliding window
- [ ] Webhook delivery for key events

**Notes:** Shipped in Professional edition.

---

**Mobile Waiter**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Tableside orders, kitchen handoff, split/merge (`SaleGroup`), offline retry — improves service speed.

**Scope:** Mobile order UI, kitchen handoff protocol, sale grouping for split/merge, offline retry.

**Acceptance criteria:**
- [ ] Orders placed from mobile device at table
- [ ] Orders handed off to kitchen
- [ ] Sales can be split and merged
- [ ] Offline orders retry on reconnect

**Notes:** Shipped in Professional edition.

---

**POS-KO Gaming Center**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Token-based gaming sessions with stations, time tokens, start/pause/resume/stop with duration×rate billing, and waitlist queue.

**Scope:** Gaming session model, token system, station management, billing integration, waitlist.

**Acceptance criteria:**
- [ ] Gaming sessions start/pause/resume/stop
- [ ] Time-based token billing
- [ ] Station routing for games
- [ ] Waitlist queue for popular stations

**Notes:** Shipped in Full edition.

---

**Gift Cards**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Digital gift cards with issue, balance check, redeem with `GiftCardTransaction` ledger, reload, and disable.

**Scope:** Gift card model, transaction ledger, balance tracking, reload, disable.

**Acceptance criteria:**
- [ ] Gift cards can be issued
- [ ] Balance check API
- [ ] Redemption with ledger entry
- [ ] Reload and disable supported

**Notes:** Shipped in Professional+ edition.

---

**Table Management**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Restaurant floor layouts, order tracking, table CRUD, status lifecycle, occupy/clear with live sale link, floor summary, and reservation booking/lifecycle.

**Scope:** Floor layout editor, table model, status lifecycle, reservation system.

**Acceptance criteria:**
- [ ] Floor layouts configurable
- [ ] Tables have status: available, occupied, reserved
- [ ] Orders linked to tables
- [ ] Reservations booking and lifecycle

**Notes:** Shipped in Professional+ edition.

---

**Delivery Integration**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Delivery platform connectors for Talabat/HungerStation with provider registry, outbound order dispatch with zone-based fee, status lifecycle, provider webhook ingestion, and delivery KPIs.

**Scope:** Provider registry, order dispatch, zone-based fees, status lifecycle, webhook ingestion, KPIs.

**Acceptance criteria:**
- [ ] Talabat integration working
- [ ] HungerStation integration working
- [ ] Zone-based fee calculation
- [ ] Delivery status lifecycle
- [ ] Provider webhooks ingested
- [ ] Delivery KPIs available

**Notes:** Shipped in Professional+ edition.

---

**AI Forecasting**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Read-only advisory analytics with per-product demand projection (moving average + trend), stock/reorder recommendations, waste aggregation with cost, and sales movers/growth insights with recommendation strings.

**Scope:** Demand projection, stock recommendations, waste analysis, sales insights.

**Acceptance criteria:**
- [ ] Per-product demand projection
- [ ] Stock/reorder recommendations
- [ ] Waste aggregation with cost
- [ ] Sales growth insights with recommendations

**Notes:** Shipped in Professional/SaaS edition.

---

**Employee Scheduling**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Shift planning + time clock with weekly shift upsert, concrete week roster, staffing coverage, clock in/out/break, worked-hours, overtime, and pay estimate.

**Scope:** Shift model, time clock, roster management, hours calculation, pay estimation.

**Acceptance criteria:**
- [ ] Weekly shifts planned
- [ ] Concrete week roster generated
- [ ] Clock in/out/break tracked
- [ ] Worked hours + overtime calculated
- [ ] Pay estimate generated

**Notes:** Shipped in Professional edition.

---

**Customer Display**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Read-only customer-facing order confirmation with per-order display envelope (items, totals, table, kitchen-ticket status + ETA) and active-orders board feed with polling wall-screen page.

**Scope:** Customer display UI, order envelope, kitchen-ticket status, active-orders feed.

**Acceptance criteria:**
- [ ] Customer sees order confirmation
- [ ] Items, totals, table displayed
- [ ] Kitchen-ticket status + ETA shown
- [ ] Active-orders board feed
- [ ] Wall-screen polling page

**Notes:** Shipped in Professional edition.

---

**Self-checkout Kiosk**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Self-service kiosk mode with `KioskSession` + cart, catalog feed, touchscreen UI; checkout reuses the canonical `sale_checkout` surface (Sale/SaleItem/KitchenTicket + stock deduction).

**Scope:** Kiosk session model, cart management, catalog feed, touchscreen UI, checkout integration.

**Acceptance criteria:**
- [ ] Kiosk mode startable
- [ ] Cart management works
- [ ] Catalog feed displayed
- [ ] Touchscreen UI functional
- [ ] Checkout reuses sale_checkout surface

**Notes:** Shipped in Professional/SaaS edition.

---

**Inventory Forecasting**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Reorder-point planning + auto-reorder with per-product safety stock, reorder point, projected stock-out date, and suggested order quantity; `POST /forecast/inventory/reorder` materializes the advisory into `PurchaseOrder` drafts.

**Scope:** Safety stock model, reorder point calculation, stock-out projection, auto-reorder.

**Acceptance criteria:**
- [ ] Per-product safety stock configured
- [ ] Reorder point calculated
- [ ] Stock-out date projected
- [ ] Suggested order quantity provided
- [ ] Auto-reorder creates PurchaseOrder drafts

**Notes:** Shipped in Professional/SaaS edition.

---

**Cloud Dashboard**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | Multi-branch Management |

**Why it matters:** Web-based multi-branch management dashboard with sync queue retry/cancel, conflict resolve/dismiss, and activity feed over `/api/dashboard/*`.

**Scope:** Dashboard UI, sync queue management, conflict resolution, activity feed.

**Acceptance criteria:**
- [ ] Multi-branch view
- [ ] Sync queue retry/cancel
- [ ] Conflict resolve/dismiss
- [ ] Activity feed

**Notes:** Shipped in Professional/SaaS edition.

---

**Bolt Analytics Dashboard**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Self-contained HTML dashboard at `/apis/data/` with 6 KPI cards, live WebSocket updates, and sync event log viewer.

**Scope:** KPI cards, WebSocket live updates, sync event log.

**Acceptance criteria:**
- [ ] 6 KPI cards displayed
- [ ] Live WebSocket updates
- [ ] Sync event log viewer

**Notes:** Shipped in pos-cloud server.

---

**Sync Event Log Viewer**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** Fixed-position panel with 50-entry ring buffer, collapse, and reconnect indicator on bolt + admin dashboards.

**Scope:** Ring buffer log, collapse UI, reconnect indicator.

**Acceptance criteria:**
- [ ] 50-entry ring buffer
- [ ] Collapse/expand
- [ ] Reconnect indicator

**Notes:** Shipped in pos-cloud server.

---

**DataToken Sync Tagging**

| Field | Value |
|-------|-------|
| **Status** | ✅ Shipped |
| **Priority** | P1 |
| **Product** | Formint POS |
| **Owner** | — |
| **Target** | Done |
| **Depends on** | — |

**Why it matters:** django-fusion model for ordered sync row tagging with parent/child trees, progress tracking, and auto-untag.

**Scope:** Sync tagging model, parent/child tree, progress tracking, auto-untag.

**Acceptance criteria:**
- [ ] Rows tagged for sync
- [ ] Parent/child tree maintained
- [ ] Progress tracked
- [ ] Auto-untag on completion

**Notes:** Shipped in django-fusion library. 🔧

**Case study:** [`case-studies/data-token-sync-tagging.md`](../case-studies/data-token-sync-tagging.md)

---

## P2 — Planned (Empty)

No P2 features currently planned for Formint POS. The launch scope is complete.

---

## Remarks & Notes

- Status values are lowercase in the template but emoji-prefixed in tables for readability
- Priority alignment with [`feature-roadmap.md`](../../features/feature-roadmap.md) is mandatory — drift causes confusion
- Read [`../feature-tracking.md`](../feature-tracking.md) for the lifecycle, definitions, and the per-product index

<!-- AI-generated: review needed -->
