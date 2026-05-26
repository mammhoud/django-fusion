# Tasks: Package Reorganization v2

## Tasks

- [x] 1. Move libs/tests to django-grep
  - [x] 1.1 Copy test_craftsai.py → tests/test_nawaai/test_crafts_ai.py (update imports)
  - [x] 1.2 Copy test_osoul.py → tests/test_osoul/test_osoul_smoke.py
  - [x] 1.3 Copy test_rseal.py → tests/test_rseal/test_rseal_smoke.py
  - [x] 1.4 Copy test_deduplication_properties.py → tests/
  - [ ] 1.5 Delete libs/tests/ directory

- [x] 2. Create automation scripts
  - [x] 2.1 scripts/libs/run_tests.sh
  - [x] 2.2 scripts/libs/check_boundaries.sh
  - [x] 2.3 scripts/libs/scan_imports.py
  - [x] 2.4 scripts/libs/move_seeder.sh
  - [x] 2.5 scripts/libs/generate_namespace_docs.py

- [x] 3. Move seeder to django-grep
  - [x] 3.1 Run move_seeder.sh (copies seeder files, writes shim in rseal)
  - [x] 3.2 Verify django_grep.seeder exports same API

- [x] 4. Move routes to django-osoul
  - [x] 4.1 Copy rseal.pipelines.routes.base → django_osoul.routes.base
  - [x] 4.2 Write django_osoul.routes.__init__.py
  - [x] 4.3 Fix contrib imports in routes/base.py
  - [x] 4.4 Add DEFAULT, camel_case_to_underscore etc to django_osoul.contrib.__init__
  - [x] 4.5 Fix comp/templatetags imports to use django_osoul.routes

- [x] 5. Add TemplateRenderer to django-osoul
  - [x] 5.1 Create django_osoul.rendering.TemplateRenderer
  - [x] 5.2 Make django_rseal.renderer a shim

- [x] 6. Add BaseDashboardMixin / BaseCartMixin to django-osoul
  - [x] 6.1 Add to django_osoul.views.mixins

- [x] 7. Generate namespace README.md files
  - [x] 7.1 Run generate_namespace_docs.py for all 4 packages

- [x] 8. Verify package boundaries
  - [x] 8.1 Run check_boundaries.sh — all 15 checks pass

- [x] 9. Phase 1 remaining moves (foundation → osoul)
  - [x] 9.1 Move rseal.pipelines.middlewares → django_osoul.middlewares
  - [x] 9.2 Move rseal.pipelines.forms (base) → django_osoul.forms
  - [x] 9.3 Move rseal.pipelines.backends → django_osoul.backends
  - [x] 9.4 Move rseal.pipelines.filters → django_osoul.filters
  - [x] 9.5 Move rseal.pipelines.managers (generic) → django_osoul.managers
  - [x] 9.6 Move rseal.pipelines.mixins (generic) → django_osoul.mixins
  - [x] 9.7 Move rseal.contrib.debug_tools → django_osoul.contrib.debug_tools
  - [x] 9.8 Move rseal.contrib.{admin_site,cache,email_config,privacy} → django_osoul.contrib
  - [x] 9.9 Move rseal.handlers → django_osoul.handlers
  - [x] 9.10 Move rseal.scripts → django_osoul.scripts
  - [x] 9.11 Move rseal.logging_config → django_osoul.logging_config
  - [x] 9.12 Add deprecation shims in rseal for all moved items
  - [x] 9.13 Run check_boundaries.sh — verify still passing

- [x] 10. Phase 2 AI moves (rseal AI → crafts-ai)
  - [x] 10.1 Extract newsletter AI logic → crafts_ai.ai.newsletter
  - [x] 10.2 Update rseal.newsletter.enhancer to delegate to crafts_ai
  - [x] 10.3 Update rseal.ai.__init__ to be thin adapter
  - [x] 10.4 Verify crafts_ai has zero Django imports

- [x] 11. Delete libs/tests/
  - [x] 11.1 Confirm all tests moved to django-grep/tests/
  - [x] 11.2 Delete libs/tests/ directory

- [x] 12. Update all package READMEs
  - [x] 12.1 Re-run generate_namespace_docs.py after all moves
  - [x] 12.2 Update top-level README.md for each package

- [ ] 13. Commit and push all repos
  - [ ] 13.1 Commit django-osoul
  - [ ] 13.2 Commit django-rseal
  - [ ] 13.3 Commit django-grep
  - [ ] 13.4 Commit nawaai (crafts-ai)
  - [ ] 13.5 Push all to remote

- [x] 14. Final verification
  - [x] 14.1 Run check_boundaries.sh — all pass
  - [x] 14.2 Run scan_imports.py — zero violations
  - [x] 14.3 Run run_tests.sh — all tests pass
  - [x] 14.4 Verify libs/tests/ does not exist
  - [x] 14.5 Verify every package dir has README.md
