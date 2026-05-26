# Tasks: Finalize Refactor

**Legend**: `[ ]` not started · `[-]` in progress · `[x]` complete · `[~]` queued

## Package Architecture (venv/libs)

```
django-osoul   — Foundation layer: models, mixins, utils, comp (UI components),
                 CI models, contrib (enums, choices, context, schemas, responses)
                 Boundary: NO wagtail, celery, django_rseal imports

django-rseal   — Automation layer: pipelines (models, views, forms, services,
                 signals, snippets, routes), email, email_tools, mcp_designer,
                 workflows/orchestrator, management commands, contrib (debug_tools,
                 admin_site, cache, email_config, privacy)
                 Depends on: django-osoul, wagtail, celery

django-grep    — Testing framework: seeder, tests (base, assertions, factories,
                 fixtures, mixins, selenium_base, pytest_plugin)
                 Depends on: django-osoul, django-rseal

nawaai         — AI/MCP toolkit: crafts_ai (ai, chat, mcp, orchestrator, seeder)
                 Boundary: NO Django imports (pure Python)
```

## What Changed (not just renames)

The refactor reorganised responsibilities across packages:
- `django_grep.pipelines.*` → `django_rseal.pipelines.*` (all pipeline logic moved to rseal)
- `django_grep.comp.*` → `django_osoul.comp.*` (UI components moved to osoul)
- `django_grep.CI.*` → `django_osoul.CI.*` (CI models moved to osoul)
- `django_grep.contrib.*` → split: debug_tools/admin/cache/email/privacy → `django_rseal.contrib.*`; enums/choices/context/schemas → `django_osoul.contrib.*`
- `django_grep.handlers.*` → `django_rseal.handlers.*`
- `django_grep.scripts.*` → `django_rseal.scripts.*`
- `django_seed` → `django_rseal` (seeder/email/models all in rseal)
- `django_rseal.seeder` → shim pointing to `django_grep.seeder` (seeder lives in grep)
- `crafts_ai.orchestrator` → same path in nawaai (no change)
- `django_rseal.workflows.orchestrator` → new home for orchestrator CLI

---

## Priority 1 — Missing Modules in venv/libs (Import Errors)

These paths are imported by both sites but don't exist yet in venv/libs.

- [x] 1. Create missing `django_osoul.comp.blocks` sub-modules
  - [x] 1.1 Create `venv/libs/django-osoul/src/django_osoul/comp/blocks/media/__init__.py`
  - [x] 1.2 Create `venv/libs/django-osoul/src/django_osoul/comp/blocks/media/image.py`
    - Must export `SimpleImageBlock` (Wagtail StructBlock subclass)
    - Used by: ctc-research migrations, LMS migrations
  - [x] 1.3 Create `venv/libs/django-osoul/src/django_osoul/comp/blocks/media/gallery.py`
    - Must export `MediaGalleryBlock`
    - Used by: `ctc-research.com/apps/pages/models/pages/about.py`
  - [x] 1.4 Create `venv/libs/django-osoul/src/django_osoul/comp/blocks/partials/__init__.py`
  - [x] 1.5 Create `venv/libs/django-osoul/src/django_osoul/comp/blocks/partials/faq.py`
    - Must export `FAQSectionBlock`
    - Used by: `ctc-research.com/apps/pages/models/pages/contact.py`, `base.py`

- [x] 2. Create missing `django_osoul.comp.payloads` module
  - [x] 2.1 Create `venv/libs/django-osoul/src/django_osoul/comp/payloads/__init__.py`
  - [x] 2.2 Create `venv/libs/django-osoul/src/django_osoul/comp/payloads/services.py`
    - Must export `BaseService`, `TokenService`
    - Used by: `ctc-research.com/apps/LMS/services_legacy.py`

- [x] 3. Fix `django_rseal.contrib.enums` — redirect to `django_osoul.contrib.enums`
  - [x] 3.1 Create `venv/libs/django-rseal/src/django_rseal/contrib/enums.py` shim
    - Re-export `Environment`, `Runtime`, `Module`, `Direction`, `Workflow`, `LogLevel` from `django_osoul.contrib.enums`
    - Re-export `FileUploadStorage`, `FileUploadStrategy` from `django_osoul.contrib.enums.upload`
    - Used by: `ctc-research.com/configs/settings/conf.py`, `ctc-research.com/core/CI/models/media/file.py`, `structa.cloud/configs/settings/conf.py`

- [x] 4. Create missing `django_rseal.contrib.models` module
  - [x] 4.1 Identify what `Contact`, `ContactEmail`, `ContactPhone`, `Corporate` are
    - Check `venv/libs/django-rseal/src/django_rseal/pipelines/models/contacts/`
  - [x] 4.2 Create `venv/libs/django-rseal/src/django_rseal/contrib/models.py` shim
    - Re-export `Contact`, `ContactEmail`, `ContactPhone` from `django_rseal.pipelines.models.contacts`
    - Re-export `Corporate` (or alias) from correct location
    - Used by: `ctc-research.com/apps/handlers/processors/company.py`

