# Landing-Fusion

> **Status:** 🟢 Phase 0 + 1 complete; dark mode done; backend added
> **Tags:** #landing #astro #django #wagtail #aha-stack
> **Stack:** Astro 5 + Tailwind CSS 4 + HTMX + Alpine.js (frontend) · Django 5.2 + Wagtail 7.4 (backend)

Landing-only implementation of the [Landing-Fusion plan](../../docs/plans/precis-landing/README.md),
with an historical reference to the superseded CMS-Fusion migration (archived).
It uses an **AHA stack** (Astro + HTMX + Alpine.js) with a **Django + Wagtail backend**
whose editable fields drive the landing pages. The project is the canonical
landing slice after the CMS-Fusion migration.

## Why this project exists

The upstream plan targets the heavy Next.js SPA as a replacement for the landing
+ marketing + CMS pages. This repository is the **landing slice** — an isolated,
dependency-light project proving out the migration while a paired Wagtail backend
makes every landing section editable.

| Factor | Next.js (Current) | Astro + AHA (This repo) |
|--------|:-----------------:|:------------------------:|
| Client JS shipped | Large React bundle (~80KB+) | Minimal (~30KB HTMX + Alpine) |
| `fusion_render_first` | Requires FusionProxy/decoder | Native server-rendered HTML |
| Dynamic interactions | React state + RTK Query | HTMX fragments + Alpine.js |
| Content editing | Custom React components | Wagtail CMS StreamFields |

## Repository layout

```
projects/precis/precis-landing/
├── frontend/            # Astro 5 + Tailwind 4 + HTMX + Alpine.js
│   ├── src/
│   │   ├── layouts/Layout.astro    # Header, Footer, SEO, theme init, AHA runtime, skeleton loading
│   │   ├── pages/                  # index, about, company, services, products, contact, faq, privacy, 404
│   │   ├── components/
│   │   │   ├── ui/                 # Button, Card, Accordion, Modal, Toast, ThemeToggle, Skeleton, PricingCard
│   │   │   ├── blocks/             # Hero, Features, Stats, Testimonials, Pricing, FAQ, CTA, ContactForm
│   │   │   └── layout/             # Header, Footer
│   │   ├── lib/site.ts             # Nav, footer links, contact methods, backend URL
│   │   └── styles/globals.css      # Tailwind 4 + Fusion tokens + .dark variant + skeleton shimmer
│   ├── astro.config.mjs
│   ├── tests/section-placement.test.mjs
│   └── package.json
├── backend/             # Django 5.2 + Wagtail 7.4 — landing-only CMS (precis-lms-style apps)
│   ├── manage.py / settings.py / urls.py / wsgi.py / Makefile
│   └── apps/
│       ├── content/                # StreamField block types + content/blocks/ templates
│       ├── pages/                  # page models + pages/ templates + seed_pages + tests + migrations
│       └── handlers/               # django-fusion PageHandler views (HTMX fragment rendering)
├── plan/                # Deprecated local plan path; canonical plans live in ../../docs/plans/precis-landing/
├── Makefile             # Root dispatcher (frontend + backend targets)
└── README.md
```

## Quick start

### Frontend (Astro)

```bash
cd projects/precis/precis-landing
npm install          # or: make install
npm run dev          # http://localhost:3000
npm run check        # astro check (types + diagnostics)
npm run build        # static output → frontend/dist/
npm run preview      # preview the build
```

### Backend (Django + Wagtail)

```bash
cd projects/precis/precis-landing/backend
make migrate         # makemigrations + migrate (SQLite)
make seed            # create site + home/about/company/services/products/contact/faq/privacy pages
make dev             # http://localhost:8074 — Wagtail admin at /admin/
make check           # django system checks
make test            # apps.pages tests
```

> Uses the workspace venv via `uv --project ../..` (Wagtail 7.4 + Django 5.2).

## What's implemented

### Frontend (Astro + AHA)
- **Phase 0** ✅ — Astro 5 scaffold, Fusion theme tokens → Tailwind 4, bundled HTMX 2 + Alpine 3, root Layout with SEO/OG, toast store, HTMX error handling
- **Phase 1** ✅ — home (hero/stats/features/testimonials/pricing/FAQ/CTA), about, contact (HTMX form), FAQ (search + accordion), privacy, 404
- **Page expansion** ✅ — separate Company / Services / Products pages; current home content moved to About; pricing folded into Features; all sections appended to page ends
- **§5.1 dark mode** ✅ — `ThemeToggle` persists to localStorage, swaps `.dark` on `<html>`, FOUC-free init script, cross-tab sync
- **Skeleton loading** ✅ — `Skeleton` component + shimmer CSS; global HTMX in-flight indicator; Alpine hydrate fallback (`is-hydrating`)

### Backend (Django + Wagtail)
- Landing-only Wagtail page models with editable StreamFields for every section (hero, stats, features, testimonials, pricing, FAQ, CTA, contact) — organized precis-lms-style into `apps/content`, `apps/pages`, `apps/handlers`
- **django-fusion views** — every landing route is served by a `PageHandler` subclass (unified fragment/layout render pipeline); HTMX requests get `pages/fragments/page.html`, plain requests get the full document
- Render-mechanism documented in `apps/handlers/views.py` (backend → HTML → HTMX/Alpine)
- Skeleton loading on the backend too (`pages/partials/skeleton.html` + `#htmx-indicator`)
- Templates mirroring the Astro frontend (same Fusion tokens, `.dark` variant, HTMX/Alpine)
- `seed_pages` management command — creates the site + full 8-page tree (idempotent)
- Self-contained `settings.py` (standalone, no shared-config dependency)

### Plan docs
- [`../../docs/plans/precis-landing/README.md`](../../docs/plans/precis-landing/README.md) — canonical Landing Fusion plan entry point

## Not yet ported (later phases)

- Dynamic content (blog, courses, events, shop) → HTMX fragments
- Auth + dashboards → HTMX forms + Alpine
- Full E2E tests (Playwright) and final Docker/Traefik production rollout gates

## See also

- [docs/CATALOG_AND_FUSION.md](docs/CATALOG_AND_FUSION.md) — product & edition comparison, the django-fusion dependency surface, and Django Fusion guide references
- [`../../docs/plans/precis-landing/README.md`](../../docs/plans/precis-landing/README.md) — this project's canonical plan
- [shadcnblocks/mainline-astro-template](https://github.com/shadcnblocks/mainline-astro-template) — theme reference
