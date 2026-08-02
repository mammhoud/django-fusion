# Fusion CMS — Migration & Integration Plan
> **Tags:** #cms-fusion #fusion #frontend

## Status: ✅ Complete

The CMS Fusion core integration is complete. Remaining cleanup work (assets, templates, legacy directories) is tracked in [`docs/plans/README.md`](../README.md).

The CMS Fusion project is a complete, full-featured content management system built on django-fusion + django-bolt + Wagtail with a Next.js frontend. It absorbs all features from the legacy fusion-cms project (now backed up at `projects/cms/fusion-cms.bak`).

---

## Architecture

```
cms-fusion/
├── backend/                    # Django + Wagtail backend
│   ├── www/api/bolt_apis.py   # Bolt API — all endpoints
│   ├── www/api/pages.py       # Page API (Wagtail-first, static fallback)
│   ├── plugins/               # All fusion-cms plugins merged
│   │   ├── accounts/          # Auth, registration, profiles
│   │   ├── blog/              # Blog posts, categories, tags, RSS
│   │   ├── lms/               # Courses, enrollments, lessons
│   │   ├── products/          # Product listings, cart
│   │   ├── profile/           # User profiles, settings
│   │   ├── pages/             # FusionPage Wagtail models + STATIC_PAGES
│   │   └── branding/          # Dynamic Wagtail branding model (FUSION-specific)
│   ├── templates/             # All Django templates from fusion-cms
│   └── assets/                # All static assets, SCSS, JS, fixtures
├── frontend/                  # Next.js 14 frontend
│   └── src/
│       ├── app/               # Pages: [slug], blog, courses, products
│       ├── components/        # FusionProxy, FusionWagtailPage, Header, Footer, etc.
│       └── lib/               # api-client, fusion-store, fusion-decoder, site-content
├── assets/                    # Shared front-end design assets
│   └── styles/fusion-theme.scss
└── plan/
    └── MIGRATION_PLAN.md      # This file
```

---

## Feature Matrix

| Feature | Backend | Bolt API | Next.js | Status |
|---------|:-------:|:--------:|:-------:|:------:|
| **Pages** (about, team, services, contact) | Wagtail + STATIC_PAGES | `/api/pages/<slug>` | `[slug]/page.tsx` via FusionProxy | ✅ |
| **Home Page** | Wagtail FusionHomePage | `/api/pages/home` | `page.tsx` via FusionProxy | ✅ |
| **Blog Listing** | BlogPost model | `/api/blog` | `/blog/page.tsx` | ✅ |
| **Blog Detail** | BlogPost model | `/api/blog/<slug>` | `/blog/[slug]/page.tsx` | ✅ |
| **Blog Categories** | BlogCategory model | `/api/blog/categories` | Used in sidebar | ✅ |
| **Blog Tags** | BlogTag model | `/api/blog/tags` | Used in sidebar | ✅ |
| **Course Catalog** | Course model | `/api/courses` | `/courses/page.tsx` | ✅ |
| **Course Detail** | Course model | `/api/courses/<slug>` | `/courses/[slug]/page.tsx` | ✅ |
| **Course Filters** | Course model | `/api/courses/filters` | Sidebar filters | ✅ |
| **Products** | Product model + STATIC_PAGES | `/api/products` | `/products/page.tsx` | ✅ |
| **Branding** | Branding Wagtail model | `/api/fusion/branding` | Header, Footer | ✅ |
| **Auth Status** | django-allauth | `/api/auth/status` | (via allauth views) | ✅ |
| **Health** | FusionSessionChecker | `/api/health`, `/api/fusion/health` | FusionProxy init | ✅ |
| **Fusion Layouts** | django-fusion layout system | Via fragment pointer | FusionLayout component | ✅ |
| **Fusion Render-First** | Session preference | Via fragment pointer | FusionProxy fallback chain | ✅ |
| **Wagtail Admin** | Full Wagtail admin | N/A | N/A | ✅ |
| **Fusion CMS Config** | settings.py FUSION_FEATURES | N/A | N/A | ✅ |

