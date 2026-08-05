# POS — Backend Environment Setup

> **Edition:** Full | **Component:** Robyn Server (Django portal removed July 2026)

---

## ⚠️ DEPRECATED

This document described the **old Django portal** (`manage.py runserver`) which has
been removed. The POS Full edition now runs a single **Robyn + Django ORM** server
via `python3 server.py --port 8766` with no separate Django process.

See [`POS_ARCHITECTURE.md`](../../docs/POS_ARCHITECTURE.md) and
[`SIDECAR_V2.md`](../../docs/SIDECAR_V2.md) for the current architecture.

---

## Quick Start (Current)

```bash
cd sidecar
pip install -r requirements.txt
python3 server.py --port 8766
# Robyn server handles everything — no manage.py needed
```

## Related Docs

- [`ARCHITECTURE.md`](../../sidecar/ARCHITECTURE.md) — Sidecar architecture
- [`README.md`](../../sidecar/README.md) — Sidecar overview
