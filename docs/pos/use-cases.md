# 🎯 POS — Use Cases

> **Superseded edition names.** This page uses the retired `Minimal` / `Solo` /
> `Full` tiers. Map them to the current chain: **Minimal → Community**,
> **Solo → Standard**, **Full → Pro/Cloud**. The scenarios below stay valid as
> deployment patterns; the canonical buyer guide and capability matrix live in
> [`docs/plans/editions/comparison.md`](../plans/editions/comparison.md).

---

## Minimal Edition (now Community) — Single Terminal POS

**Best for**: Small retail shops, market stalls, pop-up stores.

### Scenario: Corner Grocery Store

A small grocery store with one cash register and no internet:
- **Catalog**: ~500 products with barcodes
- **Sales**: 50–100 transactions/day
- **Hardware**: Single Windows laptop, USB barcode scanner, thermal printer
- **Offline**: Works without internet — SQLite stores everything locally
- **Setup**: `pnpm tauri build` → install `.exe` → create products → start selling

### What Minimal CAN Do

| Capability | How |
|------------|-----|
| Product catalog | CRUD with barcode scanning |
| Sales orders | Create, view, print receipt |
| Cash register | Open/close sessions, track cash |
| Basic reporting | Daily sales totals, top products |
| Tax rates | Configurable per product/category |
| Dark mode | Toggle in settings |

### What Minimal CANNOT Do

- Multi-terminal (no sync)
- Customer management
- Inventory tracking across locations
- Cloud backup or CRM sync
- Purchase orders or supplier management

---

## Solo Edition — Smart Standalone with Cloud Sync

**Best for**: Mid-size retail, cafes, restaurants with online presence.

### Scenario: Neighborhood Cafe Chain

A cafe with 2 locations, each running independently but syncing to a cloud CRM:
- **Catalog**: ~200 products (menu items, modifiers)
- **Sales**: 200–400 transactions/day per location
- **Hardware**: Windows tablets at each counter
- **Online**: Syncs sales + customers to Cloud CRM every 60 seconds (Standard sync client → Cloud master)

### What Solo ADDS Over Minimal

| Capability | How |
|------------|-----|
| Customer profiles | Name, phone, order history |
| Cloud CRM sync | Push products, sales, customers to cloud |
| Django admin portal | Web-based product/category management |
| Node API endpoints | Programmatic access to POS data |
| Discount rules | Percentage/flat/buy-X-get-Y |
| Payment methods | Cash, card, mobile, tab |

### Solo Sync Architecture (now Standard → Cloud)

```
POS Terminal (Tauri)
    │ invoke() (calls Rust commands)
    ▼
Rust Core (lib.rs) + offline sync queue
    │ flush pending sync
    ▼
Cloud master (:8082 / Django)   ← products, sales, customers
    ▼
Products, Sales, Customers DB
```

---

## Full Edition (now Pro/Cloud) — Multi-Terminal Enterprise

**Best for**: Supermarkets, department stores, warehouses with multiple POS stations.

### Scenario: Supermarket with 10 Checkout Lanes

A supermarket with 10 checkout stations, warehouse management, and real-time inventory:
- **Catalog**: 10,000+ products with variants and attributes
- **Sales**: 2,000+ transactions/day
- **Hardware**: 10 Windows terminals + 1 server
- **Real-time**: Channels WebSocket sync (Pro multi-terminal / Cloud master)
- **Multi-terminal**: terminals sync through the Django master

### What Full ADDS Over Solo

| Capability | How |
|------------|-----|
| Multi-warehouse | Stock levels per location |
| Purchase orders | Supplier procurement tracking |
| Multi-terminal sync | All stations share one sidecar server |
| Real-time WebSocket | Inventory changes broadcast instantly |
| Cloud CRM master | Full bidirectional sync + admin |
| Advanced reporting | Sales per terminal, per cashier, per hour |
| Role-based access | Admin, manager, cashier roles |
| Barcode scanning | Batch scanning, inventory counts |

### Full Architecture (now Pro/Cloud)

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Terminal 1   │  │ Terminal 2   │  │ Terminal N   │
│ (Tauri)      │  │ (Tauri)      │  │ (Tauri)      │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │ sync push + WebSocket (Channels)
              ┌──────────▼──────────┐
              │  Django master      │
              │  (Pro :8767 / Cloud)│
              └──────────┬──────────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
┌────▼─────┐    ┌────────▼──────┐    ┌───────▼──────┐
│ SQLite   │    │ Django ORM    │    │ Cloud sync   │
│ pos.db   │    │ (formint_cloud)│   │ queue/broker │
└──────────┘    └───────────────┘    └──────────────┘
```

---

## Gaming Center Use Case (POS-KO)

**Best for**: Gaming cafes, LAN centers, esports arenas.

### Scenario: Gaming Center with 20 Stations

- **Token-based sessions**: Buy time tokens, start/pause/resume sessions
- **Station management**: Assign PCs, track occupancy, manage queues
- **Integrated billing**: Charge by time (hourly/flat), print session receipts
- **Scheduling**: Book future sessions, recurring time slots

| Feature | Description |
|---------|-------------|
| Token purchase | Buy 1hr, 3hr, day-pass, monthly |
| Session tracking | Start/pause/resume per station |
| Queue management | Waitlist with estimated wait time |
| Station status | Available, occupied, maintenance |
| Session billing | Auto-calculate cost from duration × rate |

---

## Edition Selection Guide

| Your Business | Recommended Edition |
|---------------|-------------------|
| Single register, offline, <500 products | **Community** |
| 1–3 registers, want money/tax/roles/export, need customer tracking | **Standard** |
| 3+ registers, KDS/tables/delivery/loyalty, purchase orders | **Pro** |
| Multi-branch chain, hosted sync + monitoring | **Cloud** |
| Retail shop with own catalog + online storefront | **Client** |
| Gaming cafe, LAN center, token-based time billing | **Pro (POS-KO)** |

---

## Related

| Topic | Path |
|-------|------|
| POS configuration | [`configuration.md`](configuration.md) |
| POS editions | [`editions.md`](editions.md) |
| POS features | [`features.md`](features.md) |
| POS infrastructure | [`infrastructure.md`](infrastructure.md) |
