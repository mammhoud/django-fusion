# 🎯 POS — Use Cases

> Real-world scenarios and deployment patterns for the POS Tauri desktop application across all three editions.

---

## Minimal Edition — Single Terminal POS

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
- **Online**: Syncs sales + customers to Cloud CRM every 60 seconds
- **Sidecar**: Embedded Python/Sanic API handles sync, Django portal for admin

### What Solo ADDS Over Minimal

| Capability | How |
|------------|-----|
| Customer profiles | Name, phone, order history |
| Cloud CRM sync | Push products, sales, customers to cloud |
| Django admin portal | Web-based product/category management |
| Node API endpoints | Programmatic access to POS data |
| Discount rules | Percentage/flat/buy-X-get-Y |
| Payment methods | Cash, card, mobile, tab |

### Solo Sync Architecture

```
POS Terminal (Tauri)
    │ pnpm tauri (calls Rust commands)
    ▼
Rust Core (lib.rs)
    │ spawn sidecar binary
    ▼
Sidecar API (:3000)     ──sync every 60s──▶   Cloud CRM (:8082)
    │ HTTP REST                                  │
    ▼                                            ▼
Django Portal (:8000)              Products, Sales, Customers DB
    │ Web admin UI
    ▼
SQLite (solo_portal.db)
```

---

## Full Edition — Multi-Terminal Enterprise

**Best for**: Supermarkets, department stores, warehouses with multiple POS stations.

### Scenario: Supermarket with 10 Checkout Lanes

A supermarket with 10 checkout stations, warehouse management, and real-time inventory:
- **Catalog**: 10,000+ products with variants and attributes
- **Sales**: 2,000+ transactions/day
- **Hardware**: 10 Windows terminals + 1 Ubuntu server
- **Real-time**: WebSocket broadcasts inventory changes instantly
- **Multi-terminal**: All stations share one sidecar API server

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

### Full Architecture

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Terminal 1   │  │ Terminal 2   │  │ Terminal 10  │
│ (Windows)    │  │ (Windows)    │  │ (Windows)    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │ HTTP REST + WebSocket
              ┌──────────▼──────────┐
              │  Sidecar API Server │
              │  (Rust HTTP :3000)  │
              │  WebSocket :3001    │
              └──────────┬──────────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
┌────▼─────┐    ┌────────▼──────┐    ┌───────▼──────┐
│ SQLite   │    │ Django ORM    │    │ Cloud CRM    │
│ pos.db   │    │ (Django 5.1)  │    │ :8766        │
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
| Single register, offline, <500 products | **Minimal** |
| 1–3 registers, want cloud backup, need customer tracking | **Solo** |
| 3+ registers, multi-location, real-time inventory, purchase orders | **Full** |
| Gaming cafe, LAN center, token-based time billing | **Full + POS-KO** |

---

## Related

| Topic | Path |
|-------|------|
| POS configuration | [`configuration.md`](configuration.md) |
| POS editions | [`editions.md`](editions.md) |
| POS features | [`features.md`](features.md) |
| POS infrastructure | [`infrastructure.md`](infrastructure.md) |
