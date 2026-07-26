# Plugin Template Guide — Blog Plugin (CTC Research)

**Path:** `projects/ctc-research/plugins/blog/templates/` — Blog plugin for CTC Research

## Scope
Blog plugin templates for the CTC Research site. Blog post listings, detail pages, categories, and related content.

## Resolution Context
```
1. Site templates (projects/ctc-research/templates/) ← highest priority
2. Plugin templates (this directory)                  ← you are here
3. Shared templates (projects/assets/templates/)      ← fallback
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

### Common Patterns
- **Blog listing**: `{% comp "blog/post_card" post=post /%}`
- **Blog detail**: Extends `{% extends "layout/landing/skeleton.html" %}`
- **Category filter**: HTMX with `fragment_name="post_list"`
- **Related posts**: `fragment_name="related_posts"` for lazy-load

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve Django/Wagtail context variables, block tags, and template inheritance

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. Use `{% comp "path" /%}` for auto-registered components; `{% include %}` for dynamic names