---

## Priority 2 — Structural Cleanup (Blockers)

- [x] 5. Fix structa.cloud apps duplication (`apps/apps/` → `apps/`)
  - [x] 5.1 Move `structa.cloud/apps/apps/LMS/` → `structa.cloud/apps/LMS/`
  - [x] 5.2 Move `structa.cloud/apps/apps/blog/` → `structa.cloud/apps/blog/` (merge, skip existing)
  - [x] 5.3 Move `structa.cloud/apps/apps/handlers/` → `structa.cloud/apps/handlers/` (merge, skip existing)
  - [x] 5.4 Move `structa.cloud/apps/apps/pages/` → `structa.cloud/apps/pages/` (merge, skip existing)
  - [x] 5.5 Move `structa.cloud/apps/apps/templates/` → `structa.cloud/apps/templates/` (merge)
  - [x] 5.6 Scan `structa.cloud/configs/` for `apps.apps.*` in `INSTALLED_APPS` → fix to `apps.*`
  - [x] 5.7 Remove `structa.cloud/apps/apps/` directory (verify zero `apps.apps.*` imports first)

- [x] 6. Delete old `libs/tests/` directory
  - [x] 6.1 Confirm all tests present in `venv/libs/django-grep/tests/`
  - [x] 6.2 Delete `libs/tests/` if it still exists

- [x] 7. Verify `ctc-research.com/core/urls.py` resolves correctly
  - [x] 7.1 Confirm `django_rseal.pipelines.urls` include works
  - [x] 7.2 Confirm `django_rseal.contrib.debug_tools.*` imports resolve
  - [x] 7.3 Confirm `django_osoul.CI.*` imports resolve

---

## Priority 3 — Package Enhancements (venv/libs)

- [x] 8. Add backup management commands to `venv/libs/django-grep`
  - [x] 8.1 Create `venv/libs/django-grep/src/django_grep/management/__init__.py`
  - [x] 8.2 Create `venv/libs/django-grep/src/django_grep/management/commands/__init__.py`
  - [x] 8.3 Create `backup_db` command → `BACKUP_DIR/db_YYYYMMDD_HHMMSS.json` via `dumpdata`
  - [x] 8.4 Create `backup_media` command → `BACKUP_DIR/media_YYYYMMDD_HHMMSS.tar.gz`
  - [x] 8.5 Create `load_fixtures` command → idempotent `loaddata` for each fixture arg

- [x] 9. Enhance `venv/libs/django-grep` Selenium test infrastructure
  - [x] 9.1 Add `selenium_driver` + `base_url` fixtures to `pytest_plugin.py`
  - [x] 9.2 Create `venv/libs/django-grep/tests/selenium/__init__.py`
  - [x] 9.3 Create `venv/libs/django-grep/tests/selenium/conftest.py`
  - [x] 9.4 Create `venv/libs/django-grep/tests/selenium/test_site_health.py`
    - `test_homepage_loads`, `test_health_endpoint`, `test_admin_accessible` via `requests`

- [x] 10. Phase 1 remaining moves in venv/libs: rseal → osoul (with shims)
  - [x] 10.1 Move `rseal.pipelines.middlewares` → `django_osoul.middlewares` + shim
  - [x] 10.2 Move `rseal.pipelines.forms` (base) → `django_osoul.forms` + shim
  - [x] 10.3 Move `rseal.pipelines.backends` → `django_osoul.backends` + shim
  - [x] 10.4 Move `rseal.pipelines.filters` → `django_osoul.filters` + shim
  - [x] 10.5 Move `rseal.pipelines.managers` (generic) → `django_osoul.managers` + shim
  - [x] 10.6 Move `rseal.pipelines.mixins` (generic) → `django_osoul.mixins` + shim
  - [x] 10.7 Move `rseal.logging_config` → `django_osoul.logging_config` + shim
  - [x] 10.8 Run `venv/libs/scripts/check_boundaries.sh` — all checks pass

- [x] 11. Phase 2 AI moves: rseal.ai → nawaai/crafts_ai
  - [x] 11.1 Extract newsletter AI logic → `crafts_ai.ai.newsletter`
  - [x] 11.2 Update `rseal.newsletter.enhancer` to delegate to `crafts_ai`
  - [x] 11.3 Update `rseal.ai.__init__` to thin adapter
  - [x] 11.4 Verify `crafts_ai` has zero Django imports

---

## Priority 4 — ctc-research Selenium Tests

- [x] 12. Create ctc-research Selenium test suite
  - [x] 12.1 Create `ctc-research.com/tests/selenium/__init__.py`
  - [x] 12.2 Create `ctc-research.com/tests/selenium/conftest.py`
    - `base_url = os.getenv("SELENIUM_BASE_URL", "http://localhost:8270")`
  - [x] 12.3 Create `ctc-research.com/tests/selenium/test_homepage.py`
  - [x] 12.4 Create `ctc-research.com/tests/selenium/test_auth.py`
  - [x] 12.5 Create `ctc-research.com/tests/selenium/test_admin.py`

