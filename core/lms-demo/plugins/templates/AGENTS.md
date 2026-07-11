# Template Root Instructions: Plugin-specific templates

## Scope
This directory is a plugin-specific template root for `core/lms-demo/plugins/templates`. Follow the shared template rules in `core/assets/templates/AGENTS.md` first, then apply these local notes.

## Expected Template Structure
Use the shared folder conventions when adding templates: `base/`, `layout/`, `components/`, `sections/`, `blocks/`, `fragments/`, `modals/`, `email/`, and page-specific folders. Create only the folders that make sense for this local template root.

## Local Override Notes
- Keep templates here focused on plugin behavior, plugin UI, and plugin-local overrides.
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
