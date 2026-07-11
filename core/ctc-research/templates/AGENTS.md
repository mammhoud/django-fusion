# Site Template Overrides

Scope: this site template tree.

## Lookup Strategy

Site templates here are resolved before the shared `core/assets/templates/` layer. Keep files in this tree only when they are intentional site-specific overrides, branded shells, or templates that must shadow shared behavior.

## Override Rules

- Prefer deleting exact duplicates and allowing Django to load `core/assets/templates/<relative-path>`.
- Keep thin overrides for branded variations; move reusable repeated markup into shared includes under `core/assets/templates/components/`.
- Preserve existing template names, include names, block names, and context variables to avoid breaking Wagtail/Django rendering.
- Use `fragment_name` for fragment identifiers and context keys; do not introduce alternate fragment naming.
- When adding or changing a site override, compare the same relative path in `core/assets/templates/` first.
# Template Root Instructions: Site Templates

## Scope
This directory is a site-specific template root for `core/ctc-research/templates`. Follow the shared template rules in `core/assets/templates/AGENTS.md` first, then apply these local notes.

## Expected Template Structure
Use the shared folder conventions when adding templates: `base/`, `layout/`, `components/`, `sections/`, `blocks/`, `fragments/`, `modals/`, `email/`, and page-specific folders. Create only the folders that make sense for this local template root.

## Local Override Notes
- Keep templates here focused on site-only presentation and template overrides.
- Prefer `core/assets/templates` for cross-site components and shared behavior.
- Prefer this template root for presentation or overrides that are specific to this scope.
- Preserve Django/Wagtail context variables, template tags, inheritance, includes, translations, permissions, and CMS-managed fields.
- Use `fragment_name` for fragment identifiers and context keys.
- Use `{% include %}` for reusable components. Do not replace dynamic content with static demo text.
- Use BEM-style CSS classes and do not use IDs for styling.

## Customization Tips
- Search nearby templates first, then shared templates, before adding a new partial.
- When replacing a component, copy the equivalent data bindings from the old markup to the new include or partial.
- Check related app, plugin, site, and shared templates with targeted `rg` searches for include paths, block names, context variables, and CSS classes.
