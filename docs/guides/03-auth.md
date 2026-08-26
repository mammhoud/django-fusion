---
title: Auth
description: Authentication across all Structa Cloud projects — POS superuser, Django allauth, OAuth, MFA, WebAuthn.
navigation:
  title: Auth
  icon: i-lucide-lock
object:
  type: "guide"
  id: "guide.auth"
attributes:
  source_path: "guides/03-auth.md"
  canonical_route: "/docs/en/guides/03-auth"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - onboarding
  - auth
  - superuser
  - oauth
  - mfa
  - webauthn
links:
  - label: "Setup & Build"
    to: "/guides/02-setup"
    icon: "i-lucide-wrench"
  - label: "Dev"
    to: "/guides/04-dev"
    icon: "i-lucide-code"
  - label: "POS Auth Deep Dive"
    to: "/projects/pos/backend/rust-auth"
    icon: "i-lucide-shield"
---

# 🔐 Auth — Authentication Guide

> **Related:** `projects/pos/backend/rust-auth.md`, `libs/auth-customization.md`, `back-env/`
> **Tags:** #auth #login #superuser #oauth #mfa #session

How authentication works across all Structa Cloud projects and how to configure it.

---

## POS Desktop App Auth

### How It Works

```
App launch
  └── check_auth_required(db_path)
       ├── SUPERUSER_EMAIL+PASSWORD set? → Show login screen
       ├── SMTP configured? → Email confirmation code flow
       └── Neither? → Skip auth, open Home directly
```

> 💡 **Tip:** For development, set `SUPERUSER_EMAIL=dev@test.com` and `SUPERUSER_PASSWORD=dev` in `projects/pos/.env`. The superuser is auto-created on first launch with bcrypt-hashed password.

### Enabling Auth

1. Set both env vars in `projects/pos/.env`:
   ```bash
   SUPERUSER_EMAIL=admin@restaurant.com
   SUPERUSER_PASSWORD=your-secure-password
   SUPERUSER_NAME=Admin              # optional
   ```

2. Launch the app — first screen becomes Login
3. Login with the superuser email + password
4. Profile button appears in top-right showing user email

> ⚠️ **Warning:** If only ONE of `SUPERUSER_EMAIL`/`SUPERUSER_PASSWORD` is set, auth is NOT enabled. Both must be set.

### Profile/Logout Button

- Shows avatar circle (first letter of name) + email in top bar
- Click → dropdown with user info + **Sign Out** button
- Closes on outside click
- Only visible when auth is enabled AND user logged in

### Inactivity Warning

When auth is enabled, the app tracks user inactivity:
- Yellow warning banner slides down after configurable timeout
- Click **Stay** to dismiss
- ❌ **Not customizable** — behavior is in `AuthContext.tsx`

### SMTP Email Auth

Alternative to superuser auth:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your-app-password
SMTP_RECIPIENT='Support <support@site.com>'
```

Users receive confirmation codes via email.

---

## Django Sites Auth (precis-ctc, lms, VResume)

### Framework

All sites use `django-allauth` with `django-fusion` auth mixins.

### Auth Flow

```
Browser GET /auth/login/
├── HX-Request: true  → AuthHTMXAdapter → bare fragment (auth/login.html)
└── No HX header      → AuthHTMXAdapter → skeleton.html wrapping fragment
```

### Adapters

| Adapter | Location | Role |
|---------|----------|------|
| `AuthHTMXAdapter` | `plugins/accounts/adapters.py` | Maps allauth templates → HTMX fragments |
| `AuthHTMXSocialAccountAdapter` | Same file | Social login handling |
| `RegistrationAdapter` | Same file | Routes email confirmations |

> 💡 **Tip:** All three adapters live in `plugins/accounts/adapters.py` in each site. They follow the same pattern — copy from one site to another if needed.

### Social Login

Google and Facebook OAuth supported. Set env vars:
```bash
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_SECRET=...
FACEBOOK_OAUTH_CLIENT_ID=...
FACEBOOK_OAUTH_SECRET=...
```

> ⚠️ **Warning:** Social login buttons MUST use `<a>` tags, NEVER `hx-post`. OAuth redirects don't work with HTMX.

### MFA / 2FA

Custom TOTP-based 2FA available in profile settings:
- `two_factor_enabled` flag on profile model
- `two_factor_secret` stores TOTP secret
- Optional `allauth.mfa` for WebAuthn/passkey support

### Template Mapping

| Allauth Default | Fragment Template |
|----------------|-------------------|
| `account/login.html` | `auth/login.html` |
| `account/signup.html` | `auth/register.html` |
| `account/password_reset.html` | `auth/forgot_page.html` |
| `account/password_reset_from_key.html` | `auth/reset_password.html` |
| `account/email_confirm.html` | `auth/verification_link.html` |
| `socialaccount/signup.html` | `auth/social_signup.html` |
| `socialaccount/connections.html` | `auth/social_connections.html` |

> 💡 **Tip:** To add a new auth view: create template in `templates/auth/` → add mapping in `AuthHTMXAdapter.TEMPLATE_MAP`.

---

## Quick Reference

| Task | POS | Django |
|------|-----|--------|
| Enable auth | Set `SUPERUSER_*` env vars | Configured by default |
| Add user | Auto-created from env | `manage.py createsuperuser` or admin |
| Change password | `ensure_superuser_exists` updates hash | Via profile page or admin |
| Social login | N/A | Google, Facebook OAuth |
| MFA | N/A | TOTP (profile) + optional WebAuthn |
| Password reset | N/A | Via email (SMTP required) |

---

## ## Remarks & Notes

- POS superuser is **not** a Django user; it lives in the POS SQLite DB.
- Django sites share the same allauth + HTMX adapter pattern — copy `plugins/accounts/adapters.py` between sites for consistency.
- For WebAuthn/passkey setup, see [WebAuthn Passkeys](auth/webauthn-passkeys.md).
- Allauth template overrides go in `templates/account/` (Django) or `templates/auth/` (fusion fragments).

---

→ [Back to Guides](README.md) | [POS Auth Deep Dive](/docs/en/projects/pos/backend/rust-auth) | [Auth Customization](/docs/en/libs/auth-customization) | [WebAuthn Passkeys](auth/webauthn-passkeys.md)

<!-- AI-generated: review needed -->