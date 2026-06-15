# Alliance Docs Refactoring — Task List

> Generated from conversation: `7d30f510-588e-43f2-8111-d38b3fcda71e`
> Date: 2026-03-30

---

## Phase 1: Create `docs/` Skeleton + New Root Docs

- [x] Create `core/docs/README.md` (master index)
- [x] Create `core/docs/PRODUCT.md` (Alliance product overview)
- [x] Create `core/docs/INSTALL.md` (Docker-based install guide)
- [ ] Create `core/docs/config/settings.md` (expanded settings reference)

---

## Phase 2: Migrate Existing Docs → `docs/` (with Xellent → Alliance rename)

- [x] Migrate `apps/blog/PRODUCT.md` → `core/docs/apps/blog.md`
- [x] Migrate `apps/handlers/PRODUCT.md` → `core/docs/apps/handlers.md`
- [x] Migrate `apps/handlers/MCP.md` → `core/docs/integrations/mcp.md`
- [x] Migrate `apps/pages/models/contact_analysis.md` → `core/docs/apps/contact-model.md`
- [x] Migrate `components/profile/partials/BANNER_OPTIONS.md` → `core/docs/apps/profile-banner.md`
- [ ] Migrate `assets/static/js/ARCHITECTURE.md` → `core/docs/frontend/js-architecture.md`
- [ ] Migrate `assets/static/js/README.md` → `core/docs/frontend/js-codebase.md`
- [ ] Migrate `assets/static/js/pages/README.md` → `core/docs/frontend/pages-layout.md`
- [ ] Migrate `assets/static/js/modules/components/docs/preloader.md` → `core/docs/frontend/preloader.md`
- [ ] Migrate `assets/templates/allauth.md` → `core/docs/frontend/allauth-templates.md` (upgraded)
- [ ] Migrate `core/CI/README.md` → `core/docs/architecture/temporal-workflows.md`
- [ ] Migrate `webpack/readme.md` → `core/docs/frontend/webpack.md`

---

## Phase 3: Update `pyproject.toml` + Rename Sync Command

- [ ] Update `pyproject.toml` — `name = "xellent"` → `name = "alliancecore"`, update description
- [ ] Rename `apps/handlers/management/commands/sync_xellent.py` → `sync_alliancecore.py` and update internal references

---

## Phase 4: Delete Originals + Empty Files

- [ ] Delete `core/CI/models/.md` (empty file)
- [ ] Delete `configs/settings/readme.md` (empty file, replaced by `core/docs/config/settings.md`)
- [ ] Delete all 12 original `.md` files that were migrated (see Phase 2)

---

## Phase 5: Verify

- [ ] `find core/docs -name "*.md" | sort` — confirm all docs exist
- [ ] `grep -r "Xellent\|xellent\|Alliance\|/root/xellent" core/docs` — should return 0 results
- [ ] `grep -r "Xellent" pyproject.toml` — should return 0 results
- [ ] Confirm deleted originals no longer exist

---

## Status Legend

- `[ ]` — Pending
- `[/]` — In Progress
- `[x]` — Completed
