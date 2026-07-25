---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreif2dvc2sijvzrsswrsusejjlj6e2epspt5n2eki6oqz6v5vlqhhca
---
# Sync Architecture   
**Type:** Architecture 🏗️
T**ags: **#`pos-solo `#`pos-full `#`pos-cloud `#`sync
`S**tatus: **Published
E**dition: **Solo, Full, Cloud   
 --- 
## Three-Tier Sync Model   
```
  pos-mini              pos-solo                pos-full
  ┌────────┐           ┌────────────┐          ┌──────────────┐
  │ Offline│           │  Branch    │          │  Cloud Sync  │
  │ Only   │           │  Master    │          │  Enterprise  │
  └────────┘           └─────┬──────┘          └──────┬───────┘
                             │ LAN Poll               │ HTTPS
                             ▼                        ▼
                      ┌────────────┐          ┌──────────────┐
                      │  Devices   │          │  Cloud API   │
                      │  (slaves)  │          │  (central)   │
                      └────────────┘          └──────────────┘

```
 --- 
## Tier 1: pos-mini — Air Gapped   
**Pattern:** No sync. All data is local to the device.   
```
[Device] ──→ [SQLite DB] ←── [All operations local]

```
- Database backups via `Export Database` / `Import Database`   
- Use case: food trucks, temporary events, remote locations   
   
## Tier 2: pos-solo — LAN Branch-to-Master   
**Pattern:** One master device collects data from branch devices over LAN.   
```
┌─────────┐     HTTP Poll     ┌──────────┐
│ Branch  │ ←─────────────── │ Master   │
│ Device  │ ────────────────→ │ (Server) │
└─────────┘   Sync Response  └──────────┘

```
**Flow:**   
```
Device → POST /sync/push → Master stores → Master responds with updates
Device → GET /sync/poll?since={ts} → Master returns changes since timestamp

```
**Models used:**   
- `SyncQueue` → Tracks pending sync items   
- `SyncLog` → Audit log of sync operations   
- `Node` → Branch device identity + last sync timestamp   
   
## Tier 3: pos-full — Cloud Enterprise   
**Pattern:** All devices sync to a central cloud API with conflict resolution.   
```
┌─────────┐     HTTPS/WSS      ┌──────────────┐
│ Branch  │ ←─────────────── │ Cloud API    │
│ Device 1│ ────────────────→ │ (Central)    │
└─────────┘                   │              │
┌─────────┐                   │ PostgreSQL   │
│ Branch  │ ←─────────────── │              │
│ Device 2│ ────────────────→ │ Admin Panel  │
└─────────┘                   └──────────────┘

```
**Conflict resolution:** Last-write-wins with merge for non-conflicting fields.   
 --- 
## Data Models   
```
Node {
  id          (PK)
  name        (varchar)
  device_id   (varchar, unique)
  last_seen   (datetime)
  is_master   (bool)
}

SyncQueue {
  id          (PK)
  node_id     (FK → Node)
  table_name  (varchar)
  record_id   (varchar)
  action      (varchar: create|update|delete)
  payload     (json)
  created_at  (datetime)
  synced_at   (datetime, nullable)
}

```
## Related Docs   
- → `editions-overview.md` — Edition comparison   
- → `references/sidecar-api.md` — Sync API endpoints   
- → `references/database-schema.md` — Full schema   
[Sync Architecture](sync-architecture.md)    
