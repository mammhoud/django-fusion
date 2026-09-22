# Standard Edition — Local Completion Record

> Tags: `#formints` `#pos` `#standard` `#tauri` `#rust` `#diesel` `#sqlite` `#currency` `#tax` `#export` — status ✅ done (21 Aug 2026).

**Canonical source:** `projects/formints/formint-standard/`

**Status (21 Aug 2026): ✅ DONE.** Local implementation complete and verified
(multi-currency, tax profiles, role permissions, CSV/JSON export, offline sync
queue, contract/build fixes). An online server is optional and not required for
core operation. Only environment/operator-gated items remain.

## Verified features (code-backed, Rust/Diesel)

- **Currencies** — `list_currencies` / `create_currency` / `update_currency` /
  `delete_currency` (`src-tauri/src/lib.rs`, `operations/currency.rs`).
- **Tax profiles** — `list_tax_profiles` / `create_tax_profile` /
  `update_tax_profile` / `delete_tax_profile` + `compute_tax`
  (`operations/tax_profile.rs`, default-profile + validation tests).
- **Roles & permissions** — `operations/roles.rs` (`get_permission_catalog`,
  role CRUD, assign/remove, soft delete) + `Role` model.
- **CSV/JSON export** — `operations/exports.rs` (`export_resource` for
  products/sales/customers/inventory, CSV escaping, timestamped filenames,
  `ReportMetadata` recording) + `operations/reports.rs`.
- **Offline sync queue + reconnect** — `operations/server_reconnect.rs`
  (health check, pending-sync count, flush with backoff) + `operations/dump.rs`
  (dump/unuploaded/JSON) + `operations/server.rs` (embedded server lifecycle).
- **Community parity** — refunds, KDS tickets, hardware printer, invoices,
  loyalty transactions, payroll, scheduling, shifts, coupons, notes.

## Remaining work

- [ ] Full browser/E2E suite — requires a desktop/browser runtime (environment
  gate only; not a missing Standard product feature).

## Optional / external work intentionally left pending

- Django sidecar sync endpoints and large-dataset async exports are additive
  integrations, not required for Standard's local contract.
- Release packaging, signing, publishing, and remote commits remain operator
  actions and are prepared locally only.
