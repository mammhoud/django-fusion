# Plugin Template Guide — Blog Plugin

**Path:** `projects/lms/plugins/blog/templates/` — Blog plugin templates

## Scope
Plugin-specific templates for the Blog feature. These render blog post listings, detail pages, categories, and related content.

## Resolution Context
```
1. Site templates (projects/lms/templates/) ← highest priority
2. Plugin templates (this directory)           ← you are here
3. App templates (projects/lms/www/**/templates/)
4. Shared templates (projects/assets/templates/) ← fallback
```

## Quick Reference

### Available Components
| Component | Tag | Context Needed |
|-----------|-----|---------------|
| Pagination | `{% comp "pagination/numbers" /%}` | `page_obj` |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Search | `{% comp "search/search" /%}` | `form` |
| Breadcrumbs | `{% comp "breadcrumbs" /%}` | `breadcrumbs` list |

### Common Patterns for This Plugin
- **Blog listing**: `{% comp "blog/post_card" post=post /%}`
- **Blog detail**: `{% extends "layout/landing/skeleton.html" %}`
- **Category filter**: HTMX-triggered with `fragment_name="post_list"`
- **Share buttons**: Social share component with URL context
- **Related posts**: `fragment_name="related_posts"` for HTMX lazy-load

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve Django/Wagtail context variables, block tags, and template inheritance

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. Check related app, plugin, site, and shared templates with targeted searches for include paths, block names, and context variables
4. Use `{% comp "path" /%}` for auto-registered components; `{% include %}` for dynamic names
