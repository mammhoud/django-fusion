# Shared Templates — Organization Guide

Scope: `applications/assets/templates/` — the shared template layer for Structa Cloud websites.

## Directory Structure

```
templates/
├── base.html                  # Root base template (all sites)
├── base_email.html            # Base email template
├── base_profile.html          # Base profile template
├── index.html                 # Default index
├── robots.txt                 # Robots.txt template
│
├── about/                     # About page sections
├── account/                   # Allauth account overrides
├── auth/                      # Authentication templates & partials
├── blocks/                    # Wagtail StreamField blocks
│   ├── contact/               # Contact form blocks
│   ├── content/               # Content blocks
│   ├── media/                 # Media blocks (images, video)
│   ├── pages/                 # Page-type blocks
│   └── partials/              # Block partials
├── blog/                      # Blog system templates
│   ├── components/            # Blog UI components
│   ├── fragments/             # HTMX fragments
│   ├── profile/               # Author profile templates
│   └── tags/                  # Tag templates
├── components/                # Reusable cross-cutting components
│   ├── chat/                  # Chat UI components
│   ├── form/                  # Form components
│   └── modal/                 # Modal components
├── contact/                   # Contact page sections
├── courses/                   # Course/learning templates
│   ├── details/               # Course detail views
│   ├── partials/              # Course partials
│   └── sections/              # Course page sections
├── email/                     # Email text templates (unique, non-plugin)
├── events/                    # Event page templates
│   └── includes/              # Event includes
├── generic/                   # Generic reusable templates
├── home/                      # Home page sections
├── layout/                    # Page layout/chrome templates
│   ├── apps/                  # App-style layout variant
│   ├── auth/                  # Auth pages layout
│   ├── forms/                 # Form layouts
│   ├── headers/               # Shared header includes
│   ├── landing/               # Landing page layout
│   ├── learning/              # Learning platform layout
│   ├── navigation/            # Navigation components
│   └── profile/               # Profile page layout
├── learning/                  # Learning-related templates
├── lms/                       # LMS-specific templates
│   ├── blocks/                # LMS Wagtail blocks
│   └── partials/              # LMS partials
├── partials/                  # Shared partials
│   └── header/                # Header partials
├── plugins/                   # CANONICAL reusable plugin templates
│   ├── base/                  # Plugin base templates
│   ├── certifications/        # Certification templates
│   ├── chat/                  # Chat plugin templates
│   ├── courses/               # Course plugin templates
│   ├── emails/                # Email templates (canonical)
│   ├── errors/                # Error page templates (canonical)
│   ├── forms/                 # Form templates
│   ├── headers/               # Header templates
│   ├── mfa/                   # MFA/2FA templates (canonical)
│   ├── modals/                # Modal templates
│   ├── newsletter/            # Newsletter templates (canonical)
│   ├── notifications/         # Notification templates
│   ├── pagination/            # Pagination components (canonical)
│   ├── privacy/               # Privacy policy templates (canonical)
│   ├── search/                # Search templates
│   └── tables/                # Table templates
├── products/                  # Product page sections
├── registration/              # Registration templates
│   └── fragments/             # Registration HTMX fragments
├── services/                  # Services page templates
│   ├── includes/              # Service includes
│   └── sections/              # Service page sections
├── socialaccount/             # Social auth templates
│   └── snippets/              # Social auth snippets
├── team/                      # Team page sections
├── ui/                        # UI utility templates
├── usersessions/              # User session templates
├── wagtailadmin/              # Wagtail admin overrides
│   ├── pages/                 # Page editing
│   ├── panels/                # Admin panels
│   ├── shared/                # Shared admin
│   ├── snippets/              # Snippet admin
│   └── userbar/               # User bar
└── wagtailcore/               # Wagtail core template overrides
```

## Template Resolution Order

Django resolves templates in this order (configured in `configs/base/templates.py`):

1. **Site root templates** — `applications/<site>/templates/`
2. **Site page templates** — `applications/<site>/pages/templates/`
3. **Site www templates** — `applications/<site>/www/pages/templates/`
4. **Site asset templates** — `applications/<site>/assets/templates/`
5. **Site layout templates** — `applications/<site>/assets/templates/layout/`
6. **Workspace shared plugins** — `applications/_shared/plugins/`
7. **Site plugin templates** — `applications/<site>/plugins/`
8. **Site plugin component templates** — `applications/<site>/plugins/components/`
9. **Workspace asset templates** — `applications/assets/templates/` ← THIS DIRECTORY
10. **Workspace layout templates** — `applications/assets/templates/layout/`
11. **Django app templates** — discovered via `APP_DIRS: True`

## Plugins/ Directory — Canonical Source

The `plugins/` subdirectory is the canonical location for shared reusable templates. When a template exists in both `plugins/<name>/` and the top-level `<name>/`, the `plugins/` version is authoritative for edits.

**Backwards-compatible mirrors**: `emails/` and `components/pagination/` directories also exist as mirrors of their `plugins/` counterparts. This ensures that 117+ existing `render_to_string("emails/...")` and `{% include "components/pagination/..." %}` references continue to work. When editing these templates, modify the `plugins/` version and then copy changes to the mirror.

Previously duplicated directories (`errors/`, `newsletter/`, `privacy/`, `mfa/`) were consolidated — only the `plugins/` versions remain. No code references use the old paths for these directories.

## Rules for Template Changes

### Adding Templates
- **Cross-site reusable** → place in `plugins/` or appropriate functional directory
- **Site-specific** → place in the site's own templates directory
- **Layout variant** → add to the appropriate `layout/<variant>/` subdirectory

### Modifying Templates
- Preserve existing Django/Wagtail context variables, filters, and block tags
- Use `fragment_name` for HTMX fragment identifiers
- Use BEM-style CSS classes: `card`, `card__title`, `card--featured`
- Keep styling hooks as classes, not IDs
- Maintain `{% include %}` contracts — don't change include variable names

### Template Inheritance
- `base.html` → all page templates extend this
- `base_email.html` → all email templates extend this
- `base_profile.html` → profile page templates extend this
- Layout variants extend their shell: `layout/<variant>/skeleton.html`

### HTMX Fragments
- Fragments must include the `.fragment--<name>` wrapper for swap targets
- Use `hx-target` consistently with the fragment wrapper class
- Include `HX-Request` headers where views check for HTMX

## Website Template Maps

| Website | Module | Port | Site ID | Template Root |
|---|---|---|---|---|
| ctc-research | LMS | 5070 | 1 | `applications/ctc-research/` |
| lms-demo | LMS | 5071 | 2 | `applications/lms-demo/` |
| VResume | CMS | 5072 | 3 | `applications/VResume/` |

## See Also
- `docs/templates.md` — Template usage best practices
- `docs/websites.md` — Website configuration guide
- `docs/packages.md` — Package documentation
- `docs/environments.md` — Environment configuration
