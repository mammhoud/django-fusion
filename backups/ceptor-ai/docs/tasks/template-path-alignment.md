# Template path alignment tasks

Priority: 2 — after runtime boot/log errors are stable.

## Affected paths
- `applications/assets/templates/`
- `applications/ctc-research/templates/`
- `applications/ctc-research/assets/templates/`
- `applications/ctc-research/plugins/**/templates/`
- `applications/lms-demo/templates/`
- `applications/lms-demo/assets/templates/`
- `applications/lms-demo/plugins/**/templates/`
- `applications/VResume/**/templates/`

## Intended behavior
- CTC Research remains the reference for the current component tree, template organization, and include paths.
- LMS Demo and VResume use the same shared-template paths where the UI is cross-site, with site-specific overrides only where presentation differs.
- Duplicated templates are removed only after each include, extend, and Wagtail block template path resolves to the shared or site-specific replacement.
- Component categories avoid duplicated directory names such as `components/blocks/contact/contact/...`.
- Moved templates preserve Django/Wagtail context variables, tags, translations, forms, permissions, HTMX targets, and CMS-managed fields.

## Validation commands
- `rg -n "components/blocks/.*/.*/" applications/assets/templates applications/ctc-research applications/lms-demo applications/VResume`
- `rg -n "extends|include|template =|template'|template\"" applications/assets/templates applications/ctc-research applications/lms-demo applications/VResume`
- `make -C applications check WEBSITE=ctc`
- `make -C applications check WEBSITE=lms-demo`
- `make -C applications check WEBSITE=VResume`
- `make -C applications build-assets WEBSITE=ctc`
- `make -C applications build-assets WEBSITE=lms-demo`
