# Landing-Fusion

> **Status:** 🟡 In Progress — Phase 0 (foundation) + Phase 1 (static pages) complete
> **Tags:** #landing #astro #migration #aha-stack #frontend
> **Stack:** Astro 5 + Tailwind CSS 4 + HTMX + Alpine.js (AHA)

Standalone landing/marketing site implementing the first two phases of the
[ASTRO_MIGRATION_PLAN](../cms-fusion/plan/ASTRO_MIGRATION_PLAN.md) — migrating
the CMS-Fusion Next.js frontend to an **AHA stack** (Astro + HTMX + Alpine.js),
without touching the existing `cms-fusion` project.

## Why this project exists

The migration plan targets the heavy Next.js SPA (`cms-fusion/frontend/`) as a
replacement for the landing + marketing + CMS pages. This repository is the
**landing slice**: it proves out Phase 0 (scaffold, Fusion theme, AHA runtime)
and Phase 1 (static pages: home, about, contact, FAQ, privacy) as an isolated,
dependency-free project first.

| Factor | Next.js (Current) | Astro + AHA (This repo) |
|--------|:-----------------:|:------------------------:|
| Client JS shipped | Large React bundle (~80KB+) | Minimal (~30KB HTMX + Alpine) |
| `fusion_render_first` | Requires FusionProxy/decoder | Native server-rendered HTML |
| Dynamic interactions | React state + RTK Query | HTMX fragments + Alpine.js |
| Styling | Tailwind 3 + SCSS | Tailwind 4 + Fusion tokens |

## Quick start

```bash
cd projects/landing-fusion
npm install
npm run dev        # http://localhost:3000
npm run build      # static output → dist/
npm run preview    # preview the build
npm run check      # astro check (types + diagnostics)
```

> Node 20+ required. The repo uses nvm — `~/.nvm/versions/node/v22.18.0`.

## Directory structure

```
projects/landing-fusion/
├── src/
│   ├── layouts/
│   │   └── Layout.astro          # Root layout — Header, Footer, SEO, HTMX/Alpine runtime
│   ├── pages/
│   │   ├── index.astro           # Homepage (Phase 1.1)
│   │   ├── about.astro           # About page (Phase 1.2)
│   │   ├── contact.astro         # Contact page + form (Phase 1.3)
│   │   ├── faq.astro             # FAQ with search + accordion (Phase 1.4)
│   │   ├── privacy.astro         # Privacy policy (Phase 1.5)
│   │   └── 404.astro             # Branded 404 (Plan §13.5)
│   ├── components/
│   │   ├── ui/                   # Button, Card, Accordion, Modal, Toast (Alpine-powered)
│   │   ├── blocks/               # Hero, Features, Stats, Testimonials, Pricing, FAQ, CTA, ContactForm
│   │   └── layout/               # Header (Alpine mobile menu), Footer
│   ├── lib/
│   │   └── site.ts               # Nav, footer links, contact methods, backend URL
│   └── styles/
│       └── globals.css           # Tailwind 4 + Fusion theme tokens (Plan §4)
├── astro.config.mjs
├── tsconfig.json
└── package.json
```

## What's implemented (migration status)

### Phase 0 — Foundation ✅
- [x] Astro 5 scaffold with TypeScript + Tailwind 4 (`@tailwindcss/vite`)
- [x] Fusion theme CSS variables → Tailwind 4 CSS-first config (Plan §4 colors)
- [x] AHA runtime bundled: HTMX 2 + Alpine.js 3 + collapse/intersect plugins
- [x] Root `Layout.astro` with SEO meta, OG tags, Header, Footer
- [x] Alpine.js global toast store + HTMX error handling (Plan §13.5)
- [x] `astro:page-load` analytics hook (Plan §13.7)

### Phase 1 — Static pages ✅
- [x] Homepage — Hero, Stats, Features, Testimonials, Pricing, FAQ, CTA
- [x] About — hero, stat cards, mission + values
- [x] Contact — Alpine-validated form with HTMX POST to Django backend
- [x] FAQ — Alpine search + accordion
- [x] Privacy — static content
- [x] Consistent Header/Footer/SEO across all pages

### Not yet ported (later phases)
- Dynamic content (blog, courses, events, shop) → HTMX fragments
- Auth + dashboards → HTMX forms + Alpine
- Dark mode toggle, E2E tests (Playwright), Docker/Traefik wiring

## Backend integration

`src/lib/site.ts` exposes `fusionApiUrl` (default `http://localhost:5075`,
override with `PUBLIC_FUSION_API_URL`). The contact form POSTs to
`/api/htmx/contact/` with `HX-Request: true` and falls back to an inline
toast when the backend is unreachable — so the landing site works standalone.

## See also

- [ASTRO_MIGRATION_PLAN.md](../cms-fusion/plan/ASTRO_MIGRATION_PLAN.md) — source plan
- [CASE_STUDY_SITE_APPLICATION_DUAL_MODE.md](../cms-fusion/plan/CASE_STUDY_SITE_APPLICATION_DUAL_MODE.md) — dual-mode rendering
- [shadcnblocks/mainline-astro-template](https://github.com/shadcnblocks/mainline-astro-template) — theme reference
