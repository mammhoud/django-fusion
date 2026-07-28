# CTC Research

> **Site:** `applications/ctc-research/` · **Domain:** https://ctc-research.com
> **Variant:** `layout/landing/skeleton.html` + `layout/learning/skeleton.html`
> **Routing style:** Wagtail Pages + django-fusion Applications
> **AGENTS:** [`applications/ctc-research/AGENTS.md`](../../../applications/ctc-research/AGENTS.md)
> **Prompts:** [`applications/ctc-research/PROMPTS.md`](../../../applications/ctc-research/PROMPTS.md)

---

## Architecture Overview

CTC Research is the **primary LMS site** and medical-research publication surface. It combines
Wagtail-managed CMS pages with django-fusion's component routing system. The LMS plugin here
(`plugins/lms/`) is canonical — `lms-demo` mirrors its structure for parity.

### Site / Application Tree

```
CTCResearchSite (Site, autodiscovery ON)
├── Articles (Application)          — publication domain, Wagtail Page models
├── LMSApp (Application)            — shared LMS surface (courses, modules, progress)
├── Courses (Application)           — Wagtail-driven course catalog
├── Blog (Application)              — HTMX-driven blog with FragmentComponent
├── Account (Application)           — auth + 2FA (TOTP), social auth (Google, GitHub)
└── Profile (Application)           — user settings, 2FA management
```

### Template Resolution

1. `ctc-research/templates/` — site overrides (highest)
2. `ctc-research/plugins/<name>/templates/` — plugin templates
3. `ctc-research/plugins/components/` — site-specific components
4. `assets/templates/` — shared templates (lowest)

### Plugins

| Plugin | Purpose | Key Files |
|--------|---------|-----------|
| **accounts** | Auth, social auth, 2FA, email templates | `adapters.py`, `views/allauth.py` |
| **blog** | Blog posts (Wagtail Page model) | `models.py`, `templates/blog/` |
| **lms** | Courses, modules, enrollments | `models.py`, `templates/lms/`, `views/courses.py` |
| **profile** | User profile, settings, 2FA | `templates/profile/` |
| **components** | Site-specific UI blocks | `blocks/`, `common/`, `contact/` |

### Layout Variants

| Variant | Use Case |
|---------|----------|
| `layout/landing/` | Public-facing pages (home, about, contact, services) |
| `layout/learning/` | Course pages, LMS sub-pages |
| `layout/profile/` | User profile, settings |
| `layout/auth/` | Login, signup, password reset |

### Auth & Accounts

- **Adapter:** `plugins.accounts.adapters.RegistrationAdapter` (HTMX-aware, fragment rendering)
- **2FA:** TOTP-based via `two_factor_enabled` / `two_factor_secret` on profile model
- **Social auth:** Google, GitHub — adapters in `plugins/accounts/adapters.py`
- **Email templates:** Wagtail snippets via `AuthEmailTemplate` from `django_fusion.wagtail.snippets`
- **Flows:** login, signup, password reset, password change, email management, social signup, social connections

### Fragment Naming

All HTMX fragments use dot-notation: `ctc.fragments.<app>.<name>`
- `ctc.fragments.blog.post_list` — blog listing
- `ctc.fragments.lms.course_detail` — LMS course detail
- `ctc.fragments.lms.course_progress` — enrollment progress

---

## Site-Specific Patterns

1. **ARTICLE-typed Wagtail Pages** dominate the publication surface. See `applications/ctc-research/www/<page>/models.py`.
2. **Form field audit (`contact-section` BEM):** the canonical `applications/assets/templates/components/form/form_field.html` is the SINGLE source of truth; site adapters in `plugins/components/blocks/partials/form_field.html` pass `class_field` overrides.
3. **`plugins/components/`** hosts CTC-specific blocks (`blocks/`, `common/`, `contact/`) — these take priority over `assets/templates/components/` for CTC-scoped renders. If a block is reused across sites, promote it to `assets/templates/components/blocks/`.
4. **Auth email templates** are managed as Wagtail snippets — do not add raw email template files without a corresponding `AuthEmailTemplate` snippet.
5. **Section markers** in `main.html` files use the standard `{# @section: <name> #}` form.

---

## Commands

```bash
# Django checks
make -C applications check WEBSITE=ctc-research

# Run tests
make -C applications test WEBSITE=ctc-research

# Migrate
make -C applications makemigrations WEBSITE=ctc-research
make -C applications migrate WEBSITE=ctc-research

# Lint
make -C applications lint

# Type check
make -C applications typecheck WEBSITE=ctc-research
```

---

## See Also

- [`../shared_lms.md`](../shared_lms.md) — shared LMS Application surface with lms-demo
- [`applications/ctc-research/AGENTS.md`](../../../applications/ctc-research/AGENTS.md) — template tree, conventions, step-by-step task guides
- [`applications/ctc-research/PROMPTS.md`](../../../applications/ctc-research/PROMPTS.md) — AI prompt catalog for CTC Research
- [`../../../applications/libs/django-fusion/docs/COMPONENT_TAG.md`](../../../applications/libs/django-fusion/docs/COMPONENT_TAG.md) — `{% comp %}` props/slots/vars reference
- [`../../../applications/libs/django-fusion/docs/VIEWFLOW_MAPPING.md`](../../../applications/libs/django-fusion/docs/VIEWFLOW_MAPPING.md) — django-material → django-fusion mapping
- [`../../architecture/routable_site.md`](../../reference/architecture/routable_site.md) — Site registration patterns
