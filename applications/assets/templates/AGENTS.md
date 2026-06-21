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
