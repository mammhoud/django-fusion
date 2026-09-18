# Project Design — structa.cloud Landing Platform

## Overview

The precis-landing project is the public-facing website for structa.cloud — a portfolio and product hub showcasing Mahmoud Ezzat Moustafa's open-source libraries, cloud platforms, and desktop applications.

## Design Principles

### 1. Document-First Architecture

Every page is a complete HTML document. No SPA, no client-side routing, no hydration waterfall. The browser receives finished HTML and renders it immediately.

```
Request → Astro SSG → HTML → Browser (paint)
                ↑
        Backend API (build time)
```

### 2. Progressive Enhancement

- **Core**: Static HTML (works without JavaScript)
- **Enhanced**: HTMX fragment swaps (server-rendered HTML patches)
- **Delight**: Alpine.js micro-interactions (accordion, theme, counter)

### 3. Single Source of Truth

All content originates from Wagtail CMS. The Astro frontend fetches data at build time (SSG) and falls back to sensible defaults when the backend is unavailable.

## Component Architecture

```
Layout.astro
├── Header.astro           ← navItems (backend), siteName (backend)
├── <slot />               ← page content
│   ├── Hero.astro         ← pageData.hero
│   ├── Stats.astro        ← pageData.stats
│   ├── Features.astro     ← pageData.features
│   ├── Testimonials.astro ← pageData.testimonials
│   ├── FAQ.astro          ← pageData.faq
│   ├── Pricing.astro      ← pageData.pricing
│   ├── ContactForm.astro  ← contactData (backend)
│   └── CTA.astro          ← pageData.cta
├── Footer.astro           ← siteSettings (backend)
└── Toast.astro            ← Alpine.js store
```

## Data Flow

```
┌─────────────┐     build-time fetch      ┌──────────────────┐
│  Astro SSG   │ ◄────────────────────── │  Django/Wagtail   │
│  (frontend)  │                          │  (backend)        │
│              │     GET /apis/pages/*     │                   │
│  Static HTML │     GET /apis/site/       │  SiteSettings     │
│  + HTMX.js   │     GET /apis/navigation/ │  Page Models      │
│  + Alpine.js │                          │  StreamField      │
└──────┬───────┘                          └───────────────────┘
       │
       ▼
┌─────────────┐
│   Browser   │
│             │
│  Renders    │
│  HTML       │
│  Hydrates   │
│  HTMX +     │
│  Alpine     │
└─────────────┘
```

## Page Types

| Page | Backend Source | Frontend Component |
|------|---------------|-------------------|
| `/` (Home) | `HomePage` → `GET /apis/pages/home/` | `index.astro` |
| `/about/` | `AboutPage` → `GET /apis/pages/about/` | `about.astro` |
| `/products/` | `ProductsPage` → `GET /apis/pages/products/` | `products.astro` |
| `/projects/` | `ProjectsPage` → `GET /apis/pages/projects/` | `projects.astro` |
| `/features/` | `FeaturesPage` → `GET /apis/pages/features/` | `features.astro` |
| `/faq/` | `FAQPage` → `GET /apis/pages/faq/` | `faq.astro` |
| `/contact/` | `ContactPage` → `GET /apis/contact/` | `contact.astro` |
| `/privacy/` | Static content (no Wagtail model) | `privacy.astro` |
| `404` | Static content | `404.astro` |

## CSS Architecture

- **Design tokens**: CSS custom properties (`--fu-*`) in `globals.css`
- **Utility classes**: Tailwind 4 with Fusion theme extension
- **Component classes**: BEM-style (`.card`, `.btn-primary`, `.tag-marker`)
- **Dark mode**: `.dark` class on `<html>`, toggled via Alpine + localStorage
- **Skeleton loading**: `.fusion-skeleton__*` classes for HTMX loading states

## Backend Organization (mirrors precis-lms)

```
backend/
├── apps/
│   ├── content/           # Wagtail content blocks + site settings
│   │   ├── blocks.py       #    StreamField block definitions
│   │   └── models/
│   │       └── settings.py #    SiteSettings (branding, nav, footer)
│   ├── handlers/           # Django-fusion handlers + middleware
│   │   ├── views.py        #    HTMX fragment views
│   │   ├── middleware.py   #    HTMX detection
│   │   └── urls.py         #    Fragment routes
│   └── pages/              # Wagtail page models + API
│       ├── models.py       #    HomePage, AboutPage, ProductsPage, etc.
│       ├── api.py          #    /apis/* endpoints
│       └── management/     #    seed_pages command
├── urls.py                 # Root URL config
└── settings.py             # Django settings
```
