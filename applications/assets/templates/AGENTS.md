# Shared Template Lookup Strategy

Scope: all templates under `applications/assets/templates/`.

## Role in Template Resolution

This directory is the shared template layer for Structa Cloud sites. Shared templates are loaded after the active site's root and asset template directories, but before Django app template discovery, via `applications/configs/base/templates.py`.

Use this directory for:
- Identical templates used by more than one site.
- Cross-site include components that preserve existing include names and context variables.
- Shared fallback templates for plugin and Wagtail app template names.

Do not use this directory for:
- Site branding shells that intentionally differ by site.
- Templates whose output depends on a site-specific layout contract unless that contract is expressed through explicit blocks or context variables.

## Consolidation Rules

1. Generate duplicate reviews with `python applications/scripts/template_duplicate_map.py`.
2. Treat exact SHA-256 matches across sites as shared candidates.
3. Move exact cross-site matches here using the same relative template path so existing `{% include %}`, `{% extends %}`, Wagtail `template = ...`, and Django render calls keep working.
4. Delete site copies only when the shared relative path can satisfy the same include name safely through configured template lookup.
5. For branded variations, keep a small site template in the site path and move only reusable markup into `components/` includes.
6. Preserve context variable names, especially `fragment_name`, form variables, page objects, and Wagtail block values.
7. If a site must override a shared template, keep the override thin and document why in the nearest site-level template `AGENTS.md`.

## Classification Summary

- **Identical shared templates**: exact SHA-256 matches consolidated here and deleted from site roots.
- **Mostly-identical branded templates**: keep site shell templates; extract reusable pieces into `components/` while preserving current include names and context.
- **Truly site-specific templates**: remain in the site tree when the relative path has different markup, copy, behavior, or brand contract.
# Template Root Instructions: Shared Templates

## Scope
This directory is the shared template root for cross-site Django/Wagtail UI in Structa Cloud. Prefer templates here when a component, layout, email, section, block, fragment, or modal is intended to be reused by more than one site.

## Expected Template Structure
Use these folders consistently when adding or moving templates:

- `base/` for base documents, shell templates, and root inheritance targets.
- `layout/` for page chrome, navigation, footers, wrappers, grids, and shared layout partials.
- `components/` for reusable, context-driven UI components.
- `sections/` for larger page sections composed from components.
- `blocks/` for Wagtail StreamField/block templates.
- `fragments/` for fragment-rendered templates; use `fragment_name` for identifiers and context keys.
- `modals/` for modal dialogs and overlays.
- `email/` for email-specific templates and partials.
- Page-specific folders for templates that only support one page or route.

## Rules for AI-Assisted Template Edits
- Prefer shared templates from `applications/assets/templates` for cross-site components.
- Prefer site templates for site-only presentation.
- Preserve existing Django/Wagtail context variables, filters, inclusion tags, block tags, `{% load %}` statements, and template inheritance contracts.
- Use `fragment_name` for fragment identifiers and context keys; do not introduce alternate names for the same concept unless maintaining compatibility with existing code.
- Use `{% include %}` for reusable components and pass only the context needed by the included template.
- Do not replace dynamic content, CMS-managed fields, translations, URLs, forms, permissions, or feature flags with static demo text.

## CSS Class Guidance
- Use BEM-style class names for reusable template markup, for example `card`, `card__title`, and `card--featured`.
- Keep styling hooks as classes, not IDs. Do not add IDs for styling.
- Preserve existing class names when templates are already coupled to SCSS, JavaScript, tests, or analytics.

## Customization Tips
- Find related templates with `find applications -path '*/templates' -type d` and targeted `rg` searches for template names, block names, include paths, context variables, and CSS classes.
- Before replacing a component, inspect the current template and the closest shared/site/plugin equivalent, then map each dynamic binding to the replacement.
- Replace components with equivalent data bindings: keep URLs, images, Wagtail page fields, StreamField values, form fields, translations, and permission checks connected to their original context.
- If a change is cross-site, add or update a shared template here and include/extend it from site-specific templates. If it is site-only, keep the override in the relevant site template root.
