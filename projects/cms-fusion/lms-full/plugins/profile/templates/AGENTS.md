# Plugin Template Guide — Profile Plugin

**Path:** `projects/lms/plugins/profile/templates/` — Profile plugin templates

## Scope
Plugin-specific templates for user profiles. These render profile pages, settings forms, certifications, and user activity streams.

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
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Table | `{% comp "table" /%}` | `headers`, `rows` |
| Chat Bubble | `{% comp "chat/bubble" /%}` | `message`, `role` |

### Common Patterns for This Plugin
- **Profile view**: `{% extends "layout/profile/skeleton.html" %}`
- **Settings forms**: HTMX-triggered with `fragment_name="settings_form"`
- **Certification badges**: `{% comp "profile/cert_badge" cert=cert /%}`
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
3. Check related app, plugin, site, and shared templates with targeted searches
4. Use `{% comp "path" /%}` for auto-registered components; `{% include %}` for dynamic names
