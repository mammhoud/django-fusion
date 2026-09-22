---
Object type: Workspace
Tags: auth, security
Status: Published
---

# Auth — Authentication & Authorization System

> **Type:** Workspace 🏢
> **Description:** Cross-site authentication powered by django-allauth with django-fusion auth mixins. Supports email/password, social login, MFA (TOTP), and HTMX-based flows.

---

## Overview

Auth is implemented uniformly across all sites using django-allauth:

| Auth Feature | Status | Implementation |
|-------------|--------|----------------|
| Email/Password Login | ✅ Complete | allauth account adapter |
| Social Login (Google, GitHub) | ✅ Complete | Social account adapters |
| Registration | ✅ Complete | HTMX modal flows |
| Password Reset | ✅ Complete | Email-based reset |
| MFA (TOTP 2FA) | ✅ Complete | Two-factor auth in profile |
| WebAuthn / Passkeys | 📋 Planned | allauth.mfa WebAuthn |
| Session Management | ✅ Complete | django-fusion session mixins |

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

## Supporting Libraries

| Library | Role |
|---------|------|
| `django-allauth` | Auth framework |
| `django-fusion` | Auth mixins (LoginRequiredMixin, PermissionRequiredMixin) |
| `hijack` (dev only) | Impersonation for debugging |

---

## Project Context

| Aspect | Description |
|--------|-------------|
| **Library** | django-allauth + django-fusion auth mixins |
| **Color** | Blue (#3b82f6) / Indigo (#6366f1) — representing trust, security, and identity |
| **Account Adapter** | `plugins.accounts.adapters.RegistrationAdapter` (HTMX-aware) |
| **MFA Model** | `two_factor_enabled` / `two_factor_secret` on profile model |

---

## Color Palette: Auth Blue

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#3b82f6` (Blue-500) | Login buttons, auth form accents |
| Surface | `#eff6ff` / `#172554` | Auth pages (light/dark) |
| Accent | `#6366f1` (Indigo-500) | MFA indicators, 2FA badges |
| Success | `#22c55e` (Green-500) | Verified, authenticated |
| Danger | `#ef4444` (Red-500) | Auth errors, lockouts |

---

## Related Docs

- → `../../../../AGENTS.md` — Auth adapter details
- → `../../../../projects/structa.cloud/backend/apps/auth/adapters.py` — Auth implementation
- → `../README.md` — Master index
