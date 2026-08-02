# CMS-Fusion → Astro Migration Plan

> **Status:** 📋 Plan — Proposed  
> **Tags:** #cms-fusion #astro #migration #aha-stack  
> **Target Framework:** Astro 5 + Tailwind CSS 4 + HTMX + Alpine.js  

---

## 1. Executive Summary

Migrate the `cms-fusion/frontend/` (Next.js 14 + React 18 + Redux) to an **AHA stack** (Astro + HTMX + Alpine.js) using the **[shadcnblocks/mainline-astro-template](https://github.com/shadcnblocks/mainline-astro-template)** as the base theme. This leverages the existing `fusion_render_first` backend architecture while eliminating the complexity of a heavy SPA framework.

### Why Astro + AHA?

| Factor | Next.js (Current) | Astro + AHA (Target) | Benefit |
|--------|:-----------------:|:--------------------:|---------|
| Client JS shipped | Large React bundle (~80KB+) | Minimal (~30KB HTMX + Alpine) | Faster loads |
| SSR complexity | Node.js server, ISR | Static-first, SSR adapters optional | Simpler deploy |
| `fusion_render_first` | Requires FusionProxy/decoder | Native — Astro *is* server-rendered HTML | Zero overhead |
| Dynamic interactions | React state + RTK Query | HTMX server fragments + Alpine.js | No API JSON layer needed |
| Styling | Tailwind 3 + SCSS + CSS vars | Tailwind 4 + shadcn/ui + CSS vars | Unified design system |
| Content pages | Custom React components | MDX + Astro Content Collections | Simpler authoring |
| Dashboards | Complex React + Recharts | HTMX fragments + Alpine.js state | Much less code |

---

## 2. Architecture Comparison

### Current (Next.js)

```
Browser
  └── Next.js (React SPA with partial SSR)
       ├── React Router → page components
       ├── Redux Store → RTK Query → /api/ endpoints
       ├── FusionDecoder → decode codec payloads
       ├── FusionProxy → fetch & inject server HTML
       └── FusionLayout → layout variants
```

The current architecture is a **hybrid** that uses React's client-side rendering for most content but can optionally fall back to server-rendered HTML fragments via `FusionProxy`. This is complex — the `fusion_render_first` session check, decoder, wrapper components, and Redux store all add significant overhead.

### Target (Astro + AHA)

```
Browser
  └── Astro (SSR/static HTML + HTMX + Alpine)
       ├── Astro file-based routing → .astro pages
       ├── HTMX hx-get/hx-post → Django fragments (existing)
       ├── Alpine.js x-data/x-show → local interactivity
       ├── Astro View Transitions → SPA-like navigation
       └── shadcn/ui components → design system
```

With Astro, `fusion_render_first` becomes **the default rendering mode** rather than a fallback. The Django backend renders HTML, HTMX handles dynamic updates, and Alpine.js adds client-side sparkle. No Redux, no decoder, no FusionProxy needed for most pages.

---

## 3. Phased Migration Plan

### Phase 0: Foundation (`week 1`)

| # | Task | Details | Dependencies |
|---|------|---------|-------------|
| 0.1 | Scaffold Astro project | `npm create astro@latest` in `projects/cms-fusion/astro/` with TypeScript, Tailwind 4, React | None |
| 0.2 | Add shadcnblocks theme | Clone/merge `mainline-astro-template` blocks, Tailwind 4 config, typography | 0.1 |
| 0.3 | Install AHA stack | Add HTMX (via CDN or npm), Alpine.js, astro-themes for dark/light | 0.1 |
| 0.4 | Setup View Transitions | Add `<ClientRouter />` to layout, set up `transition:name` on persistent elements | 0.1 |
| 0.5 | Port Fusion theme CSS | Migrate `fusion-theme.scss` variables → `tailwind.config` (Tailwind 4 uses CSS-first config) | 0.1 |
| 0.6 | Configure Dev/Prod adapters | `@astrojs/node` for dev, `@astrojs/vercel` or `@astrojs/netlify` for prod | 0.1 |
| 0.7 | Setup `src/pages/` layout | Root `Layout.astro` with Header, Footer, View Transitions, HTMX/Alpine scripts | 0.1–0.4 |

**Deliverable:** Blank Astro site running at `localhost:3000` with shadcn/ui components, HTMX, Alpine.js, and the Fusion theme.

---

### Phase 1: Static Pages (Landing, About, Contact, FAQ, Privacy) (`week 2`)

| # | Task | Details | Dependencies |
|---|------|---------|-------------|
| 1.1 | Homepage (`index.astro`) | Hero section, stats, featured content — use shadcnblock hero + feature blocks | 0.7 |
| 1.2 | About page (`about.astro`) | Static content with `fusion_render_first` fragment or direct HTML | 0.7 |
| 1.3 | Contact page (`contact.astro`) | Form with HTMX `hx-post` to Django backend | 0.7 |
| 1.4 | FAQ page (`faq.astro`) | Alpine.js `x-data` accordion, shadcnblock FAQ pattern | 0.7 |
| 1.5 | Privacy page (`privacy.astro`) | Simple markdown/MDX content | 0.7 |
| 1.6 | Layout consistency | Ensure Header, Footer, SEO metadata, OG images are consistent | 0.7 |

**Key Decision:** For static pages, the Astro frontend can either:
- **(A)** Directly embed server-rendered Wagtail content via API (calling Django during SSR)
- **(B)** Use HTMX fragments from the existing Django `fusion_render_first` endpoints
- **(C)** Write content directly in Astro/MDX and bypass the CMS for non-dynamic pages

**Recommendation:** Use **(B)** for most pages to preserve CMS integration, **(C)** for truly static pages (privacy, terms).

**Deliverable:** All public-facing static pages ported with matching or improved UI.

---

### Phase 2: Dynamic Content Pages (Blog, Courses, Events, Shop) (`week 3`)

| # | Task | Details | Dependencies |
|---|------|---------|-------------|
| 2.1 | Blog index (`blog.astro`) | HTMX `hx-get` for paginated post list, Alpine.js search filter | 0.7 |
| 2.2 | Blog detail (`blog/[slug].astro`) | Server-rendered from Django via HTMX fragment or API call | 2.1 |
| 2.3 | Courses index (`courses.astro`) | HTMX grid/list toggle, category filters, pagination | 0.7 |
| 2.4 | Course detail (`courses/[slug].astro`) | Deep server-rendered page, HTMX enrollment button | 2.3 |
| 2.5 | Events page (`events.astro`) | HTMX calendar grid with Alpine.js month picker | 0.7 |
| 2.6 | Shop page (`shop.astro`) | HTMX product grid, Alpine.js cart state | 0.7 |
| 2.7 | Shop detail (`shop/[id].astro`) | Server-rendered product page | 2.6 |
| 2.8 | Products page (`products.astro`) | HTMX product listing | 0.7 |

**Key Insight:** In the AHA stack, most "data fetching" becomes HTMX `hx-get` requests that return HTML fragments from the Django backend. No JSON API, no Redux, no loading states — HTMX swaps fragments directly.

**Pattern:**
```astro
---
// Astro component script (server-side)
// For initial render, fetch from Django:
const pageHtml = await fetch(`http://backend:5075/pages/blog/`);
---
<!-- Fallback: inject server HTML directly -->
<Fragment set:html={pageHtml} />

<!-- HTMX version for dynamic updates -->
<div hx-get="/api/pages/blog/fragment/" hx-trigger="load" hx-swap="innerHTML">
  Loading blog posts...
</div>
```

**Deliverable:** All dynamic content pages ported with HTMX-driven fragments.

---

### Phase 3: Auth & User Pages (Login, Registration, Dashboard) (`week 4`)

| # | Task | Details | Dependencies |
|---|------|---------|-------------|
| 3.1 | Login (`login.astro`) | HTMX form with Alpine.js validation, Django allauth integration | 0.7 |
| 3.2 | Registration (`register.astro`) | HTMX multi-step form with Alpine.js state | 3.1 |
| 3.3 | Student Dashboard (`dashboard/student.astro`) | HTMX metric panels, Alpine.js tab navigation | 2.0 |
| 3.4 | Instructor Dashboard (`dashboard/instructor.astro`) | HTMX data panels, Alpine.js chart toggle | 2.0 |
| 3.5 | Admin Dashboard (`dashboard/admin.astro`) | HTMX CRUD tables with Alpine.js modals | 2.0 |
| 3.6 | Profile/Settings (`profile.astro`) | HTMX form fragments, Alpine.js edit-in-place | 3.1 |
| 3.7 | Notifications (`notifications.astro`) | HTMX real-time notification list, Alpine.js badge counter | 3.0 |

**Auth Flow:**
- Login/register forms use HTMX `hx-post` → Django allauth endpoints
- Alpine.js `x-data` manages client-side form state and validation hints
- Session tokens stored in cookies (Django standard), not localStorage
- HTMX `HX-Redirect` handles post-auth navigation
- Existing `django-allauth` + `django-fusion` auth adapters work unchanged

**Deliverable:** Auth flows and dashboards fully functional.

---

### Phase 4: Interactive Features (Cart, Checkout, Payments, Lessons) (`week 5`)

| # | Task | Details | Dependencies |
|---|------|---------|-------------|
| 4.1 | Cart (`cart.astro`) | Alpine.js `x-data` for cart state, HTMX for server sync | 2.6 |
| 4.2 | Checkout (`checkout.astro`) | Multi-step HTMX form, Stripe Elements via Alpine.js | 4.1 |
| 4.3 | Lesson player (`lesson.astro`) | Alpine.js video player state, HTMX progress tracking | 2.4 |
| 4.4 | Quiz components | Alpine.js quiz state machine, HTMX submission | 4.3 |
| 4.5 | Assignments | HTMX document upload + Alpine.js drag-drop UI | 4.3 |
| 4.6 | Withdrawals | HTMX form + Alpine.js amount calculator | 3.0 |

**Stripe Integration with AHA:**
- Stripe Elements included via Alpine.js component
- HTMX submits form data to Django, which creates Stripe payment intent
- Alpine.js handles real-time card validation
- This replaces the React `<StripePaymentForm>` component

**Deliverable:** All e-commerce and learning features ported.

---

### Phase 5: Polish & Migration Completion (`week 6`)

| # | Task | Details | Dependencies |
|---|------|---------|-------------|
| 5.1 | Dark mode | Test astro-themes compatibility with Fusion colors | 0.5 |
| 5.2 | Responsive audit | Mobile/tablet/desktop breakpoints using shadcnblock patterns | All |
| 5.3 | SEO audit | Astro `<Head>` metadata, OG images, sitemap generation | All |
| 5.4 | Performance audit | Lighthouse scores, bundle size, HTMX caching | All |
| 5.5 | E2E tests (Playwright) | Port key E2E tests — homepage-content, auth-flows, course-enrollment | All |
| 5.6 | Remove Next.js | Delete `frontend/` or archive as `frontend-legacy/` | All |
| 5.7 | Docker updates | Update Dockerfile.frontend, docker-compose, Traefik config | All |
| 5.8 | CI updates | Update `fusion-ci.yml` — replace Next.js build with Astro build | All |

**Deliverable:** Full production-ready Astro frontend replacing Next.js.

---

## 4. shadcnblocks Theme Customization

### Colors (Fusion → shadcnblocks)

The current Fusion theme CSS variables map to shadcnblocks HSL variables:

| Token | Fusion Var (Current) | shadcnblocks Var (Target) | Usage |
|-------|---------------------|---------------------------|-------|
| Primary | `--fu-primary: #7c3aed` | `--primary: 262 83% 58%` | Buttons, links, accent |
| Primary Dark | `--fu-secondary: #5b21b6` | `--primary-foreground: 0 0% 100%` | Text on primary |
| Accent | `--fu-accent: #4c1d95` | `--accent: 262 70% 35%` | Hover states |
| Background | `--fu-bg: #fafafa` | `--background: 0 0% 98%` | Page bg |
| Text | `--fu-text: #18181b` | `--foreground: 240 6% 10%` | Body text |
| Muted | — | `--muted: 240 5% 96%` | Card bg |
| Border | — | `--border: 240 6% 90%` | Dividers |

### Component Mapping

| shadcnblock Component | Fusion Use Case | Notes |
|-----------------------|-----------------|-------|
| `HeroSection` | Homepage hero | Replace custom hero |
| `FeaturesSection` | Stats row, testimonials | Reuse grid layout |
| `LogoShowcase` | Partner/instructor logos | New component |
| `TestimonialsCarousel` | Course reviews | Replace custom carousel |
| `PricingTable` | Course pricing plans | New use case |
| `FAQAccordion` | FAQ page | Already matches |
| `ContactForm` | Contact page | Already matches |
| `NavigationBar` | Header nav | Replace custom header |
| `Footer` | Site footer | Replace custom footer |

---

## 5. Component Porting Guide

### Component Replacement Table

| Current Next.js Component | Astro Replacement Strategy |
|--------------------------|---------------------------|
| `FusionLayout.tsx` | **Delete** — Layout native to Astro via `Layout.astro` |
| `FusionProxy.tsx` | **Delete** — HTMX `hx-get` handles fragment injection natively |
| `FusionPage.tsx` | **Delete** — Astro pages call API directly in frontmatter |
| `FusionWagtailPage.tsx` | **Simplify** → `fetchWagtailPage()` in Astro frontmatter |
| `FusionMiddleware.tsx` | **Delete** — No Redux context needed |
| `FusionDecoder.ts` | **Keep** (simplified) — decode codec payloads in Astro endpoints |
| `api-client.ts` | **Rewrite** → Astro API endpoints or server-side fetch |
| `fusion-types.ts` | **Keep** — type definitions remain useful |
| `fusion-store.ts` | **Delete** — no Redux store needed |
| `site-content.ts` | **Rewrite** → Astro content collections for static content |
| `Header.tsx` | **Rewrite** → `Header.astro` with Alpine.js mobile menu |
| `Footer.tsx` | **Rewrite** → `Footer.astro` — simpler, no JS needed |
| `Providers.tsx` | **Delete** — no React context providers |
| `AuthGuard.tsx` | **Simplify** → Astro middleware or HTMX guard |
| `DashboardRedirect.tsx` | **Simplify** → Astro middleware or server-side check |
| `ErrorBoundary.tsx` | **Delete** — Astro handles errors at page level |
| `LanguageSwitcher.tsx` | **Rewrite** → Alpine.js language selector |
| `PageNavigation.tsx` | **Rewrite** → Astro partial with HTMX fragment |
| `FusionAssets.tsx` | **Delete** — Assets managed by Astro build |
| `LoadingSkeleton.tsx` | **Delete** — HTMX `hx-indicator` handles loading states |
| `EmptyState.tsx` | **Keep** (as `.astro`) — reusable UI pattern |
| `ErrorState.tsx` | **Keep** (as `.astro`) — reusable error UI |
| `Carousel.tsx` | **Replace** — shadcnblock carousel or HTMX slide |
| `Accordion.tsx` | **Replace** — Alpine.js `x-data` accordion |
| `Modal.tsx` | **Replace** — Alpine.js `x-show` modal |
| `Toast.tsx` | **Replace** — Alpine.js notification system |
| `Tabs.tsx` | **Replace** — Alpine.js `x-data` tabs |
| `Form.tsx` | **Replace** — HTML form with HTMX submission |
| `ScrollReveal.tsx` | **Replace** — CSS `@keyframes` or IntersectionObserver |
| `RevenueChart.tsx` | **Replace** — Server-rendered SVG chart or HTMX-driven |
| `StripePaymentForm.tsx` | **Rewrite** — Alpine.js + Stripe Elements |
| `RTK Query endpoints` | **Delete all** — replaced by HTMX `hx-get`/`hx-post` |

### File Structure (Proposed)

```
projects/cms-fusion/astro/
├── src/
│   ├── layouts/
│   │   ├── Layout.astro          # Root layout — Header, Footer, SEO, scripts
│   │   ├── DashboardLayout.astro # Sidebar + content area
│   │   └── BlankLayout.astro     # Minimal layout for auth pages
│   ├── pages/
│   │   ├── index.astro           # Homepage
│   │   ├── about.astro
│   │   ├── contact.astro
│   │   ├── faq.astro
│   │   ├── privacy.astro
│   │   ├── blog/
│   │   │   ├── index.astro
│   │   │   └── [slug].astro
│   │   ├── courses/
│   │   │   ├── index.astro
│   │   │   └── [slug].astro
│   │   ├── events.astro
│   │   ├── shop/
│   │   │   ├── index.astro
│   │   │   └── [id].astro
│   │   ├── products.astro
│   │   ├── login.astro
│   │   ├── registration.astro
│   │   ├── cart.astro
│   │   ├── checkout.astro
│   │   ├── lesson.astro
│   │   ├── dashboard/
│   │   │   ├── index.astro       # Student dashboard
│   │   │   ├── instructor.astro
│   │   │   ├── admin.astro
│   │   │   ├── profile.astro
│   │   │   └── notifications.astro
│   │   └── [slug].astro          # Catch-all for CMS pages
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.astro
│   │   │   ├── Card.astro
│   │   │   ├── Modal.astro       # Alpine.js powered
│   │   │   ├── Accordion.astro   # Alpine.js powered
│   │   │   ├── Tabs.astro        # Alpine.js powered
│   │   │   ├── Toast.astro       # Alpine.js powered
│   │   │   ├── EmptyState.astro
│   │   │   └── LoadingSkeleton.astro
│   │   ├── blocks/
│   │   │   ├── Hero.astro        # shadcnblock hero
│   │   │   ├── Features.astro    # shadcnblock features
│   │   │   ├── Testimonials.astro # shadcnblock carousel
│   │   │   ├── Pricing.astro     # shadcnblock pricing
│   │   │   ├── FAQ.astro         # shadcnblock FAQ
│   │   │   ├── CTA.astro         # shadcnblock CTA
│   │   │   └── Stats.astro       # Custom stat grid
│   │   ├── layout/
│   │   │   ├── Header.astro      # Alpine.js mobile menu
│   │   │   ├── Footer.astro
│   │   │   ├── Sidebar.astro     # Dashboard sidebar
│   │   │   └── Breadcrumb.astro
│   │   ├── auth/
│   │   │   ├── LoginForm.astro   # HTMX form
│   │   │   └── RegisterForm.astro # HTMX multi-step
│   │   ├── blog/
│   │   │   ├── BlogCard.astro
│   │   │   └── BlogList.astro    # HTMX paginated
│   │   ├── courses/
│   │   │   ├── CourseCard.astro
│   │   │   └── CourseGrid.astro  # HTMX grid
│   │   ├── shop/
│   │   │   ├── ProductCard.astro
│   │   │   └── Cart.astro        # Alpine.js cart state
│   │   └── dashboard/
│   │       ├── KpiCard.astro
│   │       ├── Chart.astro       # SVG/server-rendered chart
│   │       └── DataTable.astro   # HTMX table
│   ├── lib/
│   │   ├── fusion.ts             # Fusion API helpers
│   │   ├── fusion-decoder.ts     # Keep from Next.js
│   │   ├── fusion-types.ts       # Keep from Next.js
│   │   └── site.ts              # Site config
│   └── styles/
│       ├── globals.css           # Tailwind 4 directives + custom
│       └── fusion-theme.css      # Fusion CSS variables
├── public/
│   ├── fonts/
│   └── favicon.ico
├── astro.config.mjs
├── tailwind.config.ts            # Tailwind 4 CSS-first config
├── tsconfig.json
└── package.json
```

---

## 6. `fusion_render_first` Pattern with AHA Stack

### How `fusion_render_first` Works Natively in Astro

With Astro, `fusion_render_first` becomes **the natural rendering path** rather than a special case.

**Before (Next.js):**
```tsx
// FusionProxy fetches HTML from Django
// FusionPage decodes JSON from API
// Complex session preference system

<FusionPage slug="home">
  {(page, fallback) => <HomeContent page={page} />}
</FusionPage>
```

**After (Astro):**
```astro
---
// 🎯 Astro frontmatter — runs on server at build/request time
const BACKEND = Astro.env.BACKEND_URL || 'http://backend:5075';
const response = await fetch(`${BACKEND}/api/pages/home/data/?fusion_render_first=true`);
const html = await response.text();
---
<!-- Inject server-rendered HTML directly — zero client JS for this section -->
<Fragment set:html={html} />

<!-- HTMX takes over for dynamic interactions -->
<div hx-get="/api/pages/home/fragment/" hx-trigger="load" hx-swap="outerHTML">
  <!-- Alpine.js loading state -->
  <div x-data="{ loaded: false }" x-init="setTimeout(() => loaded = true, 300)">
    <div x-show="!loaded" class="animate-pulse ...">Loading...</div>
  </div>
</div>
```

### HTMX + Alpine.js Interaction Patterns

**Pattern 1: Server-rendered page with HTMX updates**
```astro
<!-- Course list page — initial HTML rendered by Astro, updates via HTMX -->
<div
  x-data="{ view: 'grid', category: 'all' }"
  class="course-listing"
>
  <!-- Category filter buttons (Alpine.js + HTMX) -->
  <div class="filters">
    <button
      @click="category = 'all'"
      :class="{ active: category === 'all' }"
      class="filter-btn"
    >All</button>
    <button
      @click="category = 'web'"
      :class="{ active: category === 'web' }"
      hx-get="/api/courses/filter/?cat=web"
      hx-target="#course-grid"
      hx-swap="innerHTML"
      class="filter-btn"
    >Web Development</button>
  </div>

  <!-- HTMX target for dynamic content -->
  <div id="course-grid" class="grid grid-cols-3 gap-6">
    {coursesList.map(course => <CourseCard course={course} />)}
  </div>
</div>
```

**Pattern 2: Alpine.js state + HTMX form submission**
```astro
<!-- Checkout form with Alpine.js validation + HTMX submission -->
<div
  x-data="{
    email: '',
    cardNumber: '',
    errors: {},
    validate() {
      this.errors = {};
      if (!this.email.includes('@')) this.errors.email = 'Invalid email';
      return Object.keys(this.errors).length === 0;
    }
  }"
>
  <form
    hx-post="/api/checkout/"
    hx-target="#checkout-result"
    hx-swap="innerHTML"
    @submit.prevent="if (validate()) $el.dispatchEvent(new Event('submit', { bubbles: true }))"
  >
    <input
      type="email"
      x-model="email"
      name="email"
      placeholder="Email"
      class="input"
    />
    <template x-if="errors.email">
      <p class="text-red-500 text-sm" x-text="errors.email"></p>
    </template>

    <button type="submit" class="btn-primary">Place Order</button>
  </form>
  <div id="checkout-result"></div>
</div>
```

**Pattern 3: Alpine.js local interactivity**
```astro
<!-- FAQ accordion — entirely client-side with Alpine.js -->
<div x-data="{ openItem: null }" class="space-y-2">
  {faqItems.map(item => (
    <div class="border rounded-lg">
      <button
        @click="openItem = openItem === ${item.id} ? null : ${item.id}"
        class="w-full text-left p-4 font-semibold"
      >
        {item.question}
      </button>
      <div x-show="openItem === ${item.id}" x-collapse class="p-4 pt-0">
        <p>{item.answer}</p>
      </div>
    </div>
  ))}
</div>
```

---

## 7. Configuration Files

### `package.json`
```json
{
  "name": "cms-fusion-astro",
  "type": "module",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "astro": "astro",
    "check": "astro check",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  },
  "dependencies": {
    "@astrojs/check": "^0.9.0",
    "@astrojs/mdx": "^4.0.0",
    "@astrojs/node": "^9.0.0",
    "@astrojs/tailwind": "^6.0.0",
    "astro": "^5.0.0",
    "astro-themes": "^1.0.0",
    "htmx.org": "^2.0.0",
    "alpinejs": "^3.14.0",
    "@alpinejs/collapse": "^3.14.0",
    "@alpinejs/intersect": "^3.14.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.6.0",
    "lucide-react": "^0.460.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.49.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.7.0",
    "prettier": "^3.4.0",
    "prettier-plugin-astro": "^0.14.0"
  }
}
```

### `astro.config.mjs`
```js
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';
import themes from 'astro-themes';

export default defineConfig({
  output: 'server', // SSR mode for dynamic Fusion CMS pages
  adapter: node({ mode: 'standalone' }),
  integrations: [
    tailwind(),
    mdx(),
    themes({
      defaultTheme: 'light',
      themes: ['light', 'dark'],
    }),
  ],
  vite: {
    ssr: {
      noExternal: ['htmx.org', 'alpinejs'],
    },
  },
  server: { port: 3000 },
});
```

### `tailwind.config.ts` (Tailwind 4)
```css
@import "tailwindcss";

/* Fusion theme CSS variables */
:root {
  --fu-primary: 262 83% 58%;
  --fu-primary-foreground: 0 0% 100%;
  --fu-secondary: 262 70% 35%;
  --fu-accent: 262 83% 48%;
  --fu-bg: 0 0% 98%;
  --fu-text: 240 6% 10%;
  --fu-muted: 240 5% 96%;
  --fu-border: 240 6% 90%;
}

@theme {
  --color-fu-primary: hsl(var(--fu-primary));
  --color-fu-primary-foreground: hsl(var(--fu-primary-foreground));
  --color-fu-secondary: hsl(var(--fu-secondary));
  --color-fu-accent: hsl(var(--fu-accent));
  --color-fu-bg: hsl(var(--fu-bg));
  --color-fu-text: hsl(var(--fu-text));
  --color-fu-muted: hsl(var(--fu-muted));
  --color-fu-border: hsl(var(--fu-border));
}
```

---

## 8. Backend Integration Points

The Django backend mostly **stays unchanged**. The migration only affects the frontend.

| Backend Component | Change Required? | Notes |
|------------------|:----------------:|-------|
| Django REST API endpoints | ✅ Keep — HTMX may hit different URLs | Astro can fetch from existing `/api/` endpoints or Django can return HTML fragments |
| `fusion_render_first` logic | ❌ No change | Now **default mode** — Astro expects HTML |
| Wagtail pages | ❌ No change | Content still managed in Wagtail |
| Django allauth | ❌ No change | HTMX forms post to existing auth URLs |
| Fusion/Fragment endpoints | ❌ No change | HTMX `hx-get` hits `/api/pages/<slug>/fragment/` |
| Stripe integration | ❌ No change | Alpine.js calls existing Stripe endpoints |
| Media serving (Nginx) | ❌ No change | `media.structa.cloud` still serves files |
| Docker/Traefik config | ✅ Update | Port 3000 → Astro, update health checks |

### HTMX Fragment Endpoints (✅ Built — Phase 0.5 Complete)

The following Django endpoints have been built and are ready for the Astro frontend:

| Endpoint | View | Template | Purpose |
|----------|------|----------|---------|
| `GET /api/htmx/courses/grid/` | `htmx_views.course_grid` | `htmx/course_grid.html` | Filtered course grid with pagination |
| `GET /api/htmx/courses/filters/` | `htmx_views.course_filters` | `htmx/course_filters.html` | Course filter sidebar (difficulty) |
| `GET /api/htmx/blog/posts/` | `htmx_views.blog_post_list` | `htmx/blog_post_list.html` | Paginated blog post list with search/filter |
| `GET /api/htmx/dashboard/kpis/` | `htmx_views.dashboard_kpis` | `htmx/dashboard_kpis.html` | Dashboard KPI metric cards |
| `GET /api/htmx/cms/head-content/` | `htmx_views.cms_head_content` | (inline HTML) | CMS-injected `<head>` assets (FusionAssets replacement) |
| `POST /api/htmx/checkout/` | `htmx_views.checkout_fragment` | `htmx/checkout_result.html` | Checkout processing (stub) |

**Source files:**
- `backend/apps/core/htmx/components.py` — FragmentComponent subclasses (extends `django_fusion.routes.FragmentComponent`)
- `backend/apps/core/htmx/application.py` — `HTMXApplication` (extends `django_fusion.routes.Application`)
- `backend/apps/core/api/urls.py` — URL routing via `include(htmx_application.urls)`
- `backend/templates/htmx/` — All fragment templates

**Architecture:** Endpoints use django-fusion's `FragmentComponent` base class (NOT raw function views), wired through an `Application` instance — matching the existing django-fusion patterns for HTMX fragment services.

**Usage in Astro:**
```astro
<!-- Full course grid with HTMX lazy-load -->
<div hx-get="/api/htmx/courses/grid/" hx-trigger="load" hx-swap="innerHTML">
  <div class="animate-pulse">Loading courses...</div>
</div>
```

---

## 9. Trade-offs & Risk Analysis

### Trade-offs

| Decision | Pros | Cons |
|----------|------|------|
| Full AHA stack (no React) | ~80KB less JS, simpler mental model, no React build step | Losing React ecosystem (Recharts, etc.) |
| HTMX for data fetching | No API layer needed for most pages | Less granular loading states than RTK Query |
| Alpine.js for client state | Lightweight, declarative, no build step | Limited for complex state machines (use HTMX for those) |
| shadcnblocks theme | Production-ready components, dark mode, accessible | Lock-in to shadcnblock patterns |
| MDX for content pages | Simpler than Wagtail API for static pages | Content may drift from CMS |

### Migration Risks

| Risk | Likelihood | Mitigation |
|------|:----------:|------------|
| Complex dashboards hard to port | Medium | Keep React islands via `client:load` for chart-heavy pages |
| E2E test flakiness | Medium | Port Playwright tests gradually, component by component |
| HTMX learning curve | Low | Existing Django backend already uses HTMX fragments |
| Alpine.js state management complexity | Low | Use HTMX for server state, Alpine only for UI interactions |
| Build/CI changes | Low | Update Dockerfile, CI config — straightforward |

### When to Keep React Islands

For **data-heavy dashboard pages** with complex charts (RevenueChart, EnrollmentTrendChart), consider keeping React as an **island**:

```astro
---
// Astro page — server-rendered layout
import RevenueChart from '../components/dashboard/RevenueChart';
---

<!-- Standard Astro component — no JS -->
<aside class="sidebar">...</aside>

<!-- React island — only hydrated when visible -->
<RevenueChart client:visible />
```

This gives us the best of both worlds: lightweight AHA for most pages, React for complex visualizations.

---

## 10. Timeline Summary

| Phase | Duration | Pages | Key Tech | Lines of Code |
|-------|:--------:|:-----:|----------|:-------------:|
| **Phase 0:** Foundation | 1 week | Layout, config | Astro 5 + shadcnblocks | ~500 |
| **Phase 1:** Static pages | 1 week | Home, About, Contact, FAQ, Privacy | Astro + HTMX fragments | ~2,000 |
| **Phase 2:** Dynamic content | 1 week | Blog, Courses, Events, Shop | HTMX + Alpine.js | ~3,000 |
| **Phase 3:** Auth & Dashboards | 1 week | Login, Register, Dashboard | HTMX forms + Alpine.js | ~4,000 |
| **Phase 4:** Interactive features | 1 week | Cart, Checkout, Lessons, Quiz | Alpine.js + Stripe HTMX | ~3,000 |
| **Phase 5:** Polish & deploy | 1 week | SEO, tests, Docker, CI | Playwright + Docker | ~1,000 |
| **Total** | **6 weeks** | **~30 pages** | **AHA stack** | **~13,500** |

---

## 11. Getting Started

```bash
# 1. Create Astro project in cms-fusion
cd projects/cms-fusion
npm create astro@latest astro/ -- --template basics --typescript --tailwind
cd astro

# 2. Add shadcnblocks theme components
git clone https://github.com/shadcnblocks/mainline-astro-template /tmp/shadcnblocks
cp -r /tmp/shadcnblocks/src/components/ui/ src/components/ui/
cp -r /tmp/shadcnblocks/src/components/blocks/ src/components/blocks/
cp -r /tmp/shadcnblocks/src/layouts/Layout.astro src/layouts/

# 3. Install AHA dependencies
npm install htmx.org alpinejs @alpinejs/collapse @alpinejs/intersect

# 4. Setup HTMX + Alpine in Layout.astro
# (Add script tags for htmx.org and alpinejs)

# 5. Port fusion theme
cp ../frontend/src/styles/theme/fusion-theme.scss src/styles/fusion-theme.css
# Convert SCSS variables to Tailwind 4 CSS config

# 6. Port first page
# Create src/pages/index.astro with shadcnblock hero + HTMX fragments

# 7. Start dev server
npm run dev
```

### Quick Reference: New AHA Component Pattern

```astro
---
// ── 1. SERVER-SIDE (Astro frontmatter) ────────────────────────────
// This runs at build/request time. Fetch data, process, then render.
import { fetchPageHtml } from '../lib/fusion';

const BACKEND = Astro.env.BACKEND_URL || 'http://localhost:5075';
const html = await fetchPageHtml('home');
const courses = await fetch(`${BACKEND}/api/courses/`).then(r => r.json());
---

<!-- ── 2. HTML TEMPLATE (Rendered on server) ────────────────────── -->
<Layout title="Home — Fusion CMS">
  <!-- Server-rendered content (SEO-friendly) -->
  <Fragment set:html={html} />

  <!-- HTMX-powered interactive section -->
  <section x-data="{ activeTab: 'popular' }">
    <nav class="tabs">
      <button :class="{ active: activeTab === 'popular' }"
              @click="activeTab = 'popular'"
              hx-get="/api/courses/popular/" hx-target="#course-list">
        Popular
      </button>
      <button :class="{ active: activeTab === 'newest' }"
              @click="activeTab = 'newest'"
              hx-get="/api/courses/newest/" hx-target="#course-list">
        Newest
      </button>
    </nav>
    <div id="course-list">
      {courses.map(course => <CourseCard course={course} />)}
    </div>
  </section>

  <!-- Alpine.js local UI (no server round-trip) -->
  <section x-data="{ open: false }">
    <button @click="open = !open">Toggle Details</button>
    <div x-show="open" x-transition>
      <p>Extra details shown with Alpine.js</p>
    </div>
  </section>
</Layout>
```

---

## 12. Appendix: File Reference

### Files to Keep (with modifications)

| File | Path | Modification |
|------|------|-------------|
| `fusion-types.ts` | `astro/src/lib/fusion-types.ts` | ✅ Keep — add HTMX response types |
| `fusion-decoder.ts` | `astro/src/lib/fusion-decoder.ts` | ✅ Keep — still useful for codec decoding |
| `globals.css` | `astro/src/styles/globals.css` | 🔄 Convert Tailwind 3 → 4 syntax |

### Files to Delete (not needed in Astro)

| File | Reason |
|------|--------|
| `frontend/next.config.js` | Next.js framework specific |
| `frontend/postcss.config.js` | Tailwind 4 handles this |
| `frontend/tailwind.config.js` | Tailwind 4 uses CSS-first config |
| All `frontend/src/store/api/` | RTK Query replaced by HTMX |
| All `frontend/src/components/FusionProxy.tsx` | HTMX handles fragment fetching |
| All `frontend/src/components/FusionPage.tsx` | Astro pages replace this |
| All `frontend/src/components/FusionLayout.tsx` | Astro layouts replace this |
| All `frontend/src/components/Providers.tsx` | No React context needed |
| All `frontend/src/store/` | Redux store replaced by HTMX + Alpine |

### Files to Add

| File | Purpose |
|------|---------|
| `astro/src/layouts/Layout.astro` | Root layout template |
| `astro/src/layouts/DashboardLayout.astro` | Dashboard layout with sidebar |
| `astro/src/components/ui/Accordion.astro` | Alpine.js accordion |
| `astro/src/components/ui/Modal.astro` | Alpine.js modal |
| `astro/src/components/ui/Toast.astro` | Alpine.js toast notifications |
| `astro/src/components/blocks/Hero.astro` | shadcnblock hero |
| `astro/src/components/blocks/Features.astro` | shadcnblock features |
| `astro/src/components/blocks/Testimonials.astro` | shadcnblock testimonials |
| `astro/src/components/blocks/Pricing.astro` | shadcnblock pricing |
| `astro/src/components/blocks/CTA.astro` | shadcnblock CTA |
| `astro/src/components/layout/Header.astro` | Site header |
| `astro/src/components/layout/Footer.astro` | Site footer |
| `astro/src/components/layout/Sidebar.astro` | Dashboard sidebar |
| `astro/src/lib/fusion.ts` | Fusion API helpers |
| `astro/src/styles/globals.css` | Tailwind 4 + Fusion theme |
| `astro/astro.config.mjs` | Astro configuration |
| `astro/Dockerfile` | Astro production Dockerfile |

---

## 13. Critical Gaps (from Code Review)

The following gaps were identified during peer review and must be addressed before starting Phase 0:

### 13.1 Django Backend Role Transition

**Question:** Does Astro fully take over HTML serving, or does Django still serve the initial page load?

**Decision needed:** Currently `base.html` in Django handles the initial HTML render. Two options:

- **Option A (Recommended):** Django becomes pure **API/fragment provider**. Astro serves ALL HTML via SSR (`output: 'server'`). Django only responds to HTMX `hx-get`/`hx-post` with HTML fragments. This is cleaner but requires Astro SSR adapter to be production-ready.

- **Option B (Hybrid):** Django serves initial HTML for some pages (existing `base.html`), Astro handles client-side navigation for others. Fragments flow both ways. More complex but gradual transition.

**This decision affects Phase 5.6 (Docker/CI/Traefik) and must be made before Phases 0.6–0.7.**

### 13.2 New Django HTMX Fragment Endpoints

The plan assumes `/htmx/courses/filter/`, `/htmx/blog/posts/`, `/htmx/checkout/`, and `/htmx/dashboard/kpis/` endpoints exist. **They don't.**

**Action required:** Add a **Phase 0.5: Build HTMX Fragment Endpoints** — create lightweight Django views that return HTML snippets for each feature area. These can be simple:

```python
# backend/apps/api/htmx_views.py
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def course_grid(request):
    courses = Course.objects.filter(**request.GET.dict())
    return render(request, "htmx/course_grid.html", {"courses": courses})
```

### 13.3 FusionAssets.tsx — Dynamic CMS Assets

`FusionAssets.tsx` currently loads **dynamic CSS/JS from the CMS** (custom CSS, widget scripts, Wagtail-extracted head content). Simply deleting it without a replacement will break CMS-injected assets.

**Fix:** Replace with Astro's `<Fragment set:html={cmsHeadHtml} />` pattern. The Astro `Layout.astro` should fetch CMS head content during SSR:

```astro
---
// Layout.astro — fetch CMS-injected assets
const cmsHeadHtml = await fetch(`${BACKEND}/api/pages/head-content/`).then(r => r.text());
---
<html>
  <head>
    <Fragment set:html={cmsHeadHtml} />
  </head>
</html>
```

Alternatively, use a client-side HTMX swap to load CMS assets into `<head>` on page load.

### 13.4 Astro Middleware for Auth Guarding

`AuthGuard.tsx` deletion is listed but replacement is vague. **Astro supports `src/middleware.ts`** — create one that checks Django session cookies and redirects unauthenticated users:

```typescript
// src/middleware.ts
import { defineMiddleware } from 'astro/middleware';

export const onRequest = defineMiddleware(async (context, next) => {
  const protectedPaths = ['/dashboard/', '/checkout/', '/profile/'];
  const isProtected = protectedPaths.some(path => context.url.pathname.startsWith(path));

  if (isProtected) {
    const sessionCookie = context.cookies.get('sessionid');
    if (!sessionCookie) {
      return context.redirect('/login');
    }
  }
  return next();
});
```

### 13.5 Error Handling Strategy

Astro has no React-style `ErrorBoundary`. Replace with:

1. **Global 500 errors:** Astro `src/pages/Error.astro` — covers all unhandled errors
2. **HTMX errors:** Listen for `htmx:responseError` event globally and show Alpine.js toast
3. **Per-page errors:** Astro frontmatter try/catch with fallback rendering
4. **Not found:** `src/pages/404.astro` with Fusion-branded 404 page

### 13.6 Testing Strategy for HTMX Interactions

HTMX-based interactions need **the actual Django backend running** during E2E tests (unlike the old MSW/mocking approach). The existing `cms-fusion-e2e` CI job already spins up Django + Playwright together — reuse this pattern.

Key changes from current test approach:
- **Replace** unit tests with React Testing Library + MSW → **HTML fragment verification** (server returns correct HTML for HTMX requests)
- **Keep** Playwright E2E tests (they already test through the real stack)
- **Add** HTMX-specific assertions: verify `hx-*` attributes, swap behavior, Alpine.js state changes

### 13.7 View Transitions & Analytics

Astro View Transitions intercept client-side navigation, breaking traditional page-view analytics. **Add a tracking hook:**

```astro
<!-- In Layout.astro -->
<script>
  document.addEventListener('astro:page-load', () => {
    // Push page view to analytics
    if (typeof gtag === 'function') {
      gtag('config', 'G-XXXXXXXX', { page_path: window.location.pathname });
    }
  });
</script>
```

### 13.8 Validation of Django-Endpoint Contract

**Add to Phase 0:** Before starting Phase 1, validate that the Django backend returns correct HTML fragments.

```bash
# Validation script for Phase 0
curl -H "HX-Request: true" http://localhost:5075/api/pages/home/fragment/ \
  | grep -q '<div' && echo "✅ HTML fragment OK" || echo "❌ Not returning HTML"

curl http://localhost:5075/api/fusion/health \
  | grep -q '"fusion_render_first"' && echo "✅ Health endpoint OK" || echo "❌ Health endpoint broken"
```

---

> **See also:**
> - [shadcnblocks/mainline-astro-template](https://github.com/shadcnblocks/mainline-astro-template) → Theme reference
> - [AHA Stack Guide](https://ahastack.dev) → Astro + HTMX + Alpine.js patterns
> - [Astro Docs](https://docs.astro.build) → Framework documentation
> - [django-fusion AGENTS.md](../../libs/django-fusion/AGENTS.md) → Backend fusion conventions
> - [FRONTEND_MERGE_ANALYSIS.md](../FRONTEND_MERGE_ANALYSIS.md) → Current frontend comparison
