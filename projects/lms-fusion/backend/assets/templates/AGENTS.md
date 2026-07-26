# Site Template Overrides

Scope: this site template tree.

## Lookup Strategy

Site templates here are resolved before the shared `projects/assets/templates/` layer. Keep files in this tree only when they are intentional site-specific overrides, branded shells, or templates that must shadow shared behavior.

## Override Rules

- Prefer deleting exact duplicates and allowing Django to load `projects/assets/templates/<relative-path>`.
- Keep thin overrides for branded variations; move reusable repeated markup into shared includes under `projects/assets/templates/components/`.
- Preserve existing template names, include names, block names, and context variables to avoid breaking Wagtail/Django rendering.
- Use `fragment_name` for fragment identifiers and context keys; do not introduce alternate fragment naming.
- When adding or changing a site override, compare the same relative path in `projects/assets/templates/` first.
