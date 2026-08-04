# Landing-Fusion Build Plan

> **Tags:** #landing #astro #django #wagtail #plan
> **Depends on:** [`../../cms-fusion/plan/ASTRO_MIGRATION_PLAN.md`](../../cms-fusion/plan/ASTRO_MIGRATION_PLAN.md)

Landing-only implementation of the CMS-Fusion → **AHA stack** migration
(Astro + HTMX + Alpine.js frontend, Django + Wagtail backend), isolated in its
own project directory with the same file layout as `cms-fusion` but trimmed to
the landing slice.

## Directory layout (mirrors `projects/cms-fusion`)

```
projects/landing-fusion/
├── frontend/                 # Astro 5 + Tailwind 4 + HTMX + Alpine.js (AHA)
│   ├── src/
│   │   ├── layouts/Layout.astro   # Header, Footer, SEO, theme init, HTMX/Alpine runtime
│   │   ├── pages/                 # index, about, contact, faq, privacy, 404
│   │   ├── components/
│   │   │   ├── ui/                # Button, Card, Accordion, Modal, Toast, ThemeToggle
│   │   │   ├── blocks/            # Hero, Features, Stats, Testimonials, Pricing, FAQ, CTA, ContactForm
│   │   │   └── layout/            # Header, Footer
│   │   ├── lib/site.ts            # Nav, footer links, contact methods, backend URL
│   │   └── styles/globals.css     # Tailwind 4 + Fusion tokens (plan §4) + .dark variant
│   ├── astro.config.mjs
│   └── package.json
├── backend/                  # Django 5.2 + Wagtail 7.4 (landing-only CMS)
│   ├── manage.py / settings.py / urls.py / wsgi.py
│   ├── Makefile
│   └── apps/
│       ├── content/              # StreamField block types + content/blocks/ templates
│       ├── pages/                # page models + pages/ templates + seed_pages + tests
│       │   └── management/commands/seed_pages.py
│       └── handlers/             # django-fusion PageHandler views (HTMX fragment rendering)
├── plan/                    # Plan docs (this dir) + shadcnblocks theme styles
├── Makefile                 # Root dispatcher: frontend + backend targets
└── README.md
```

## Phase status

| Phase | Scope | Status |
|-------|-------|:------:|
| 0 | Scaffold, AHA runtime, Fusion theme, Layout | ✅ |
| 1 | Static pages (home, about, contact, faq, privacy, 404) | ✅ |
| 5.1 | Dark mode — ThemeToggle + localStorage + `.dark` on `<html>` | ✅ |
| — | Django + Wagtail backend, landing page models + templates | ✅ new |
| 2–4 | Content collections/blog, HTMX fragments, auth | ⏳ later |

## Backend ↔ frontend mapping

| Frontend block (`frontend/src/components/blocks/`) | Wagtail field (`backend/apps/pages/models.py`) | Block type (`apps/content/blocks.py`) |
|----------------------------------------------------|---------------------------------------------------|--------------------------|
| Hero | `LandingPage.hero` | `HeroBlock` |
| Stats | `AboutPage.stats` | `StatsSectionBlock` → `StatBlock` |
| Features | `AboutPage.features` | `FeaturesSectionBlock` → `FeatureBlock` |
| Testimonials | `AboutPage.testimonials` | `TestimonialsSectionBlock` → `TestimonialBlock` |
| Pricing | `AboutPage.pricing` | `PricingSectionBlock` → `PricingTierBlock` |
| FAQ | `AboutPage.faq` / `FaqPage.faq` | `FaqSectionBlock` → `FaqItemBlock` |
| CTA | `LandingPage.cta` | `CtaBlock` |
| ContactForm + methods | `ContactPage.contact` | `ContactSectionBlock` → `ContactMethodBlock` |
| Header/Footer nav + theme | hardcoded in `partials/` + `base.html` | — (site.ts equivalent) |

## Backend quick start

```bash
cd projects/landing-fusion/backend
make migrate     # makemigrations + migrate (SQLite)
make seed        # create site + home/about/company/services/products/contact/faq/privacy pages
make dev         # http://localhost:8074  (Wagtail admin at /admin/)
make check       # django system checks
make test        # apps.pages tests
```

## Theme reference

The shadcnblocks `mainline-astro-template` theme styles (oklch tokens, DM Sans,
`.dark` variant, `@theme inline` mapping) were extracted from the cloned repo
and documented in [`SHADCNBLOCKS_THEME.md`](./SHADCNBLOCKS_THEME.md).
