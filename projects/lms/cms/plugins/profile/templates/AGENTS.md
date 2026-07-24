# Plugin Template Guide — Profile Plugin (CTC Research)

**Path:** `projects/ctc-research/plugins/profile/templates/` — User profile plugin for CTC Research

## Scope
User profile templates for the CTC Research site. Profile pages, settings forms, and user activity.

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
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Table | `{% comp "table" /%}` | `headers`, `rows` |

### Common Patterns
- **Profile view**: `{% extends "layout/profile/skeleton.html" %}`
- **Settings**: HTMX with `fragment_name="settings_form"`
- **Activity history**: `fragment_name="activity_list"` for HTMX pagination

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve Django/Wagtail context variables, block tags, and template inheritance

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