---

## Priority 5 — Docker Build & Run

- [x] 13. Build and start ctc-research containers
  - [x] 13.1 Start infra: `docker compose up -d postgres redis`
  - [x] 13.2 Build: `docker compose -f ctc-research.com/docker-compose.yml build website`
  - [x] 13.3 Build: `docker compose -f ctc-research.com/docker-compose.yml build website-media`
  - [x] 13.4 Start: `docker compose -f ctc-research.com/docker-compose.yml up -d`
  - [x] 13.5 Check logs for Python errors/tracebacks

- [x] 14. Load fresh data and verify
  - [x] 14.1 `docker exec website uv run python com migrate --noinput`
  - [x] 14.2 `docker exec website uv run python com loaddata wagtail_pages_dump.json`
  - [x] 14.3 `docker exec website uv run python com loaddata ctc-research-data.json`
  - [x] 14.4 `curl -sf http://localhost:8270/health/` → HTTP 200
  - [x] 14.5 `docker exec website uv run python com check` → exit 0

---

## Priority 6 — Final Verification & Cleanup

- [x] 15. Run full test suites
  - [x] 15.1 `cd venv/libs && uv run pytest django-grep/tests/ -v`
  - [x] 15.2 `cd ctc-research.com && uv run pytest tests/ -v --ignore=tests/selenium`
  - [x] 15.3 `cd ctc-research.com && uv run pytest tests/selenium/ -v`

- [x] 16. Update all package READMEs and commit
  - [x] 16.1 Re-run `venv/libs/scripts/generate_namespace_docs.py` for all 4 packages
  - [x] 16.2 Commit `venv/libs/django-osoul`, `django-rseal`, `django-grep`, `nawaai`
  - [x] 16.3 Push all to remote

- [x] 17. Final boundary verification
  - [x] 17.1 `venv/libs/scripts/check_boundaries.sh` — all pass
  - [x] 17.2 `venv/libs/scripts/scan_imports.py` — zero violations
  - [x] 17.3 `venv/libs/scripts/run_tests.sh` — all pass
  - [x] 17.4 Verify `libs/tests/` does not exist
  - [x] 17.5 Verify every package in `venv/libs/` has `README.md`

---

## Cross-References

- **django-refactoring spec** (`.kiro/specs/django-refactoring/`): Package boundary rules implemented by tasks 1–4 and 10–11.
- **ecosystem-architectural-refactoring spec** (`.kiro/specs/ecosystem-architectural-refactoring/`): High-level architecture that the package moves in tasks 10–11 realise.
- **ctc-research-deployment-verification spec** (`.kiro/specs/ctc-research-deployment-verification/`): Post-deployment verification that depends on the Docker build work in tasks 13–14.
- **phase-3-production-deployment spec** (`.kiro/specs/phase-3-production-deployment/`): Production deployment steps that build on the container work completed in tasks 13–17.

---

## Status Summary

| Item | Status |
|------|--------|
| `django_grep.*` → `django_rseal/osoul.*` imports in sites | ✅ Done |
| Root `pyproject.toml` → `venv/libs` workspace members | ✅ Done |
| Dockerfiles → `COPY venv/libs` | ✅ Done |
| docker-compose volumes → `venv/libs` | ✅ Done |
| Postgres data path unified | ✅ Done |
| entrypoint: `uv run` + fixture loading | ✅ Done |
| start script: `uv run uvicorn` | ✅ Done |
| `django_rseal.scripts.superuser` | ✅ Exists in venv/libs |
| `django_rseal.pipelines.urls` | ✅ Exists in venv/libs |
| `django_osoul.comp.blocks.media.*` | ✅ Done (from backup) |
| `django_osoul.comp.blocks.partials.*` | ✅ Done (from backup) |
| `django_osoul.comp.payloads.services` | ✅ Done |
| `django_rseal.contrib.enums` shim | ✅ Done |
| `django_rseal.contrib.models` shim | ✅ Done |
| `structa.cloud/apps/apps/` duplication | ✅ Merged & removed |
| `libs/tests/` deleted | ✅ Already gone |
| Backup commands in django-grep | ✅ Done |
| Selenium test infrastructure (grep) | ✅ Done |
| ctc-research Selenium tests | ✅ Done |
| `.dockerignore` root (exclude node_modules) | ✅ Done |
| Dockerfile rewritten (all deps explicit) | ✅ Done |
| Docker build & run | ✅ Done |
| Final boundary verification | ✅ Done |
| `django-osoul` wagtail optional dep | ✅ Done |
| `django-rseal.chat` bubble widget + nawaai backends | ✅ Done |
| `rseal_chat` templatetag | ✅ Done |
| Chat DB models (ChatSession, ChatMessage) | ✅ Done |
| Chat migration 0001_initial | ✅ Done |
