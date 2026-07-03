# LMS Demo — Template Path Tree

Path: `applications/lms-demo/`

## Template Resolution Order (Django TEMPLATES_DIRS)

1. `lms-demo/templates/` — site-specific overrides (highest priority)
2. `lms-demo/plugins/<name>/templates/` — plugin templates
3. `lms-demo/plugins/components/` — site component blocks
4. `assets/templates/` — shared cross-site templates (lowest priority)

## Site Template Tree

```
lms-demo/templates/
├── base_page.html          # Extends shared base.html
├── base_profile.html       # Profile-specific base template
├── base_auth.html          # Auth-specific base template
├── index.html              # Home page template
├── home/
│   └── sections/
│       └── clients.html    # Client logos section
├── about/                   # About page templates
├── auth/                    # Authentication templates
├── contact/                 # Contact page templates
├── errors/                  # Custom error pages (404, 500)
├── registration/            # Registration templates
└── services/                # Services page templates
```

## Plugin Template Tree

```
lms-demo/plugins/
├── accounts/templates/      # Auth & certification templates
│   ├── auth/                # Authentication views
│   └── certification/       # Certification templates
├── blog/templates/          # Blog templates
├── lms/templates/           # LMS email and learning templates
│   ├── email/               # LMS email templates
│   └── lms/                 # LMS page templates
├── profile/templates/       # Empty shelf — reserved for profile overrides
└── components/              # Site-specific UI components
    ├── auth/                # Auth components
    └── blocks/              # Content blocks
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
