# Plugin Template Guide — LMS Plugin (CTC Research)

**Path:** `projects/ctc-research/plugins/lms/templates/` — LMS plugin for CTC Research

## Scope
LMS plugin templates for the CTC Research site. Course catalogs, lesson pages, enrollment flows, and learning UI.

## Resolution Context
```
1. Site templates (projects/ctc-research/templates/) ← highest priority
2. Plugin templates (this directory)                  ← you are here
3. Shared templates (projects/assets/templates/)      ← fallback
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

### Common Patterns
- **Course list**: `{% comp "lms/course_card" course=course /%}`
- **Lesson viewer**: `{% extends "layout/learning/skeleton.html" %}`
- **Enrollment button**: HTMX-triggered modal with `fragment_name="enroll_form"`
- **Progress**: `fragment_name="progress_bar"` for HTMX updates

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
