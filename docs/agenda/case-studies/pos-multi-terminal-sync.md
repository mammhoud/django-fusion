---
title: Multi-terminal Sync — POS Case Study
description: Real-time WebSocket broadcast + pull changeset across POS terminals — architecture, decisions, and results
navigation:
  title: Multi-terminal Sync
  icon: i-lucide-link
object:
  type: "case-study"
  id: "case-studies.pos-multi-terminal-sync"
attributes:
  source_path: "agenda/case-studies/pos-multi-terminal-sync.md"
  canonical_route: "/docs/en/agenda/case-studies/pos-multi-terminal-sync"
  source_of_truth: "repository-markdown"
  owner: "formint-pos"
  status: "active"
tags:
  - structa-cloud
  - case-studies
  - pos
  - sync
  - websocket
  - realtime
  - architecture
links:
  - label: "Agenda home"
    to: "/agenda/main"
    icon: "i-lucide-clipboard-list"
  - label: "Feature Tracking — Multi-terminal Sync"
    to: "/agenda/feature-tracking/formint-pos"
    icon: "i-lucide-target"
  - label: "Feature Tracking — Offline Queue"
    to: "/agenda/case-studies/pos-offline-queue"
    icon: "i-lucide-arrow-right"
  - label: "Libraries README"
    to: "/libs/README"
    icon: "i-lucide-book"
---

# Multi-terminal Sync — POS Case Study

> **Date:** 2026-08-31 | **Status:** Active
> **Scope:** Real-time WebSocket broadcast + pull changeset (`/sync/changes`, `/sync/ack`, `/sync/trigger`) across POS terminals
> **Feature tracking:** [`feature-tracking/formint-pos.md`](../feature-tracking/formint-pos.md) § Multi-terminal Management
> **Related:** [`pos-offline-queue.md`](./pos-offline-queue.md), [`pos-qr-menu.md`](./pos-qr-menu.md)

---

## 1. Context

A restaurant POS needs multiple terminals (front counter, kitchen, bar, takeout) to stay in sync. When a sale is created at one terminal, others need to see it immediately — kitchen tickets appear, inventory updates, and branch transfers reflect across all terminals.

**Constraints:**
- Terminals may be on different networks (LAN, Wi-Fi, cellular)
- Some terminals operate offline (see [Offline Queue case study](./pos-offline-queue.md))
- Real-time is preferred but not required — eventual consistency acceptable
- Must handle terminal crashes and reconnects gracefully

---

## 2. Architecture

### 2.1 Sync Flow Overview

```mermaid
graph TB
    subgraph "POS Terminal A"
        TA["Terminal A<br/>(Front Counter)"]
        TA_APP["POS App"]
        TA_DB["Local SQLite"]
    end

    subgraph "POS Terminal B"
        TB["Terminal B<br/>(Kitchen Display)"]
        TB_APP["KDS App"]
        TB_DB["Local SQLite"]
    end

    subgraph "POS Terminal C"
        TC["Terminal C<br/>(Bar)"]
        TC_APP["POS App"]
        TC_DB["Local SQLite"]
    end

    subgraph "Sync Server"
        WS["WebSocket Server<br/>Broadcast"]
        SYNC_API["Sync REST API<br/>/sync/changes, /sync/ack, /sync/trigger"]
        CLOUD_DB["Cloud Database<br/>Source of truth"]
    end

    TA_APP -->|1. Sale created| TA_DB
    TA_APP -->|2. POST /sync/changes| SYNC_API
    SYNC_API -->|3. Store in cloud| CLOUD_DB
    SYNC_API -->|4. Broadcast via WS| WS
    WS -->|5. Push to terminals| TB_APP
    WS -->|5. Push to terminals| TC_APP
    TB_APP -->|6. Apply change| TB_DB
    TC_APP -->|6. Apply change| TC_DB
    TB_APP -->|7. POST /sync/ack| SYNC_API
    TC_APP -->|7. POST /sync/ack| SYNC_API
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-1.svg)

### 2.2 Changeset Protocol

```mermaid
sequenceDiagram
    participant T1 as Terminal A
    participant API as Sync API
    participant DB as Cloud DB
    participant T2 as Terminal B
    participant T3 as Terminal C

    T1->>API: POST /sync/changes
    Note over T1,API: { changes: [...], branch_id, timestamp }

    API->>DB: Store changeset
    DB-->>API: changeset_id

    API->>T2: WebSocket broadcast
    Note over API,T2: { changeset_id, branch_id }

    API->>T3: WebSocket broadcast
    Note over API,T3: { changeset_id, branch_id }

    T2->>API: POST /sync/ack
    Note over T2,API: { changeset_id, status: applied }

    T3->>API: POST /sync/ack
    Note over T3,API: { changeset_id, status: applied }

    API->>DB: Update changeset status
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-2.svg)

### 2.3 Pull Changeset (Polling Fallback)

