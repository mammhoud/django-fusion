# Site Template Overrides — LMS Demo

**Path:** `projects/lms/templates/` — Site-specific template overrides

## Lookup Strategy
Site templates here are resolved before the shared `projects/assets/templates/` layer. Keep files in this tree only when they are intentional site-specific overrides, branded shells, or templates that must shadow shared behavior.

## Resolution Context
```
1. Site templates (this directory)                    ← highest priority (you are here)
2. Plugin templates (projects/lms/plugins/**/templates/)
3. App templates (projects/lms/www/**/templates/)
4. Shared templates (projects/assets/templates/)      ← fallback
```

## Override Rules
- Prefer deleting exact duplicates and letting Django load `projects/assets/templates/<relative-path>`
- Keep thin overrides for branded variations; move reusable markup into shared includes
- Preserve existing template names, include names, block names, and context variables
- Use `fragment_name` for fragment identifiers and context keys; do not introduce alternate naming
- When adding or changing a site override, compare the same relative path in shared templates first

## Quick Reference

### Layout Variants Available
| Variant | Usage |
|---------|-------|
| `layout/apps/skeleton.html` | App-style layout |
| `layout/landing/skeleton.html` | Marketing/landing layout |
| `layout/learning/skeleton.html` | LMS/learning layout |
| `layout/profile/skeleton.html` | User profile layout |
| `layout/auth/skeleton.html` | Authentication layout |

### Available Components (from shared library)
| Component | Tag |
|-----------|-----|
| Form | `{% comp "form/form" /%}` |
| Modal | `{% comp "modal/modal" /%}` |
| Pagination | `{% comp "pagination/numbers" /%}` |
| Notification | `{% comp "notification" /%}` |
| Table | `{% comp "table" /%}` |
| Chat Bubble | `{% comp "chat/bubble" /%}` |
| Breadcrumbs | `{% comp "breadcrumbs" /%}` |
| Search | `{% comp "search/search" /%}` |

## Site-Specific Conventions
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Prefer `{% comp "path" /%}` over `{% include %}` for auto-registered components
- Use `{% extends "base_page.html" %}` for Wagtail pages
- Use `fragment_name` for HTMX fragment responses

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. Check plugins and shared templates with targeted searches for include paths, block names, and context variables
4. Use `{% comp_include %}` for component tracking in auth flows
