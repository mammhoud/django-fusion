# 📸 Documentation Assets

> Screenshots, product previews, and diagrams used across the Structa Cloud documentation.

## Directory Structure

```
docs/assets/
├── README.md                          # This file
├── screenshots/                        # Product screenshots
│   └── formints/                       # Formint POS screenshots
│       ├── admin-dashboard.jpg         # Unfold admin dashboard
│       ├── admin-products.jpg          # Product management
│       ├── admin-customers.jpg         # Customer list
│       ├── admin-sales.jpg             # Sales overview
│       ├── admin-loyalty.jpg           # Loyalty program
│       ├── admin-settings.jpg          # Admin settings
│       ├── frontend-home.jpg           # POS frontend home screen
│       └── frontend-data.jpg           # POS frontend data view
└── previews/                           # Product preview images
    └── formints/                       # Formint product previews
        ├── standard-front.jpg          # Standard POS front view
        ├── standard-back.jpg           # Standard POS back view
        ├── pro-admin-dashboard.jpg     # Pro admin dashboard
        ├── pro-admin-products.jpg      # Pro product management
        └── standard-walkthrough.gif    # Standard POS walkthrough screencast
```

## Naming Conventions

- **Screenshots:** `{product}-{section}-{description}.{ext}` — e.g., `formint-admin-dashboard.jpg`
- **Previews:** `{edition}-{view}.{ext}` — e.g., `standard-front.jpg`
- **Diagrams:** `{product}-{type}-{description}.{ext}` — e.g., `precis-architecture-overview.png`
- **Screencasts/GIFs:** `{product}-{description}.gif` — e.g., `standard-walkthrough.gif`

## Source Locations

| Asset Type | Source Directory | Notes |
|---|---|---|
| Formint admin screenshots | `projects/formints/docs/screenshots/admin/` | Original captures |
| Formint frontend screenshots | `projects/formints/docs/screenshots/frontend/` | Original captures |
| Formint product previews | `projects/landing-fusion/backend/assets/static/previews/formints/` | Used on landing site |
| Landing-Fusion related images | `projects/landing-fusion/backend/assets/static/related/formints/` | Product feature images |

## Adding New Assets

1. Place the file in the appropriate `docs/assets/{category}/{product}/` directory
2. Use a descriptive, kebab-case filename
3. Reference with a relative path from the docs root: `assets/screenshots/formints/admin-dashboard.jpg`
4. For large files (>1MB), consider compressing with `optipng` or `jpegoptim`
5. Update this README to include the new asset in the inventory

## Related

- [Previews naming convention](https://github.com/mammhoud/structa.cloud/blob/generic/docs/README.md)
- [Landing-Fusion preview assets](../../projects/landing-fusion/backend/assets/static/previews/)
