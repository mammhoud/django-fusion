# Plugin Template Guide — Accounts Plugin

**Path:** `projects/lms/plugins/accounts/templates/` — Auth/accounts plugin templates

## Scope
Plugin-specific templates for authentication and account management. These render login/signup forms, password flows, email confirmations, and social auth UI.

## Resolution Context
```
1. Site templates (projects/lms/templates/) ← highest priority
2. Plugin templates (this directory)           ← you are here
3. Shared templates (projects/assets/templates/) ← fallback
```

## Quick Reference

### Available Components
| Component | Tag | Context Needed |
|-----------|-----|---------------|
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Notification | `{% comp "notification" /%}` | `message`, `type` |

### Common Patterns for This Plugin
- **Login modal**: HTMX-triggered with `fragment_name="login_form"`
- **Signup**: `{% extends "base_auth.html" %}` with allauth overrides
- **Password reset**: `fragment_name="password_reset_form"` for inline flow
- **Email confirmation**: Template in `email/` subdirectory
- **Social auth**: `allauth` templates in `socialaccount/` subdirectory
- **2FA setup**: TOTP form with `fragment_name="two_factor_form"`

### Key Templates in This Plugin
| Template | Purpose |
|----------|---------|
| `accounts/login.html` | allauth login override |
| `accounts/signup.html` | allauth signup override |
| `accounts/password_reset.html` | Password reset form |
| `email/` | Auth email templates (snippets) |
| `socialaccount/` | Social auth provider templates |

## Conventions
- Use `fragment_name` for HTMX fragment identifiers and context keys
- Use `{% include %}` for reusable components; pass only required context
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Preserve django-allauth template block names and context variables

## Customization Tips
1. Check `plugins/accounts/adapters.py` for HTMX-aware view overrides
2. Auth email templates are managed as Wagtail snippets via `AuthEmailTemplate`
3. Use `{% comp_include %}` for component tracking in auth flows
4. Extend allauth's base templates, don't copy them
