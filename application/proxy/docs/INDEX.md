# Structa Proxy Documentation Index (PX-000)

> **Source of truth.** This index never marks a doc "✅ Exists" until its file is
> actually present in `docs/`. Cross-references in other docs use the `PX-0NN`
> IDs in this table, following the convention established by `django-fusion`
> (`DF-NNN`).

## Documentation Map

| ID | File | Topic | Status |
|----|------|-------|--------|
| PX-000 | [`docs/INDEX.md`](./INDEX.md) | This index | ✅ Exists |
| PX-001 | [`docs/00-package-guide.md`](./00-package-guide.md) | Layout, what owns what, where to change things | ✅ Exists |
| PX-002 | [`docs/01-architecture.md`](./01-architecture.md) | Traefik vs Caddy, static vs dynamic, networks, Mermaid diagram | ✅ Exists |
| PX-003 | [`docs/02-routing.md`](./02-routing.md) | Host table, priorities, naming, how to add a site | ✅ Exists |
| PX-004 | [`docs/03-certificates.md`](./03-certificates.md) | ACME HTTP-01, dev certificate SANs, backups | ✅ Exists |
| PX-005 | [`docs/04-operations.md`](./04-operations.md) | Deploy, reload, rollback, routine checks | ✅ Exists |
| PX-006 | [`docs/05-validation-and-health-checks.md`](./05-validation-and-health-checks.md) | The three gates and what each catches | ✅ Exists |

Auxiliary files kept as long-form references:

| File | Topic | Status |
|------|-------|--------|
| [`LETSENCRYPT.md`](../LETSENCRYPT.md) | Let's Encrypt issuance runbook | ✅ Exists |
| [`README.md`](../README.md) | Public route table and startup instructions | ✅ Exists |

## Per-directory documentation

Every directory here carries a `README.md` describing its role, contents and
public API, following the `django-fusion` per-directory convention:

- [`configs/README.md`](../configs/README.md)
- [`configs/traefik/README.md`](../configs/traefik/README.md)
- [`configs/traefik/dynamic/README.md`](../configs/traefik/dynamic/README.md) — the live router table
- [`configs/caddy/README.md`](../configs/caddy/README.md)
- [`scripts/README.md`](../scripts/README.md)
- [`scripts/dev/README.md`](../scripts/dev/README.md)
- [`scripts/production/README.md`](../scripts/production/README.md)

## Conventions

- **Doc IDs:** `PX-NNN`. IDs are stable across filename changes; if a doc is
  renamed, edit its row here rather than the ID.
- **Cross-link discipline:** reference another doc by its `PX-NNN` ID and a
  markdown link. Plain filename references drift.
- **Status update rule:** switch a row to ✅ Exists **only after** the file is on
  disk with real, non-stub content.
- **Source mapping:** code blocks should be traceable to a real path under this
  directory.
