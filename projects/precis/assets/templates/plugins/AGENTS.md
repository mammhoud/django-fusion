# Plugin Templates Guide — Shared Plugins

**Path:** `projects/assets/templates/plugins/` — Shared plugin-level templates

## Scope
Shared plugin templates used across all Structa Cloud sites. These include email templates, error pages, newsletter forms, privacy policies, MFA flows, and pagination components.

## Resolution Context
```
1. Site-specific plugin templates (projects/<site>/plugins/**/templates/) ← highest
2. Shared plugin templates (this directory)                                  ← you are here
3. Shared components (projects/assets/templates/components/)
4. Shared base templates (projects/assets/templates/)                        ← fallback
```

## Available Templates

| Template | Purpose |
|----------|---------|
| `plugins/allauth.md` | Allauth template override guidance |
| `plugins/emails/` | Auth and notification email templates |
| `plugins/errors/` | Error pages (404, 500) |
| `plugins/newsletter/` | Newsletter signup components |
| `plugins/privacy/` | Privacy policy and consent components |
| `plugins/tables/` | Data table components |
| `plugins/pagination/` | Pagination components |

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve Django/Wagtail context variables and block tags
- Prefer `{% comp "path" /%}` over `{% include %}` when a django-fusion component exists

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. Site-specific overrides belong in `projects/<site>/templates/`, not here
4. Use targeted searches for include paths, block names, context variables, and CSS classes
