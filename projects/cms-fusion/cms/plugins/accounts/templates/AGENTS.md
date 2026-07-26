# Plugin Template Guide — Accounts Plugin (CTC Research)

**Path:** `projects/ctc-research/plugins/accounts/templates/` — Auth/accounts plugin for CTC Research

## Scope
Plugin-specific templates for authentication in the CTC Research site. Login/signup modals, password flows, email confirmations, and social auth UI.

## Resolution Context
```
1. Site templates (projects/ctc-research/templates/) ← highest priority
2. Plugin templates (this directory)                   ← you are here
3. Shared templates (projects/assets/templates/)       ← fallback
```

## Quick Reference

### Available Components
| Component | Tag | Context Needed |
|-----------|-----|---------------|
| Form | `{% comp "form/form" /%}` | Django `form` object |
| Modal | `{% comp "modal/modal" /%}` | `modal_id`, `title` |
| Notification | `{% comp "notification" /%}` | `message`, `type` |

### Common Patterns
- **Login modal**: HTMX-triggered with `fragment_name="login_form"`
- **Signup**: `{% extends "base_auth.html" %}` with allauth overrides
- **Password reset**: `fragment_name="password_reset_form"`
- **Email**: Auth email templates as Wagtail snippets via `AuthEmailTemplate`
- **2FA**: TOTP-based via `two_factor_enabled` / `two_factor_secret` on profile

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
5. Auth email templates are CMS-managed — don't hardcode email content
