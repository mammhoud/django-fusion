# Forge POS changelog

All notable Forge POS desktop changes are recorded here.

## 2026-08-11 - Active project closeout

### Changed

- Confirmed Forge POS as the active edition at `projects/pos/forge-pos/`.
- Kept Rust/Tauri and frontend changes scoped to the edition instead of adding
  cross-edition compatibility files.
- Preserved the existing design-system and native integration boundaries while
  the POS plans continue through their remaining gates.

### Verification

- Run the frontend checks from the edition's package configuration.
- Run `cargo test` from `projects/pos/forge-pos/src-tauri/` for native behavior.
- Do not treat generated `target/`, build, or screenshot output as source.
