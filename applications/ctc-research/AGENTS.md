# CTC Research — Template Path Tree

Path: `applications/ctc-research/`

## Template Resolution Order (Django TEMPLATES_DIRS)

1. `ctc-research/templates/` — site-specific overrides (highest priority)
2. `ctc-research/plugins/<name>/templates/` — plugin templates
3. `ctc-research/plugins/components/` — site component blocks
4. `assets/templates/` — shared cross-site templates (lowest priority)

## Site Template Tree

```
ctc-research/templates/
├── base_page.html          # Extends shared base.html
├── index.html              # Home page template
├── home/
│   └── sections/
│       └── clients.html    # Client logos section
├── about/                   # About page templates
├── certification/           # Certification templates
├── contact/                 # Contact page templates
├── registration/            # Registration/signup templates
└── services/                # Services page templates
```

## Plugin Template Tree

```
ctc-research/plugins/
├── accounts/templates/      # Auth templates (extends base_auth.html)
│   ├── account/             # allauth overrides: login, signup, password_reset, etc.
│   ├── email/               # Email confirmation templates
│   ├── learning/            # Learning platform templates
│   ├── lms/                 # LMS blocks and fragments
│   ├── profile/             # User profile: forms, modals, partials, sections, settings
│   └── socialaccount/       # Social auth (Google, GitHub, etc.)
├── blog/templates/          # Blog templates
├── lms/templates/           # LMS-specific templates
├── profile/templates/       # Profile templates
└── components/              # Site-specific UI components
    ├── blocks/              # Content blocks
    ├── common/              # Shared partials and modals
    └── contact/             # Contact form components
```

## Available Shared Components

See `assets/templates/components/AGENTS.md` for the full inventory:
chat, cookies, forms, modals, pagination.

## Layout Variants

Use `{% extends "layout/<variant>/skeleton.html" %}`:
- `layout/apps/` — app-style layout
- `layout/landing/` — marketing/landing layout
- `layout/learning/` — LMS/learning layout
- `layout/profile/` — user profile layout
- `layout/auth/` — authentication layout (via `base_auth.html`)
