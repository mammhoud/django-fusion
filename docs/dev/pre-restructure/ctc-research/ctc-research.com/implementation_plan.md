# Alliance Documentation Refactoring — Implementation Plan

> Generated from conversation: `7d30f510-588e-43f2-8111-d38b3fcda71e`
> Date: 2026-03-30

---

## Background

The goal of this refactoring is to:

1. Centralize all scattered `.md` specification files into a structured `core/docs/` directory.
2. Rename **"Xellent"** → **"Alliance"** across the entire repository (docs, config, management commands).
3. Create essential root-level documentation: `PRODUCT.md`, `INSTALL.md`, `README.md`.
4. Clean up redundant or empty files to establish a professional, maintainable project foundation.

---

## User Review Required

> [!IMPORTANT]
> The `pyproject.toml` currently has `name = "xellent"` and `description = "Xellent Learning Management System"`. Renaming this to `alliancecore` is a **breaking change** if any packages import from it by name. Confirm rename is safe before proceeding.

> [!WARNING]
> Some docs contain hardcoded file links to `/root/xellent/...` paths (e.g., `pages/README.md`, `BANNER_OPTIONS.md`). These will be updated to relative paths during migration.

> [!IMPORTANT]
> Renaming `sync_xellent.py` → `sync_alliancecore.py` changes the CLI management command name. Confirm this is acceptable.

---

## Proposed Changes

### 1. Target `docs/` Directory Structure

```
core/docs/
├── README.md                        # Index/overview of all docs
├── PRODUCT.md                       # Root product overview (Alliance)
├── INSTALL.md                       # Docker-based installation guide
├── implementation_plan.md           # This file
├── task.md                          # Task checklist
│
├── architecture/
│   ├── overview.md                  # Migrated from: core/CI/README.md
│   └── js-architecture.md          # Migrated from: assets/static/js/ARCHITECTURE.md
│
├── frontend/
│   ├── js-codebase.md               # Migrated from: assets/static/js/README.md
│   ├── pages-layout.md              # Migrated from: assets/static/js/pages/README.md
│   ├── preloader.md                 # Migrated from: assets/static/js/modules/components/docs/preloader.md
│   ├── webpack.md                   # Migrated from: webpack/readme.md
│   └── allauth-templates.md         # Upgraded from: assets/templates/allauth.md
│
├── apps/
│   ├── blog.md                      # Migrated from: apps/blog/PRODUCT.md
│   ├── handlers.md                  # Migrated from: apps/handlers/PRODUCT.md
│   ├── contact-model.md             # Migrated from: apps/pages/models/contact_analysis.md
│   └── profile-banner.md            # Migrated from: components/profile/partials/BANNER_OPTIONS.md
│
├── integrations/
│   └── mcp.md                       # Migrated from: apps/handlers/MCP.md
│
└── config/
    └── settings.md                  # Expanded from: configs/settings/readme.md (was empty)
```

---

### 2. Files to Create (New)

#### [NEW] `core/docs/README.md`
Master index linking to all documentation sections.

#### [NEW] `core/docs/PRODUCT.md`
Root-level product overview for **Alliance** — project purpose, modules, tech stack.

#### [NEW] `core/docs/INSTALL.md`
Full Docker-based installation guide including:
- Prerequisites
- `.env` setup
- `docker compose` commands
- First-run steps
- `django-fusion` source-clone configuration

#### [NEW] `core/docs/config/settings.md`
Expand the previously empty `configs/settings/readme.md` into a proper settings documentation with environment variable reference.

#### [NEW] `core/docs/frontend/allauth-templates.md`
Expand the raw template list in `assets/templates/allauth.md` into a proper reference document.

---

### 3. Files to Migrate

Content is copied to the new `docs/` location, all `Xellent`/`xellent` references replaced with `Alliance`, then originals deleted.

| Original Path | New Path |
|---|---|
| `apps/blog/PRODUCT.md` | `core/docs/apps/blog.md` |
| `apps/handlers/MCP.md` | `core/docs/integrations/mcp.md` |
| `apps/handlers/PRODUCT.md` | `core/docs/apps/handlers.md` |
| `apps/pages/models/contact_analysis.md` | `core/docs/apps/contact-model.md` |
| `assets/static/js/ARCHITECTURE.md` | `core/docs/frontend/js-architecture.md` |
| `assets/static/js/README.md` | `core/docs/frontend/js-codebase.md` |
| `assets/static/js/pages/README.md` | `core/docs/frontend/pages-layout.md` |
| `assets/static/js/modules/components/docs/preloader.md` | `core/docs/frontend/preloader.md` |
| `assets/templates/allauth.md` | `core/docs/frontend/allauth-templates.md` (upgraded) |
| `components/profile/partials/BANNER_OPTIONS.md` | `core/docs/apps/profile-banner.md` |
| `core/CI/README.md` | `core/docs/architecture/temporal-workflows.md` |
| `webpack/readme.md` | `core/docs/frontend/webpack.md` |

**Stubs to update in-place (keep existing location, improve content):**
- `apps/readme.md` — already fine, leave as-is
- `assets/readme.md` — update to a proper i18n commands reference
- `configs/readme.md` — already fine, leave as-is

**Delete entirely:**
- `core/CI/models/.md` — empty file (0 bytes)
- `configs/settings/readme.md` — empty, replaced by `core/docs/config/settings.md`

---

### 4. "Xellent" → "Alliance" Renames

#### [MODIFY] `pyproject.toml`
```diff
-name = "xellent"
-description = "Xellent Learning Management System"
+name = "alliancecore"
+description = "Alliance Platform"
```

#### [MODIFY] `apps/handlers/management/commands/sync_xellent.py`
- Rename file to `sync_alliancecore.py`
- Update all internal references from `xellent` → `alliancecore`

#### [MODIFY] All migrated docs
- Replace all occurrences of `Xellent`, `xellent`, `Alliance`, `CTC Blog`, `CTC Handlers` with `Alliance`
- Fix all `/root/xellent/` file paths to use relative paths (e.g., `../assets/static/js/pages/`)

---

## Open Questions

> [!IMPORTANT]
> **Q1:** Should the original scattered `.md` files be **deleted** after migration, or kept as stubs pointing to `docs/`? The previous session agreed to delete — please reconfirm.

> [!IMPORTANT]
> **Q2:** Should `sync_xellent.py` be renamed to `sync_alliancecore.py`? This changes the CLI invocation from `manage.py sync_xellent` → `manage.py sync_alliancecore`.

> [!NOTE]
> **Q3:** Should `CHANGELOG.md` or `CONTRIBUTING.md` be created in `core/docs/` as well?

---

## Verification Plan

### Automated Checks
```bash
# Confirm all docs migrated
find core/docs -name "*.md" | sort

# Confirm zero Xellent references remain in docs
grep -r "Xellent\|xellent\|Alliance\|/root/xellent" core/docs

# Confirm pyproject.toml updated
grep -r "Xellent" pyproject.toml

# Confirm deleted files are gone
ls apps/blog/PRODUCT.md 2>&1 || echo "Deleted OK"
```

### Manual Review
- Review `core/docs/README.md` index links for correctness
- Review `core/docs/INSTALL.md` for accuracy against actual project setup
- Confirm all cross-references within docs point to valid paths
