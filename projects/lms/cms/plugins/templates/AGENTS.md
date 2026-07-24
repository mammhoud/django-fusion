# Plugin Template Guide — General Plugin Templates (CTC Research)

**Path:** `projects/ctc-research/plugins/templates/` — Shared plugin-level templates

## Scope
Shared templates across all CTC Research plugins. Cross-cutting UI used by accounts, blog, LMS, and profile plugins.

## Resolution Context
```
1. Site templates (projects/ctc-research/templates/) ← highest priority
2. Plugin-specific templates (plugins/<name>/templates/)
3. Shared plugin templates (this directory)            ← you are here
4. Shared templates (projects/assets/templates/)       ← fallback
```

## Quick Reference

### Available Components
| Component | Tag | Context Needed |
|-----------|-----|---------------|
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Notification | `{% comp "notification" /%}` | `message`, `type` |
| Pagination | `{% comp "pagination/numbers" /%}` | `page_obj` |
| Table | `{% comp "table" /%}` | `headers`, `rows` |
| Breadcrumbs | `{% comp "breadcrumbs" /%}` | `breadcrumbs` list |

### Common Patterns
- **Form rendering**: `{% comp "form/form" form=form /%}`
- **Modal dialogs**: `{% comp "modal/modal" modal_id="..." title="..." %}`
- **HTMX fragments**: Use `fragment_name` context key for server responses
- **Error pages**: Override at `errors/404.html`, `errors/500.html`

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve Django/Wagtail context variables and block tags

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. Use the site-specific plugins for custom behavior; this directory for shared UI
