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
├── element/                 # UI illustration elements (SVG)
│   └── *.svg
└── avatar/                  # Default avatar images
    └── *.jpg
```

## Product Previews

Product screenshots and screencasts live under each project:

```
projects/landing-fusion/backend/assets/static/previews/formints/
├── standard-front.jpg         # Checkout screen
├── standard-back.jpg          # Data & operations
├── standard-walkthrough.gif   # Animated walkthrough
├── standard-sale-complete.png # Completed sale receipt
├── pro-admin-dashboard.jpg    # Admin dashboard
└── pro-admin-products.jpg     # Product administration

projects/formints/docs/screenshots/
├── admin/                     # Admin panel screenshots
│   ├── 03_admin_dashboard.jpg
│   ├── 04_admin_products.jpg
│   ├── 05_admin_customers.jpg
│   ├── 06_admin_sales.jpg
│   ├── 07_admin_loyalty.jpg
│   └── 08_admin_settings.jpg
└── frontend/                  # POS frontend screenshots
    ├── 01_frontend_home.jpg
    └── 02_frontend_data.jpg
```

## Favicon Locations

| Location | Purpose |
|----------|---------|
| `projects/landing-fusion/assets/static/favicon.svg` | Shared favicon |
| `projects/landing-fusion/frontend/public/favicon.svg` | Astro dev favicon |
| `projects/precis/frontend/public/favicon.svg` | Precis favicon |

All favicons should be kept in sync. Update all three when changing the icon.

## Naming Conventions

### Screenshots
```
<product>-<context>-<label>.<ext>
```
- `formint-pos-checkout.jpg`
- `precis-lms-course-detail.png`

### Previews
```
previews/<product-slug>/<edition>-<label>.<ext>
```
- `previews/formints/standard-front.jpg`

### Generated Images
```
generated/<tool>-<description>-<date>.<ext>
```
- `generated/chatgpt-preview-2026-08-07.png`

---

## Cross-References

| Topic | Link |
|-------|------|
| Landing-Fusion | `../../projects/landing-fusion/README.md` |
| Precis LMS | `../../projects/precis/README.md` |
| Formints POS | `../../projects/formints/README.md` |
| Docs sidebar | `../../docs/_sidebar.md` |
