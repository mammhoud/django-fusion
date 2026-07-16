# Auth System Overview

The auth system integrates **django-allauth** with an **HTMX + SSE fragment-based UI** across both `ctc-research.com` and `structa.cloud`.

## Architecture

All auth pages are pure fragment templates under `templates/auth/`. A custom allauth adapter (`AuthHTMXAdapter`) handles the difference between HTMX and full-page requests:

- **HTMX request** (`HX-Request: true`) → returns bare `<section class="fragment--form">` for in-place swapping
- **Full-page request** → wraps the fragment in `layout/auth/skeleton.html` (the split-layout chrome)

```
Browser GET /auth/login/
    │
    ├── HX-Request: true  →  AuthHTMXAdapter  →  auth/login.html (bare fragment)
    │
    └── (no header)       →  AuthHTMXAdapter  →  skeleton.html wrapping auth/login.html
```

## URL Namespace

All auth routes use the `plugins` namespace (replacing the legacy `pipelines` namespace):

| URL | Name |
|-----|------|
| `/auth/login/` | `plugins:login` |
| `/auth/logout/` | `plugins:logout` |
| `/auth/register/` | `plugins:register` |
| `/auth/password/forgot/` | `plugins:password_forgot` |
| `/auth/privacy-modal/` | `plugins:privacy_modal` |
| `/auth/newsletter/subscribe/` | `plugins:subscribe_newsletter` (ctc only) |

allauth's own URLs are mounted at `/accounts/` via `include("allauth.urls")`.

## Key Components

| Component | Location |
|-----------|----------|
| Custom adapter | `plugins/accounts/adapters.py` |
| URL config | `plugins/urls.py` |
| Auth templates | `templates/auth/` |
| Auth settings | `configs/base/auth.py` |

## Sections

- [Adapter](adapter.md) — `AuthHTMXAdapter` configuration and customization
- [Templates](templates.md) — Fragment template pattern and BEM CSS standards
- [Social Login](social-login.md) — Google and Facebook OAuth setup
- [Testing](testing.md) — Property-based and integration test patterns
