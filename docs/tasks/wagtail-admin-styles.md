# Wagtail admin style consolidation tasks

Priority: 3 — after runtime and auth/template path stability.

## Affected paths
- `applications/assets/templates/`
- `applications/assets/static/styles/`
- `applications/ctc-research/**/wagtail_hooks.py`
- `applications/lms-demo/**/wagtail_hooks.py`
- `applications/VResume/**/wagtail_hooks.py`

## Intended behavior
- Wagtail admin customizations use shared static colors and style tokens from `applications/assets/static/styles`.
- Copied admin templates are deduplicated into shared templates unless a site-specific override is required.
- Overrides preserve Wagtail block/panel behavior and do not remove admin context variables or permissions.

## Validation commands
- `rg -n "wagtail|admin" applications/assets/templates applications/assets/static applications/ctc-research applications/lms-demo applications/VResume`
- `make -C applications check WEBSITE=ctc`
- `make -C applications check WEBSITE=lms-demo`
- `make -C applications check WEBSITE=VResume`
- `make -C applications build-assets-all`
