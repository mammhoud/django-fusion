# POS Editions Overview

**Type:** Architecture 🏗️
**Tags:** `#pos-mini` `#pos-solo` `#pos-full` `#pos-cloud`
**Status:** Published
**Edition:** Mini, Solo, Full, Cloud

---

## Architecture Flow

```
                    ┌─────────────────────────────────┐
                    │         POS Editions            │
                    │  (Shared React Frontend Core)   │
                    └───────┬──────────┬──────────────┘
                            │          │
         ┌──────────────────┤          ├──────────────────┐
         ▼                  ▼          ▼                   ▼
   ┌──────────┐    ┌────────────┐ ┌──────────┐   ┌────────────┐
   │ pos-mini  │    │ pos-solo   │ │ pos-full  │   │ pos-cloud  │
   │ (Rust)   │    │ (Django)  │ │ (Django) │   │ (Django)  │
   │ SQLite   │    │ SQLite    │ │ SQLite   │   │ PostgreSQL│
   │ Tauri    │    │ Tauri     │ │ Tauri    │   │ Web App   │
   │ Offline  │    │ LAN Sync  │ │ Cloud    │   │ Multi-    │
   │ Only     │    │ Branch    │ │ Sync     │   │ tenant    │
   └──────────┘    └────────────┘ └──────────┘   └────────────┘
```

---

## Edition Comparison

| Feature | pos-mini | pos-solo | pos-full | pos-cloud |
|---------|----------|----------|----------|-----------|
| **Backend** | Rust (Tauri) | Django + Robyn | Django + Robyn | Django + DRF |
| **Database** | SQLite | SQLite | SQLite | PostgreSQL |
| **Desktop** | ✅ Tauri v2 | ✅ Tauri v2 | ✅ Tauri v2 | ❌ Web only |
| **Sync** | ❌ Air-gapped | ✅ LAN master/slave | ✅ Cloud + LAN | ✅ Cloud |
| **Roles** | Rust model | Django Role model | Django Role model | Django Admin |
| **Offline** | ✅ Always | ✅ Partial | ✅ Partial | ❌ Online |
| **Branch Mgmt** | ❌ Single store | ✅ Branch master | ✅ Multi-branch | ✅ Multi-branch |
| **Target** | Food truck / kiosk | Single restaurant | Restaurant chain | Enterprise SaaS |

---

## Key Differentiators

### pos-mini — Lightweight & Fast
- `Rust` → `Tauri` → `SQLite` stack
- No Python sidecar dependency
- Ideal: food trucks, small kiosks, pop-up shops

### pos-solo — Branch Ready
- `Django` → `Robyn sidecar` → `SQLite` stack
- LAN sync between branch devices
- One master device collects all branch data
- Ideal: single restaurant with multiple POS terminals

### pos-full — Enterprise Scale
- `Django` → `Robyn sidecar` → `SQLite` / `PostgreSQL`
- Cloud sync across branches
- Central admin dashboard
- Ideal: restaurant chains, franchises

### pos-cloud — Multi-tenant SaaS
- Pure web application (no Tauri)
- Multi-tenant isolation
- Subscription management
- Ideal: white-label POS service

---

## Data Flow (All Editions)

```
[React UI] ←→ [Tauri Rust Commands / HTTP API]
                  │
                  ▼
          [SQLite / PostgreSQL]
                  │
                  ▼
          [Sync Engine] ←→ [LAN / Cloud / None]
                  │
                  ▼
          [Admin Dashboard / Sidecar]
```

---

## Related Docs
- → `architecture/sync-architecture.md` — Sync models per edition
- → `architecture/role-system.md` — Role & permission models
- → `architecture/theme-system.md` — Theme variant system
- → `features/comparison-matrix.md` — Detailed feature comparison
