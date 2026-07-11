# Theme and BEM conversion tasks

Priority: 4 — large UI migration after runtime, auth, and shared template paths are stable.

## Affected paths
- `theme/`
- `.kilo/mcp_server.py`
- `.kilo/skills/`
- `core/lms-demo/assets/static/styles/`
- `core/lms-demo/templates/`
- `core/lms-demo/plugins/**/templates/`
- `core/assets/templates/`

## Intended behavior
- Theme analysis tools map theme components to current Django template/component paths.
- Copied theme components keep live Django data bindings, template tags, URLs, forms, translations, and Wagtail fields.
- LMS Demo styles are converted to reusable BEM-style classes without styling IDs.
- Shared components are promoted to `core/assets/templates`; LMS-specific presentation remains in `core/lms-demo`.

## Validation commands
- `rg -n "id=|class=|include|extends" core/lms-demo/templates core/lms-demo/plugins core/assets/templates`
- `make -C applications build-assets WEBSITE=lms-demo`
- `make -C applications check WEBSITE=lms-demo`
