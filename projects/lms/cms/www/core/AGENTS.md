# App Template Guide — Core App (CTC Research)

**Path:** `projects/ctc-research/www/projects/templates/` — Core app templates

## Scope
App-specific templates for the Core application in the CTC Research site. These templates are owned by the Django app, not the site or a plugin.

## Resolution Context
```
1. Site templates (projects/ctc-research/templates/) ← highest priority
2. Plugin templates (projects/ctc-research/plugins/**/templates/)
3. App templates (this directory)                      ← you are here
4. Shared templates (projects/assets/templates/)       ← fallback
```

## Quick Reference

### Available Components
| Component | Tag | Context Needed |
|-----------|-----|---------------|
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Pagination | `{% comp "pagination/numbers" /%}` | `page_obj` |
| Notification | `{% comp "notification" /%}` | `message`, `type` |

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve Django/Wagtail context variables, block tags, and template inheritance

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. This is the lowest-priority template root; prefer site or plugin templates for overrides
