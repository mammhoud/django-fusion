# Brand Assets — Images, Logos & Static Files

> Centralized organization for all brand imagery, product logos, favicons,
> screenshots, and generated art across the Structa Cloud monorepo.

---

## Directory Map

```
projects/assets/static/images/
├── brand/                   # Vector logos + brand identity marks
│   ├── pos-crest.svg        # Formints POS crest logo
│   ├── pos-crest-static.svg # Formints static variant
│   ├── lms-ribbon.svg       # Precis LMS ribbon logo
│   ├── crm-isometric.svg    # CRM isometric mark
│   └── structa-logo.png     # Structa Cloud primary logo
├── generated/               # AI-generated imagery (ChatGPT / DALL-E)
│   ├── chatgpt-preview-2026-08-07.png
│   └── screenshot-2026-07-16.png
├── favicons/                # Site favicons
│   └── favicon.svg          # Primary favicon (shared across sites)
├── backgrounds/             # Page background patterns
│   └── pattern-*.jpg
├── element/                # UI illustration elements (SVG)
│   └── *.svg
└── avatar/                  # Default avatar images
    └── *.jpg
```

## Related Product Media

Product screenshots and screencasts are consolidated under the project that
publishes them:

```
projects/landing-fusion/backend/assets/static/related/formints/
├── standard-checkout.jpg          # Checkout screen
├── standard-operations.jpg        # Data and operations
├── standard-sale-complete.png     # Completed sale receipt
├── standard-screencast.gif        # Full screencast
├── standard-walkthrough.gif       # Animated walkthrough
├── pro-admin-dashboard.jpg        # Admin dashboard
├── pro-admin-products.jpg         # Product administration
├── pro-admin-customers.jpg        # Customer administration
├── pro-admin-sales.jpg            # Sales administration
├── pro-admin-loyalty.jpg          # Loyalty administration
└── pro-admin-settings.jpg         # Settings administration
```

The Astro public mirror is at
`projects/landing-fusion/frontend/public/static/related/formints/`.

## Favicon Locations

| Location | Purpose |
|----------|---------|
| `projects/landing-fusion/assets/static/favicon.svg` | Shared favicon |
| `projects/landing-fusion/frontend/public/favicon.svg` | Astro dev favicon |
| `projects/precis/frontend/public/favicon.svg` | Precis favicon |

All favicons should be kept in sync. Update all three when changing the icon.

## Naming Conventions

### Screenshots

```text
<edition>-<context>-<label>.<ext>
```

### Related media

```text
related/<product-slug>/<edition>-<label>.<ext>
```

Use edition-first descriptive kebab-case names, for example
`related/formints/standard-checkout.jpg`.

### Generated images

```text
generated/<tool>-<description>-<date>.<ext>
```
- `generated/chatgpt-preview-2026-08-07.png`

## Cross-References

| Topic | Link |
|------|------|
| Landing-Fusion | `../../projects/landing-fusion/README.md` |
| Precis LMS | `../../projects/precis/README.md` |
| Formints POS | `../../projects/formints/README.md` |
| Docs sidebar | `../../docs/_sidebar.md` |
