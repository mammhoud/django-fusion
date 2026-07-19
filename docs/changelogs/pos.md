# 🛒 POS Changelog

> All POS changes extracted from the real repo `CHANGELOG.md` at the repository root.

---

## 2026-07-19 — POS-KO Gaming Center + 3-Edition System

### feat: POS-KO Gaming Center

New gaming center module for the POS desktop app:

- **Token-based gaming sessions** with time tracking — start/stop/pause/resume
- **Game station management** — assign stations, track occupancy, manage queues
- **Session scheduling** — book future sessions, recurring time slots
- **Integrated billing** — charge by time (hourly/flat) with receipt generation
- **Receipt generation** — printable receipts with session details, time, cost

### feat: POS 3-Edition System

| Edition | Dir | Features |
|---------|-----|----------|
| **Minimal** | `pos-minimal/` | React + Tauri + Rust + SQLite — basic POS |
| **Solo** | `pos-solo/` | Minimal + Python/Sanic sidecar API + Cloud CRM sync |
| **Full** | `pos-full/` | Solo + Django ORM + WebSocket + Cloud CRM master |

### feat: Cloud CRM Architecture

- **Standalone Cloud CRM server** — `shared-portal/cloud/` on port 8766
- **Solo edition sync client** — pushes products, sales, customers to cloud
- **Sync proxy** — generic entity push endpoint on cloud server
- **Broadcast change signals** — Rust-based real-time update system via WebSocket

### feat: Django Portal

Shared Django portal with `django-fusion` viewsets across all editions:
- Portal admin interface for managing POS data via web
- Node API views for solo/minimal editions
- Cloud CRM master views for Full edition

### docs: POS CHANGELOG.md

Full version history created (see `projects/pos/CHANGELOG.md`).

---

## Previous Versions

For detailed per-version release notes, see:

- `projects/pos/CHANGELOG.md` — complete POS version history
- `projects/pos/pos-minimal/.github/workflows/release.yml` — release artifacts
- `projects/pos/pos-solo/.github/workflows/release.yml`
- `projects/pos/pos-full/.github/workflows/release.yml`

---

## Related

| Topic | Path |
|-------|------|
| POS editions | [`../projects/pos/editions.md`](../projects/pos/editions.md) |
| POS features | [`../projects/pos/features.md`](../projects/pos/features.md) |
| POS infrastructure | [`../projects/pos/infrastructure.md`](../projects/pos/infrastructure.md) |
| POS release pipeline | [`../publish/pos-release.md`](../publish/pos-release.md) |
