# 📊 Assets Usage Analysis

**Path:** `projects/assets/` (shared workspace assets)
**Last Updated:** 2026-07-26
**Total Files:** 1,270

---

## Overview

This directory is the **canonical shared asset source** for all Structa Cloud projects. It is configured via `projects/configs/base/assets.py` and `projects/configs/base/templates.py` and consumed by all Django sites.

---

## Directory Usage

| Directory | Used By | How |
|-----------|---------|-----|
| `static/` | **All projects** (lms, cms-fusion, lms-fusion, portfolio, cypercloud, fusion-cms) | Via `STATICFILES_DIRS` → `SHARED_STATIC_DIR` in `assets.py`. Served by Nginx `shared-media` at `/static/`. |
| `templates/` | **All projects** (lms, cms-fusion, lms-fusion, portfolio, cypercloud, fusion-cms) | Via `TEMPLATES_DIRS` → `BASE_DIR.parent / "assets" / "templates"` in `templates.py`. Served by Django template engine. |
| `locale/` | **All projects** | Via `LOCALE_PATHS` → `LOCALE_DIRS` in `assets.py`. Used for Django i18n translations. |
| `fixtures/` | **All projects** | Via `FIXTURE_DIRS` in `assets.py`. Used for database seeding (`loaddata`). |
| `scripts/` | **Build system** (asset CLI) | Referenced in `package.json` as `workspace.mjs`. Used by npm scripts for webpack builds, collectstatic, etc. |
| `Makefile` | **Build system** | Frontend build commands for all sites. |
| `package.json` | **Build system** | npm dependencies and scripts for asset building. |
| `package-lock.json` | **Build system** | Lock file for npm dependencies. |
| `ASSETS_GUIDE.md` | **Documentation** | Developer reference for asset build system. |

---

## Merge Sources

This directory was assembled by merging content from:

| Source | Files Merged | Notes |
|--------|-------------|-------|
| `projects/lms-fusion/assets copy/` | ~1,198 files | Core shared assets (static, templates, locale, fixtures, scripts) |
| `projects/cms-fusion/backend/assets/` | 71 unique files | Fixtures (auth, by-model, cleaned, production, test), static CSS/JS, template examples, email CSVs |
| `projects/lms-fusion/backend/assets/` | 71 unique files | Same content as cms-fusion (derived from same source) |
| `projects/cms-fusion/assets copy 2/` | 1 file | `package-lock.json` |

---

## Copy Locations

Copies of this merged asset set also exist at:

| Path | Purpose |
|------|---------|
| `projects/cms-fusion/assets/` | Isolated asset copy for Fusion CMS project |
| `projects/lms-fusion/assets/` | Isolated asset copy for Fusion LMS project |

---

## Notes

- **Media files** from `backend/assets/media/` are **NOT** merged here — they are user-uploaded Wagtail content and remain in each project's `backend/assets/media/`.
- **node_modules** from `assets copy 2` are **NOT** merged — they are build artifacts tracked separately.
- The shared `projects/assets/` is the **source of truth**; project-level copies are snapshots for isolation.
