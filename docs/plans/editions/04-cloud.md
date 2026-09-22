# Cloud Edition — Design, Architecture & Implementation Plan

> Tags: `#formints` `#pos` `#cloud` `#django` `#channels` `#unfold` `#saas` `#backups` `#monitoring` — status 🟡 staging (21 Aug 2026).

> **Status (21 Aug 2026): 🟡 STAGING.** Backup/monitoring + Cloud Dashboard
> implementation is complete and verified locally —
> `BackupRun` model + migration, `backup_db` management command, `/monitor/status`
> endpoint, docs/changelog sync, django-fusion monitor tile + `BackupRun` admin,
> SDK monitor wiring in the telemetry page, and Playwright e2e + inheritance
> parity sweep. **Staging** means the code is implemented and locally verified
> but has not yet been deployed/promoted to a running staging environment;
> the remaining items below are the promotion path.

## Verified features (code-backed)

- **Automatic backups** — `BackupRun` model
  (`backend/apps/core/models.py`), `backup_db` management command
  (`backend/apps/core/management/commands/backup_db.py`), nightly scheduled
  task (`backend/plugins/workers/backup_tasks.py`), Unfold admin
  (`backend/apps/core/admin.py`). Tests: `apps/test_backup.py`.
- **Monitoring** — `GET /monitor/status` (`apps/handlers/surface.py`),
  monitor fragment (`apps/handlers/fragments/monitor.py`). Tests:
  `apps/test_monitor.py`.
- **Cloud dashboard** — `/api/dashboard/*` contract (branch health, queue
  summary/by-branch/list/retry/cancel, conflict list/resolve/dismiss/stats,
  activity) + frontend `/cloud-dashboard` page. Tests:
  `apps/test_dashboard_contract.py`.
- **Tenant identity layer** — `Tenant`/`Domain` registry, `BranchSettings`,
  `TenantAwareAccountAdapter`, context processor, branch DB aliases —
  SQLite-safe and tenant-inert (`08-tenant-schemas.md`). Tests:
  `apps/test_tenancy.py`.
- **Sync pipeline + WebSockets** — sync receivers/broker/conflict resolver,
  `/ws/sync-events/` Channels consumer with parity-contract tests
  (`apps/test_ws_sync_events.py`, `apps/test_ws_parity_contract.py`).

## Remaining work — staging promotion (repository-owner actions)

All code items are implemented and verified in the working tree; each is held
back only because the promotion is an explicit owner action.

- [ ] Commit `BackupRun` model + migration (Task C1).
- [ ] Commit `backup_db` management command (Task C2).
- [ ] Commit `/monitor/status` endpoint (Task C3).
- [ ] Commit Cloud docs & changelog sync (Task C4).
- [ ] Commit django-fusion monitor tile + `BackupRun` admin (Task C5).
- [ ] Commit SDK monitor module wiring in the telemetry page (Task C6).
- [ ] Commit Playwright e2e + inheritance parity sweep (Task C7).
- [ ] **Deploy a staging master** — boot the Django backend (daphne + runserver),
  run `make verify-stack` live parity check, confirm `/monitor/status` and the
  dashboard against a running instance.
- [ ] **Postgres flip-on (schema-per-tenant)** — set `DB_ENGINE`,
  `migrate_schemas --shared` + `--tenant`, seed `public` Tenant + `localhost`
  Domain ([08-tenant-schemas.md](08-tenant-schemas.md) Tenant 6–7).

Per-task `git add`/`git commit` messages are recorded in the original task
steps; nothing else is outstanding.
