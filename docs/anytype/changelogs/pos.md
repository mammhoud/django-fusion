# Changelog — POS Editions

**Type:** Changelog 📋
**Tags:** `#pos-mini` `#pos-solo` `#pos-full` `#pos-cloud`
**Status:** Published

---

## [2026-07-24] — Latest

### Added
- **Theme System** — 5 theme variants (Default, Corporate, Luxury, Pastel, Cyberpunk)
- **i18n** — 5 languages (EN, AR, FR, DE, ES) with RTL support
- **Role System** — Permission flags + 5 default roles (planning phase)
- **Sync Architecture** — 3-tier model (air-gapped, LAN, cloud)

### Fixed
- Settings.tsx: `setMode` ReferenceError — added to `useTheme()` destructuring
- Sale.tsx: Mobile sticky checkout bar for easier checkout on phones
- pos-full sidecar: conftest.py sys.path fix for test imports
- i18n: Added Appearance tab keys to all 15 locale files

### Changed
- Sidecar migrated to `uv` for Python dependency management
- Django fusion imports updated to canonical paths

---

## [2026-07] — Earlier

### Added
- All 4 POS editions (mini, solo, full, cloud)
- Tauri v2 desktop shell for mini/solo/full
- Django + Robyn sidecar for solo/full
- Full sales, inventory, analytics, employees, recipes, reports
- PDF receipt generation with jsPDF
- Keyboard shortcuts across all pages
- Responsive grid layouts for product display

### Fixed
- Sale.tsx mobile layout overflow → `max-w-full overflow-x-hidden`
- Fragment test imports → sys.path fix
- Payroll model missing fields → regular_hours, overtime_hours, total_pay

---

## Related Docs
- → `features/comparison-matrix.md` — Current feature state
- → `references/i18n-keys.md` — Translation key changes
