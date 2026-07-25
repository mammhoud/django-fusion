---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Tags:
    - auth
    - reference
Status: Published
---

# Auth — Quick Reference

> **Type:** Page 📄
> **Description:** Quick reference for auth flows and methods across all Structa Cloud sites.

---

## Auth Flow Summary

| Flow | URL Pattern | HTMX | Modal |
|------|------------|------|-------|
| Login | `/accounts/login/` | ✅ | ✅ |
| Signup | `/accounts/signup/` | ✅ | ✅ |
| Password Reset | `/accounts/password/reset/` | ✅ | ✅ |
| Password Change | `/accounts/password/change/` | ✅ | ✅ |
| Email Management | `/accounts/email/` | ✅ | ✅ |
| Social Login | `/accounts/social/login/` | ✅ | ✅ |
| Social Connections | `/accounts/social/connections/` | ✅ | ✅ |
| MFA Setup | `/accounts/2fa/setup/` | ✅ | ✅ |

---

## Supporting Libraries

| Library | Role |
|---------|------|
| `django-allauth` | Auth framework |
| `django-fusion` | Auth mixins (LoginRequiredMixin, PermissionRequiredMixin) |
| `hijack` (dev only) | Impersonation for debugging |

---

## Related Docs

- → `auth.md` — Full auth documentation
- → `../../AGENTS.md` — Auth configuration details
- → `../README.md` — Master index
