---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreibfywbzuw6akoyowle2p23w7zokty27p2a4jsvgi3tb2e6r2k453q
---
# POS Editions Overview   
**Type:** Architecture 🏗️
T**ags: **#`pos-mini `#`pos-solo `#`pos-full `#`pos-cloud
`S**tatus: **Published
E**dition: **Mini, Solo, Full, Cloud   
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
|         Feature   <br> |           pos-mini   <br> |             pos-solo   <br> |          pos-full   <br> |        pos-cloud   <br> |
|:-----------------------|:--------------------------|:----------------------------|:-------------------------|:------------------------|
|     **Backend**   <br> |       Rust (Tauri)   <br> |       Django + Robyn   <br> |    Django + Robyn   <br> |     Django + DRF   <br> |
|    **Database**   <br> |             SQLite   <br> |               SQLite   <br> |            SQLite   <br> |       PostgreSQL   <br> |
|     **Desktop**   <br> |         ✅ Tauri v2   <br> |           ✅ Tauri v2   <br> |        ✅ Tauri v2   <br> |       ❌ Web only   <br> |
|        **Sync**   <br> |       ❌ Air-gapped   <br> |   ✅ LAN master/slave   <br> |     ✅ Cloud + LAN   <br> |          ✅ Cloud   <br> |
|       **Roles**   <br> |         Rust model   <br> |    Django Role model   <br> | Django Role model   <br> |     Django Admin   <br> |
|     **Offline**   <br> |           ✅ Always   <br> |            ✅ Partial   <br> |         ✅ Partial   <br> |         ❌ Online   <br> |
| **Branch Mgmt**   <br> |     ❌ Single store   <br> |      ✅ Branch master   <br> |    ✅ Multi-branch   <br> |   ✅ Multi-branch   <br> |
|      **Target**   <br> | Food truck / kiosk   <br> |    Single restaurant   <br> |  Restaurant chain   <br> |  Enterprise SaaS   <br> |

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
[POS Editions Overview](pos-editions-overview.md)    
