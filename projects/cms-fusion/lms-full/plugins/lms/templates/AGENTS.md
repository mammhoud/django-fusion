# Plugin Template Guide — LMS Plugin

**Path:** `projects/lms/plugins/lms/templates/` — LMS plugin templates

## Scope
Plugin-specific templates for the LMS (Learning Management System) plugin. These templates render course catalogs, lesson pages, enrollment flows, and learning UI components.

## Resolution Context
```
1. Site templates (projects/lms/templates/) ← highest priority
2. Plugin templates (this directory)           ← you are here
3. App templates (projects/lms/www/**/templates/)
4. Shared templates (projects/assets/templates/) ← fallback
```

## Quick Reference

### Available Components (from shared library)
| Component | Tag | Context Needed |
|-----------|-----|---------------|
| Chat Bubble | `{% comp "chat/bubble" /%}` | `message`, `role` |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Pagination | `{% comp "pagination/numbers" /%}` | `page_obj` |
| Table | `{% comp "table" /%}` | `headers`, `rows` |

### django-fusion Built-ins
See `projects/assets/templates/components/AGENTS.md` for the full inventory.

### Common Patterns for This Plugin
- **Course list**: `{% comp "lms/course_card" course=course /%}`
- **Lesson viewer**: `{% extends "layout/learning/skeleton.html" %}`
- **Enrollment button**: HTMX-triggered modal with `fragment_name="enroll_form"`
- **Progress tracking**: Use `fragment_name="progress_bar"` for HTMX updates

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve Django/Wagtail context variables, block tags, and template inheritance

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. Check related app, plugin, site, and shared templates with `rg` for include paths, block names, and context variables
4. Use `{% comp "path" /%}` for auto-registered components; `{% include %}` for dynamic names
