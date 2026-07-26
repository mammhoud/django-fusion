# Site Template Overrides — CTC Research

**Path:** `projects/ctc-research/templates/` — Site-specific template overrides

## Lookup Strategy
Site templates here are resolved before the shared template layer. Keep files here only for intentional site-specific overrides, branded shells, or shadowed behavior.

## Resolution Context
```
1. Site templates (this directory)                          ← highest priority (you are here)
2. Plugin templates (projects/ctc-research/plugins/**/templates/)
3. Shared templates (projects/assets/templates/)            ← fallback
```

## Override Rules
- Prefer deleting exact duplicates and letting Django load shared templates
- Keep thin overrides for branded variations; move reusable markup into shared includes
- Preserve existing template names, include names, block names, and context variables
- Use `fragment_name` for fragment identifiers and context keys
- When adding or changing an override, compare same relative path in shared templates first

## Quick Reference

### Layout Variants
| Variant | Usage |
|---------|-------|
| `layout/apps/skeleton.html` | App-style layout |
| `layout/landing/skeleton.html` | Marketing/landing layout |
| `layout/learning/skeleton.html` | Learning layout |
| `layout/profile/skeleton.html` | User profile layout |
| `layout/auth/skeleton.html` | Authentication layout |

### Available Components
| Component | Tag |
|-----------|-----|
| Form | `{% comp "form/form" /%}` |
| Modal | `{% comp "modal/modal" /%}` |
| Pagination | `{% comp "pagination/numbers" /%}` |
| Notification | `{% comp "notification" /%}` |
| Table | `{% comp "table" /%}` |
| Breadcrumbs | `{% comp "breadcrumbs" /%}` |
| Search | `{% comp "search/search" /%}` |
| Chat Bubble | `{% comp "chat/bubble" /%}` |

### Site-Specific Templates
| Template | Purpose |
|----------|---------|
| `base_page.html` | Extends shared base, adds site chrome |
| `base_auth.html` | Auth layout wrapper |
| `base_profile.html` | Profile layout wrapper |
| `index.html` | Home page (HTMX dispatcher) |
| `home/main.html` | Home page sections |
| `about/` | About page templates |
| `contact/` | Contact page templates |

## Conventions
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Prefer `{% comp "path" /%}` over `{% include %}` when possible
- Use `fragment_name` for HTMX fragment responses
- Templates extend `base_page.html` for Wagtail pages

## Customization Tips
1. Search nearby templates first, then shared templates, before adding a new partial
2. When replacing a component, preserve context variable names and bindings
3. Check plugins and shared templates with targeted searches
