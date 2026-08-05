# Formint POS Backup and Phase 1 Migration Record

> **Status:** Backup verified; Phase 1 foundation started
> **Date:** 2026-08-04
> **Scope:** `projects/pos/`

## Backup record

A non-destructive source archive was created before starting the Formint Phase 1 boundary.

| Field | Value |
|---|---|
| Backup root | `/home/structa.cloud-backups/pos-pre-formint-20260804T164308Z/` |
| Archive | `pos-workspace.tar` |
| Manifest | `backup-manifest.txt` |
| Archive size | 198,481,920 bytes |
| Archive members | 1,704 |
| SHA-256 | `46637b043d549886af45acdf7a732dbecf2f7a4cb5cb27a6bbc5c04341b49e48` |
| Integrity test | Passed with `tar --test` |
| Required sources | `pos-solo`, `pos-full`, `forge-pos`, `pos-cloud`, `pos-client`, `pos-e2e` present |

Generated directories were excluded because they are reproducible and contain dependencies/build output: `node_modules`, `dist`, Rust `target`, Python virtual environments/caches, `__pycache__`, pytest cache, Playwright reports, and test results. The exclusion list and repository status are recorded in the backup manifest.

The archive is outside the repository and must be retained until the Formint migration has a separate verified restore archive.

## Restore procedure

```bash
mkdir -p /tmp/pos-restore-check
 tar -xf /home/structa.cloud-backups/pos-pre-formint-20260804T164308Z/pos-workspace.tar \
   -C /tmp/pos-restore-check
find /tmp/pos-restore-check/projects/pos -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | sort
```

Never restore over an active checkout. Restore to a new directory, compare manifests, then move only approved files after stopping services and making a fresh snapshot.

## Phase 1 migration boundary

Created: `projects/pos/formint-pos/`

- `assets/` — shared asset contract
- `frontend/` — Astro + Alpine.js + HTMX shell
- `backend/` — minimal Django data/API boundary without Wagtail
- `migration/compatibility-manifest.json` — legacy identifiers, sources, and retirement gates
- `README.md` — setup, boundaries, and validation

The existing `projects/pos/pos-solo/` and `projects/pos/pos-full/` directories were not renamed, deleted, or modified by the Phase 1 foundation. This preserves rollback and allows compatibility testing.

## Naming policy

- New product-facing references use `formint-pos` and `Formint POS Professional`.
- Legacy `pos-solo`, `POS Solo`, `pos-full`, and `POS Full` remain accepted only as migration/source identifiers.
- Do not perform a filesystem rename until core parity, data migration, backup restore, two successful Formint release cycles, and retirement approval pass.

## Phase 1 gate

The foundation is started, not complete. Completion requires:

- core branch/order/KDS/sync/report vertical slice
- compatibility tests against preserved POS sources
- offline and reconnect tests
- backup restore drill
- Astro build/check and Django checks
- Formint asset manifest and dead-code baseline
- code review and migration approval