```mermaid
graph LR
    T["Terminal<br/>offline or no WS"] -->|POST /sync/trigger| A["Sync API"]
    A -->|Returns| C["Changeset<br/>since last ack"]
    T -->|POST /sync/changes| A
    A -->|Store| DB["Cloud DB"]
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-3.svg)

### 2.4 Conflict Resolution

```mermaid
stateDiagram-v2
    [*] --> NoConflict: Single terminal changed
    NoConflict --> Applied: Ack received

    [*] --> ConflictDetected: Multiple terminals changed same record
    ConflictDetected --> ManualResolve: Show conflict UI
    ManualResolve --> Applied: User chooses winner
    ManualResolve --> AutoLastWrite: Auto-resolve (last write wins)
    AutoLastWrite --> Applied: Ack sent

    Applied --> [*]
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-4.svg)

---

## 3. Implementation

### 3.1 WebSocket Broadcast

**Endpoint:** WebSocket connection for real-time change notification.

**What it broadcasts:**
- `changeset_id` — unique identifier for the change batch
- `branch_id` — which branch the change originated from
- `change_type` — sale, inventory, transfer, etc.

**Reconnect behavior:** Terminals re-subscribe on reconnect and pull any changesets they missed since their last ack.

### 3.2 Pull Changeset API

```python
# POST /sync/changes — submit changes from terminal
{
    "branch_id": "branch-1",
    "timestamp": "2026-08-31T12:00:00Z",
    "changes": [
        {"type": "sale", "sale_id": "sale-123", "data": {...}},
        {"type": "inventory", "product_id": "prod-456", "delta": -1},
    ]
}

# POST /sync/ack — acknowledge changeset applied
{
    "changeset_id": "cs-789",
    "status": "applied",  # or "conflict"
    "conflict_info": {...}  # if status is conflict
}

# POST /sync/trigger — request pending changesets
{
    "branch_id": "branch-1",
    "since": "2026-08-31T11:00:00Z"  # last ack timestamp
}
```

### 3.3 Idempotent Sync

Changesets are idempotent — applying the same changeset twice doesn't duplicate data. Each change carries a unique identifier, and the terminal tracks which changesets it has already applied.

### 3.4 Branch Transfers

```mermaid
graph LR
    B1["Branch A<br/>(item leaving)"] -->|Transfer out| S["Sync Server"]
    B2["Branch B<br/>(item arriving)"] -->|Transfer in| S
    S -->|Broadcast transfer| B1
    S -->|Broadcast transfer| B2
```
![Rendered diagram](/agenda/diagrams/case-studies-pos-multi-terminal-sync-5.svg)

---

## 4. Results

### 4.1 What Works

| Outcome | Evidence |
|---------|----------|
| Real-time sync across terminals | WebSocket broadcast delivers changes in <100ms on LAN |
| Idempotent changesets | Re-applying same changeset is safe |
| Conflict detection | Multiple terminals editing same record triggers conflict UI |
| Offline resilience | Terminals queue changes when offline (see Offline Queue case study) |
| Branch transfers | Items transfer between branches with sync |

### 4.2 Performance

| Metric | Value |
|--------|-------|
| WebSocket broadcast latency (LAN) | <100ms |
| Changeset pull (polling fallback) | On-demand, ~100-500ms |
| Max changeset size | Configurable per branch |

---

## 5. Lessons Learned

### 5.1 WebSocket + polling hybrid is more robust than WebSocket alone

Pure WebSocket sync fails when terminals go offline or have flaky connections. The hybrid approach (WebSocket for push, polling `/sync/trigger` as fallback) means terminals always converge.

**Lesson:** Always have a pull fallback for real-time sync. Networks are unreliable.

### 5.2 Idempotency is non-negotiable

Without idempotent changesets, retrying a sync after a network error would duplicate sales, double-count inventory, etc. Every change must carry a unique ID and the terminal must track what it has applied.

**Lesson:** Design sync to be safe to retry. Idempotency keys on every change.

### 5.3 Conflict resolution needs UI, not just logic

When two terminals modify the same record, the system can detect the conflict but the resolution is a business decision. Showing the conflict to the user with both versions is more useful than silently picking a winner.

**Lesson:** Detect conflicts automatically, resolve them with user input.

---

## 6. Related Documentation

| Document | Path |
|----------|------|
| Feature tracking — Multi-branch Management | [`../feature-tracking/formint-pos.md`](../feature-tracking/formint-pos.md) § Multi-branch Management |
| Case study — Offline Queue | [./pos-offline-queue.md](./pos-offline-queue.md) |
| Case study — QR Menu | [./pos-qr-menu.md](./pos-qr-menu.md) |
| Case study — DataToken Sync Tagging | [./data-token-sync-tagging.md](./data-token-sync-tagging.md) |
| Feature roadmap | [`../../features/feature-roadmap.md`](../../features/feature-roadmap.md) |
| POS product docs | [`../../projects/formints/`](../../projects/formints/) |

---

## Remarks & Notes

- Multi-terminal sync is part of the Multi-branch Management feature (P0, Shipped)
- The sync protocol uses REST + WebSocket — no custom protocol
- Terminals are responsible for tracking their last ack timestamp
- Conflict UI is per-product — the sync layer detects, product layer resolves

<!-- AI-generated: review needed -->
