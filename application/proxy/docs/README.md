# `docs`

> Part of **Structa proxy** — Traefik edge and TLS termination for `*.structa.cloud`

Long-form documentation for the edge. Start at [`INDEX.md`](./INDEX.md) — it is
the documentation map, and every cross-reference elsewhere in this project uses
the stable `PX-NNN` IDs defined there.

These pages are **hand-written**. The per-directory `README.md` files are a
different layer: short, generated descriptions of what a directory contains.

## Contents

- `INDEX.md` - the documentation map (`PX-000`)
- `00-package-guide.md` - layout, ownership, where to change things (`PX-001`)
- `01-architecture.md` - Traefik/Caddy, static vs dynamic, networks (`PX-002`)
- `02-routing.md` - host table, priorities, adding a site (`PX-003`)
- `03-certificates.md` - ACME HTTP-01, dev cert SANs, backups (`PX-004`)
- `04-operations.md` - deploy, reload, rollback, failure interpretation (`PX-005`)
- `05-validation-and-health-checks.md` - the three gates (`PX-006`)

## Usage

```bash
# Read the map first
less docs/INDEX.md
```

## Related

- [`../README.md`](../README.md) — public route table and startup instructions
- [`../LETSENCRYPT.md`](../LETSENCRYPT.md) — certificate issuance runbook