---

## Bolt API Endpoints Reference

### Health & Status
- `GET /api/health` — Health check
- `GET /api/fusion/health` — Fusion rendering preference
- `GET /api/auth/status` — Current auth state

### Branding
- `GET /api/fusion/branding` — Dynamic site branding (colors, names)

### Pages
- `GET /api/pages` — List all published pages (navigation)
- `GET /api/pages/<slug>` — Page content (Wagtail-first, STATIC_PAGES fallback)
- `GET /api/pages/<slug>/fragment` — Fragment pointer for fusion rendering

### Blog
- `GET /api/blog` — List posts (pagination, search, category/tag filter)
- `GET /api/blog/<slug>` — Post detail + related posts
- `GET /api/blog/categories` — Categories with post counts
- `GET /api/blog/tags` — Tags with post counts

### Courses
- `GET /api/courses` — Course catalog (search, filters, pagination)
- `GET /api/courses/<slug>` — Course detail + modules, instructor, reviews
- `GET /api/courses/filters` — Available filter options

### Products
- `GET /api/products` — Product listing (model-backed or STATIC_PAGES fallback)

---

## Next.js Frontend Routes

| Route | Component | Data Source |
|-------|-----------|------------|
| `/` | `page.tsx` → FusionProxy | `/api/pages/home` |
| `/about` | `[slug]/page.tsx` → FusionProxy | `/api/pages/about` |
| `/team` | `[slug]/page.tsx` → FusionProxy | `/api/pages/team` |
| `/services` | `[slug]/page.tsx` → FusionProxy | `/api/pages/services` |
| `/contact` | `[slug]/page.tsx` → FusionProxy | `/api/pages/contact` |
| `/privacy` | `[slug]/page.tsx` → FusionProxy | `/api/pages/privacy` |
| `/faq` | `[slug]/page.tsx` → FusionProxy | `/api/pages/faq` |
| `/blog` | `blog/page.tsx` — custom grid | `/api/blog` |
| `/blog/[slug]` | `blog/[slug]/page.tsx` — post detail | `/api/blog/<slug>` |
| `/courses` | `courses/page.tsx` — catalog + filters | `/api/courses` |
| `/courses/[slug]` | `courses/[slug]/page.tsx` — detail | `/api/courses/<slug>` |
| `/products` | `products/page.tsx` — product grid | `/api/products` |

---

## Key Design Decisions

1. **Wagtail-first, STATIC_PAGES fallback**: The page API checks Wagtail FusionPage models first. If no Wagtail page exists, it falls back to `STATIC_PAGES` dict in `plugins/pages/content.py`. This allows both CMS-managed and code-defined pages.

2. **FusionProxy fallback chain**: Fragment pointer → Wagtail page data → Server-rendered HTML → Error. This ensures pages render in the optimal mode based on `fusion_render_first` preference.

3. **Isolated per-project design**: cms-fusion is a self-contained project with its own settings, URLs, bolt APIs, and frontend. It shares the django-fusion and django-bolt libraries but maintains its own feature set.

4. **Branding via Wagtail**: The `branding` plugin uses a Wagtail model for site name, colors, company info. This is editable via the Wagtail admin and exposed via the bolt API.

5. **FUSION_FEATURES toggle**: Individual features (blog, courses, products) can be toggled on/off via settings. Endpoints gracefully handle missing models.

---

## Related Plans

- [LMS Fusion Migration Plan](../lms-fusion/migration-plan.md)
- [Django Fusion Bolt Integration](../../../libs/django-fusion/src/django_fusion/plugins/bolt/)
- [POS Full Enhancement Plan](../pos/forge-pos-enhancement.md)

---

*Last updated: July 26, 2026 — Full CMS feature integration complete.*
