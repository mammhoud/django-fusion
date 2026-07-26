# Plugin Template Guide — Portfolio Accounts Plugin

**Path:** `projects/portfolio/plugins/accounts/templates/` — Accounts plugin for Portfolio

## Scope
Plugin-specific templates for authentication and account management in the Portfolio/VResume site. These render login/signup forms, password flows, and social auth UI.

## Resolution Context
```
1. Site templates (projects/portfolio/templates/) ← highest priority
2. Plugin templates (this directory)               ← you are here
3. App page templates (projects/portfolio/www/pages/**/templates/)
4. Shared templates (projects/assets/templates/)   ← fallback
```

## Quick Reference

### Available Components
| Component | Tag | Context Needed |
|-----------|-----|---------------|
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Notification | `{% comp "notification" /%}` | `message`, `type` |

### Common Patterns for Portfolio Auth
- **Login modal**: HTMX-triggered with `fragment_name="login_form"`
- **Signup**: Extends `base_auth.html` with allauth overrides
- **Social auth**: Google/GitHub login via `socialaccount/` templates
- **Tab-based navigation**: Auth flows integrate with Portfolio's tab system

### Key Templates
| Template | Purpose |
|----------|---------|
| `accounts/login.html` | allauth login override |
| `accounts/signup.html` | allauth signup override |
| `socialaccount/` | Social auth provider templates |

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve django-allauth template block names and context variables

## Customization Tips
1. Check `plugins/accounts/adapters.py` for HTMX-aware view overrides
2. Social auth adapter: `AuthHTMXSocialAccountAdapter`
3. Use `{% comp_include %}` for component tracking in auth flows
4. Extend allauth's base templates, don't copy them
