# LMS Demo — AI Agent Instructions

Path: `projects/cms/lms-full/` (Makefile alias: `lms`, deployed at structa.cloud:5071)

## Scope

This directory contains the LMS (Learning Management System) Django site — a Wagtail-powered e-learning platform with courses, certifications, blog, and user accounts. The site is deployed at **structa.cloud** on port 5071.

---

## Template Resolution Order (Django TEMPLATES_DIRS)

1. `lms/templates/` — site-specific overrides (highest priority)
2. `lms/plugins/<name>/templates/` — plugin templates
3. `lms/plugins/components/` — site component blocks
4. `assets/templates/` — shared cross-site templates (lowest priority)

---

## Site Template Tree

```
lms/templates/
├── base_page.html          # Extends shared base.html
├── base_profile.html       # Profile-specific base template
├── base_auth.html          # Auth-specific base template
├── index.html              # Home page template (HTMX dispatcher)
├── home/
│   └── main.html           # Home page content
│   └── sections/
│       └── clients.html    # Client logos section
├── about/                   # About page templates
├── auth/                    # Authentication templates
├── contact/                 # Contact page templates
├── errors/                  # Custom error pages (404, 500)
├── registration/            # Registration templates
└── services/                # Services page templates
```

---

## Plugin Template Tree

```
lms/plugins/
├── accounts/templates/      # Auth & certification templates
│   ├── auth/                # Authentication views
│   └── certification/       # Certification templates
├── blog/templates/          # Blog templates
├── lms/templates/           # LMS email and learning templates
│   ├── email/               # LMS email templates
│   └── lms/                 # LMS page templates
├── profile/templates/       # Profile templates
└── components/              # Site-specific UI components
    ├── auth/                # Auth components
    ├── profile/             # Profile partials and settings
    └── blocks/              # Content blocks
```

---

## Key Files & Components

### Models
- `plugins/lms/models/courses.py` — Course, Lesson, Enrollment models
- `plugins/lms/models/certifications.py` — Certification models
- `plugins/blog/models.py` — BlogPost, BlogCategory models

### Views & Viewsets
- `plugins/lms/views/courses.py` — Course views (list, detail, enrollment)
- `plugins/lms/views/cart.py` — Shopping cart views
- `plugins/lms/viewsets.py` — CourseViewset, EnrollmentViewset
- `plugins/blog/viewsets.py` — BlogPostViewset
- `plugins/accounts/viewsets.py` — EventViewset

### Templates
- `templates/lms/course_list.html` — Course catalog listing
- `templates/lms/course_detail.html` — Individual course page
- `templates/lms/lesson.html` — Lesson content viewer
- `templates/auth/login.html` — Login page (HTMX modal capable)
- `templates/auth/signup.html` — Registration page

---

## Available Shared Components

All shared components from `projects/assets/templates/components/` are available:
chat, cookies, forms, modals, pagination, tables, search, breadcrumbs.

---

## Layout Variants

Use `{% extends "layout/<variant>/skeleton.html" %}`:

| Variant | Purpose |
|---------|---------|
| `layout/apps/` | App-style layout |
| `layout/landing/` | Marketing/landing layout |
| `layout/learning/` | LMS/learning layout |
| `layout/profile/` | User profile layout |
| `layout/auth/` | Authentication layout (via `base_auth.html`) |

---

## Auth & Accounts

- **Adapter**: `plugins.accounts.adapters.RegistrationAdapter`
- **Views**: `plugins.accounts.views.allauth` (AllauthLoginView, AllauthSignupView)
- **HTMX fragment rendering** for login/signup modals
- **Social auth adapter**: `AuthHTMXSocialAccountAdapter`
- **2FA**: TOTP-based via `two_factor_enabled` / `two_factor_secret` on profile model
- **Templates**: Use `{% comp_include %}` for component tracking
- **Email**: Auth email templates managed as Wagtail snippets via `AuthEmailTemplate`

---

## Development Commands

```bash
cd projects
make dev WEBSITE=lms          # Run dev server
make check WEBSITE=lms        # Django system checks
make test WEBSITE=lms         # Run tests
make migrate WEBSITE=lms      # Run migrations
```

---

## Related Docs

| Resource | Path |
|----------|------|
| Project docs | `docs/projects/lms/` |
| Shared templates | `projects/assets/templates/AGENTS.md` |
| django-fusion | `libs/django-fusion/AGENTS.md` |
| INFRASTRUCTURE.md | `INFRASTRUCTURE.md` |
