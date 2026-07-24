# App Template Guide — Connect App (Portfolio)

**Path:** `projects/portfolio/www/pages/connect/templates/` — Connect/Contact app templates

## Scope
App-specific templates for the Connect (contact) app in the Portfolio/VResume site. Contact forms, map integrations, and connection requests.

## Resolution Context
```
1. Site templates (projects/portfolio/templates/)           ← highest priority
2. Plugin templates (projects/portfolio/plugins/**/templates/)
3. App templates (this directory)                            ← you are here
4. Shared templates (projects/assets/templates/)             ← fallback
```

## Quick Reference

### Available Components
| Component | Tag | Context Needed |
|-----------|-----|---------------|
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Notification | `{% comp "notification" /%}` | `message`, `type` |

### Common Patterns
- **Contact form**: `{% comp "form/form" form=contact_form /%}`
- **Success message**: `fragment_name="success_message"` for HTMX response
- **Map integration**: Use shared map component with location coordinates

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve Django/Wagtail context variables and block tags

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. This is the lowest-priority template root; prefer site or plugin templates for overrides
