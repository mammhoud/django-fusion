# LMS Demo (structa.cloud)

> **Site:** `applications/lms-demo/` · **Domain:** https://structa.cloud
> **Variant:** `layout/landing/skeleton.html` + `layout/learning/skeleton.html`
> **Routing style:** RoutableComponent + Wagtail Pages + django-fusion Applications
> **AGENTS:** [`applications/lms-demo/AGENTS.md`](../../../applications/lms-demo/AGENTS.md)
> **Prompts:** [`applications/lms-demo/PROMPTS.md`](../../../applications/lms-demo/PROMPTS.md)

---

## Architecture Overview

LMS Demo is the Structa Cloud **product surface** — a CMS-leaning marketing site layered with
LMS demos (course cards, enrollment flows, dashboards). It uses `show_all_applications: True`
auto-discovery; new Apps appear automatically when imported by an INSTALLED_APP.

### Site / Application Tree

```
LMSDemoSite (Site, autodiscovery ON)
├── Accounts (Application)          — auth + 2FA, social auth
├── LMSApp (Application)            — courses, modules, enrollment progress
├── Blog (Application)              — HTMX-driven blog posts
├── Portfolio (Application)         — project showcase
├── Profile (Application)           — user settings, certifications, learning progress
└── Certification (Application)     — shareable certificate detail pages
```

### Template Resolution

1. `lms-demo/templates/` — site overrides (highest)
2. `lms-demo/plugins/<name>/templates/` — plugin templates
3. `lms-demo/plugins/components/` — site-specific components
4. `assets/templates/` — shared templates (lowest)

### Plugins

| Plugin | Purpose | Key Files |
|--------|---------|-----------|
| **accounts** | Auth, social auth, certifications | `adapters.py`, `templates/certification/` |
| **blog** | Blog posts, comments | `models.py`, `templates/blog/` |
| **lms** | Courses, modules, enrollments, emails | `models.py`, `templates/lms/`, `views/courses.py` |
| **profile** | User profile, 2FA, learning progress | `templates/profile/` |
| **components** | Site-specific UI blocks | `auth/`, `profile/`, `blocks/` |

### Layout Variants

| Variant | Use Case |
|---------|----------|
| `layout/landing/` | Public marketing pages (home, about, contact, services) |
| `layout/learning/` | Course catalog, LMS sub-pages |
| `layout/profile/` | User profile, settings, certifications |
| `layout/auth/` | Login, signup, password reset |
| `layout/apps/` | Application-style dashboard pages |

### Auth & Accounts

- **Adapter:** `plugins.accounts.adapters.RegistrationAdapter`
- **2FA:** TOTP-based via `two_factor_enabled` on profile model
- **Social auth:** `AuthHTMXSocialAccountAdapter` for Google, GitHub
- **Certifications:** Shareable certificate detail page at `/certification/<uuid>/`
- **Flows:** login, signup, password reset, password change, email management

### WebSocket Support

Real-time learning progress events via Django Channels in `lms-demo/www/websocket.py`:
- `lesson_completed` — updates progress record and broadcasts to connected clients
- Enables real-time dashboards and progress tracking

### Fragment Naming

All HTMX fragments use dot-notation: `lms.fragments.<app>.<name>`
- `lms.fragments.courses.enrollment_status` — enrollment/checkout status
- `lms.fragments.lms.enrollment_status` — course enrollment progress
- `lms.fragments.certification.detail` — certification detail page

---

## Site-Specific Patterns

1. **`show_all_applications: True`**: Applications auto-register via INSTALLED_APPS imports — no manual registration needed.
2. **No Wagtail CMS on top-level pages**: Pages are class-based `RoutableComponent` views, not Wagtail Page tree items. Wagtail is used for admin/Snippet management.
3. **LMS plugin mirrors `ctc-research/plugins/lms/`**: Keep them in sync or extract to a shared lib if they diverge significantly.
4. **HTMX throughout**: Every interactive surface responds to `HX-Request: true` and emits a fragment. Modal login/signup swaps into `#modal-container`.
5. **WebSocket for real-time**: `lms-demo/www/websocket.py` must not be removed — enables real-time learning progress.

---

## Commands

```bash
# Django checks
make -C applications check WEBSITE=lms-demo

# Run tests
make -C applications test WEBSITE=lms-demo

# Migrate
make -C applications makemigrations WEBSITE=lms-demo
make -C applications migrate WEBSITE=lms-demo

# Lint
make -C applications lint

# Type check
make -C applications typecheck WEBSITE=lms-demo
```

---

## See Also

- [`../shared_lms.md`](../shared_lms.md) — shared LMS Application surface with ctc-research
- [`applications/lms-demo/AGENTS.md`](../../../applications/lms-demo/AGENTS.md) — template tree, conventions, step-by-step task guides
- [`applications/lms-demo/PROMPTS.md`](../../../applications/lms-demo/PROMPTS.md) — AI prompt catalog for LMS Demo
- [`../../../applications/libs/django-fusion/docs/COMPONENT_TAG.md`](../../../applications/libs/django-fusion/docs/COMPONENT_TAG.md) — `{% comp %}` props/slots/vars reference
- [`../../../applications/libs/django-fusion/docs/ROUTING_SYSTEM.md`](../../../applications/libs/django-fusion/docs/ROUTING_SYSTEM.md) — URL routing and navigation
- [`../../architecture/routable_site.md`](../../reference/architecture/routable_site.md) — Site registration patterns
