# Standard Edition — Local Completion Record

**Canonical source:** `projects/formints/formint-standard/`

**Status:** Local implementation complete. The Standard edition is a standalone
Tauri 2 + React/Astro + Rust/Diesel/SQLite desktop product. An online server is
optional and is not required for core operation.

## Completed local scope

### Rust/Diesel foundation

- [x] Multi-currency catalogue and default enforcement (`currency.rs`)
- [x] Tax profiles, default enforcement, and cent-rounded `compute_tax`
- [x] Product and sale tax-profile columns
- [x] Role permission resolution and permission-gated settings mutations
- [x] CSV/JSON exports for products, sales, customers, and inventory
- [x] Export metadata persisted in `report_metadata`
- [x] Offline `sync_queue`, batch/flush/failure/purge operations
- [x] Server reconnect and mutation dispatcher remain optional; local writes do
  not depend on a server
- [x] Rust modules are registered in `src-tauri/src/operations/mod.rs` and the
  Tauri command handler in `src-tauri/src/lib.rs`

Relevant migrations:

- `2026-12-01-000000_standard_currencies`
- `2026-12-03-000000_tax_profiles`
- `2026-08-10-000000_sync_queue`

### Frontend

- [x] Currency management page: `/currencies`
- [x] Tax profile management page: `/tax-profiles`
- [x] Local export page: `/export`
- [x] `usePermissions` and reusable `RoleGate`
- [x] Routes, lazy imports, preload registry, and navigation entries wired
- [x] Existing Standard settings, roles, reports, and offline UX retained

### Contract and build fixes closed during completion

- [x] Removed the mandatory nonexistent `binaries/pos-server` Tauri
  `externalBin`; server lifecycle code can remain optional in development
- [x] Fixed empty cash amounts being parsed as zero
- [x] Corrected the employee-schedule validation test query and removed its
  unused import
- [x] Removed an unused sidebar variable that failed Astro/TypeScript checking
- [x] Synchronized the Standard package lockfile with `@playwright/test`
  `1.49.1` locally

## Verification

- [x] `CARGO_BUILD_JOBS=1 cargo check --lib`
- [x] `./node_modules/.bin/astro check` — 0 errors; four existing deprecation
  hints remain in unrelated code
- [x] Targeted Vitest — 49 tests passed
- [x] Full Rust test suite — 81/81 passing (currency, tax-profile, permissions,
  exports, sync-queue filters all green)
- [ ] Full browser/E2E suite — requires a desktop/browser runtime (environment
  gate only; not a missing Standard product feature)

The unchecked item is an environment-dependent verification gate, not missing
Standard product features. No migrations, database resets, deployments, or
external publishing were performed.

## Optional / external work intentionally left pending

- Django sidecar sync endpoints and large-dataset async exports are additive
  integrations, not required for Standard's local contract.
- Release packaging, signing, publishing, and remote commits remain operator
  actions and are prepared locally only.
