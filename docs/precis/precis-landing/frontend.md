# 🖥️ Precis Landing — Frontend

> Astro 5 + Tailwind CSS 4 + HTMX 2 + Alpine.js frontend for structa.cloud

---

## Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Astro 5 | Static site generation + SSR |
| **Styling** | Tailwind CSS 4 | Utility-first CSS with OKLCH tokens |
| **Interactions** | Alpine.js 3 | Micro-interactions (accordions, toggles, modals) |
| **Dynamic** | HTMX 2 | Server-rendered fragment swaps |
| **Motion** | GSAP 3 | Scroll-triggered animations |
| **Bundler** | Vite 6 | Dev server + production builds |

---

## Page Routes

| Route | Astro File | Source |
|-------|-----------|--------|
| `/` | `pages/index.astro` | Wagtail API |
| `/about/` | `pages/about.astro` | Wagtail API |
| `/about/founder/` | `pages/about/founder.astro` | Static + API |
| `/about/startup/` | `pages/about/startup.astro` | Static + API |
| `/about/team/` | `pages/about/team.astro` | Static + API |
| `/services/` | `pages/services.astro` | Wagtail API |
| `/products/` | `pages/products.astro` | Wagtail API |
| `/products/[slug]/` | `pages/products/[slug].astro` | Wagtail API |
| `/products/[slug]/preview/[edition]/` | `pages/products/[slug]/preview/[edition].astro` | Wagtail API |
| `/pricing/` | `pages/pricing.astro` | Wagtail API |
| `/blog/` | `pages/blog/index.astro` | Wagtail API |
| `/blog/[slug]/` | `pages/blog/[slug].astro` | Wagtail API |
| `/contact/` | `pages/contact.astro` | Wagtail API + HTMX form |
| `/faq/` | `pages/faq.astro` | Wagtail API |
| `/brand/` | `pages/brand.astro` | Wagtail API |
| `/privacy/` | `pages/privacy.astro` | Static |

---

## Key Components

### Layout

- `Layout.astro` — Root wrapper with SEO, theme init, AHA runtime
- `Header.astro` — Navigation with dropdowns, language switcher, auth
- `Footer.astro` — Site links, newsletter, contact

### UI Components

- `Hero.astro` — Page hero with accent word, CTAs, trusted-by
- `Features.astro` — Feature grid cards
- `PricingCard.astro` — Edition pricing cards with comparison tables
- `Breadcrumb.astro` — In-page navigation for subpages
- `BrandModal.astro` — Product brand identity modal
- `LanguageSwitcher.astro` — 7-language switcher with flags
- `ThemeToggle.astro` — Dark/light mode toggle (persisted)

---

## Quick Commands

```bash
cd projects/precis/precis-landing/frontend

# Dev server
npm run dev          # http://localhost:3000

# Type check
npm run check        # astro check

# Build
npm run build        # static output → dist/

# Tests
npm test             # vitest

# Preview build
npm run preview
```

---

## Related

- [`../README.md`](../README.md) — project overview
- [`backend-api.md`](backend-api.md) — backend API docs
- [`deployment.md`](deployment.md) — Docker deployment
