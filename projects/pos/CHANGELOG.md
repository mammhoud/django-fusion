# POS project changelog

The POS workspace changelog records cross-edition changes. Edition-specific
changes belong in the owning edition directory.

## 2026-08-11 - Active project closeout

### Changed

- Confirmed `projects/pos/forge-pos/` as the active POS desktop project under
  the canonical `projects/pos/` boundary.
- Kept edition-specific implementation and native/Tauri work in the edition
  directory rather than duplicating it at the workspace root.
- Documented that unfinished cloud, tenant, and plugin migration plans remain
  active plans and were not marked complete during this audit.

### Verification

- Run the Forge POS checks from `projects/pos/forge-pos/` using its local
  package and Rust tooling.
- Keep generated build output, native targets, and runtime databases out of
  source tracking according to the project ignore rules.

## 2026-08-03 - Formint/POS consolidation

- Cross-edition consolidation and backup work is tracked in
  `projects/formints/CHANGELOG.md` and the canonical POS plans.
