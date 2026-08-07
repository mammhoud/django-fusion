# POS Dev Scripts

Development scripts shared across all POS editions (mini, solo, full).

For complete documentation of **all** scripts (dev, publish, github), see:

➡️ [`../README.md`](../README.md)

---

## Quick usage

```bash
# From any edition directory (forge-pos, formint-pos, or pos-client)

# Free up port 1420 before starting dev server
node ../scripts/dev/kill-port.cjs

# Update copyright year in tauri.conf.json
PROJECT_ROOT=. node ../scripts/dev/update-year.cjs

# Auto-seed database if missing
PROJECT_ROOT=. node ../scripts/dev/ensure-db.cjs

# Check i18n translation gaps
PROJECT_ROOT=. node ../scripts/dev/check-i18n.cjs

# Capture 6 POS route screenshots
bash ../scripts/dev/capture-screenshots.sh
```

---

## Scripts in this directory

| Script | Purpose |
|--------|---------|
| `kill-port.cjs` | Free port(s) before starting dev server |
| `ensure-db.cjs` | Auto-seed database if missing |
| `update-year.cjs` | Update copyright year in `tauri.conf.json` |
| `check-i18n.cjs` | Audit i18n translation gaps (fr, ar) |
| `i18n-merge-ar.cjs` | Merge Arabic translations (idempotent) |
| `fill-fr-translations.cjs` | Fill French translation gaps |
| `capture-screenshots.sh` | Capture 6 POS routes via headless Chromium |

For full details (env vars, options, examples), see [`../README.md`](../README.md).
