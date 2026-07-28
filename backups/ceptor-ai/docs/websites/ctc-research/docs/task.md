# Alliance Docs Refactoring — Task List

> Generated from conversation: `7d30f510-588e-43f2-8111-d38b3fcda71e`
> Date: 2026-03-30

---

## Phase 1: Create `docs/` Skeleton + New Root Docs

- [x] Create `projects/docs/README.md` (master index)
- [x] Create `projects/docs/PRODUCT.md` (Alliance product overview)
- [x] Create `projects/docs/INSTALL.md` (Docker-based install guide)
- [ ] Create `projects/docs/config/settings.md` (expanded settings reference)

---

## Phase 2: Migrate Existing Docs → `docs/` (with Xellent → Alliance rename)

- [x] Migrate `apps/blog/PRODUCT.md` → `projects/docs/apps/blog.md`
- [x] Migrate `apps/handlers/PRODUCT.md` → `projects/docs/apps/handlers.md`
- [x] Migrate `apps/handlers/MCP.md` → `projects/docs/integrations/mcp.md`
- [x] Migrate `apps/pages/models/contact_analysis.md` → `projects/docs/apps/contact-model.md`
- [x] Migrate `components/profile/partials/BANNER_OPTIONS.md` → `projects/docs/apps/profile-banner.md`
- [ ] Migrate `assets/static/js/ARCHITECTURE.md` → `projects/docs/frontend/js-architecture.md`
- [ ] Migrate `assets/static/js/README.md` → `projects/docs/frontend/js-codebase.md`
- [ ] Migrate `assets/static/js/pages/README.md` → `projects/docs/frontend/pages-layout.md`
- [ ] Migrate `assets/static/js/modules/components/docs/preloader.md` → `projects/docs/frontend/preloader.md`
- [ ] Migrate `assets/templates/allauth.md` → `projects/docs/frontend/allauth-templates.md` (upgraded)
- [ ] Migrate `projects/CI/README.md` → `projects/docs/architecture/temporal-workflows.md`
- [ ] Migrate `webpack/readme.md` → `projects/docs/frontend/webpack.md`

---

## Phase 3: Update `pyproject.toml` + Rename Sync Command

- [ ] Update `pyproject.toml` — `name = "xellent"` → `name = "alliancecore"`, update description
- [ ] Rename `apps/handlers/management/commands/sync_xellent.py` → `sync_alliancecore.py` and update internal references

---

## Phase 4: Delete Originals + Empty Files

- [ ] Delete `projects/CI/models/.md` (empty file)
- [ ] Delete `configs/settings/readme.md` (empty file, replaced by `projects/docs/config/settings.md`)
- [ ] Delete all 12 original `.md` files that were migrated (see Phase 2)

---

## Phase 5: Verify

- [ ] `find projects/docs -name "*.md" | sort` — confirm all docs exist
- [ ] `grep -r "Xellent\|xellent\|Alliance\|/root/xellent" projects/docs` — should return 0 results
- [ ] `grep -r "Xellent" pyproject.toml` — should return 0 results
- [ ] Confirm deleted originals no longer exist

---

## Status Legend

- `[ ]` — Pending
- `[/]` — In Progress
- `[x]` — Completed
