# 📁 Shared Templates (`projects/assets/templates/`)

## What's Here

Cross-site Django templates shared across all Structa Cloud sites.

```
templates/
├── base.html                      # 🔴 Root layout — extends by all sites
├── components/
│   ├── blocks/                    # 🟢 Content blocks
│   │   └── contact/               #    Contact form/profile components
│   ├── partials/                  # 🟢 UI fragments
│   └── cookies/                   # 🔵 Cookie consent components
│       ├── cookie-consent.html
│       ├── cookie-policy.html
│       └── privacy-policy.html
├── content/
│   └── media/
│       └── gallery.html           # 🟢 Media gallery component
├── about/
│   └── sections/
│       └── about.html             # 🟢 About section
└── ui/
    ├── base_auth.html             # 🔵 Auth layout wrapper
    └── base_page.html             # 🔵 Standalone page base
```

## Customization Tags

| Template | Tag | How to customize |
|----------|-----|-----------------|
| `base.html` | 🔴 `not-customizable` | Override in site `templates/` instead |
| `components/blocks/` | 🟢 `customizable` | Add new component blocks |
| `components/partials/` | 🟢 `customizable` | Add new UI fragments |
| `components/cookies/` | 🔵 `template` | Edit cookie text, not structure |
| `ui/base_auth.html` | 🔵 `template` | Override skeleton in site |
| `ui/base_page.html` | 🔵 `template` | Override in site templates |

## How to Override

Copy the template to your site's `templates/` directory with the same relative path:

```
projects/ctc-research/templates/base.html  ← overrides projects/assets/templates/base.html
```

## Reference

- [Template Architecture →](../../docs/projects/templates/architecture.md)
- [Python/Django Docs →](../../docs/python/README.md)
