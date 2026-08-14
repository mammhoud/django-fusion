# Use Case — structa.cloud Landing Platform

## Who It Serves

| Persona | Goal | Primary Path |
|---------|------|-------------|
| **Developer evaluator** | Assess django-fusion, ceptor-ai for adoption | /products → GitHub → docs |
| **Potential client** | Find Django/Wagtail development services | /about → /contact → email |
| **Open-source contributor** | Explore the monorepo, find contribution points | /projects → GitHub |
| **Technical decision-maker** | Compare server-rendered vs SPA approaches | /features → /faq |

## Core Use Case

A single-page-application-free company website that:

1. **Showcases open-source products** — django-fusion, ceptor-ai, django-bolt
2. **Documents the monorepo** — project structure, editions, shared vs standalone features
3. **Provides contact channels** — email, GitHub, LinkedIn, contact form
4. **Proves the stack** — the site IS the proof of the AHA stack (Astro + HTMX + Alpine)

## Content Flow

```
Visitor lands on /
  → hero: "Platforms that ship as documents"
  → stats: open-source metrics
  → stack section: Django+AHA description
  → products preview: 4 key products
  → HTMX/Alpine live demos
  → CTA: "View on GitHub"

Explores /products/
  → full product line cards with feature lists + tech badges

Checks /projects/
  → monorepo inventory: shared vs own features

Reads /about/
  → engineer background, skills, mission, testimonials

Gets answers /faq/
  → AHA stack, licensing, deployment, AI capabilities

Reaches out /contact/
  → contact methods from backend + form
```

## Key Interactions

| Interaction | Technology | Endpoint |
|-------------|-----------|----------|
| Navigation | SSR via Layout props | GET /apis/navigation/ |
| Branding/Footer | SSR via Layout props | GET /apis/site/settings/ |
| Page content | SSG (build-time fetch) | GET /apis/pages/<slug>/ |
| HTMX fragment swap | Client-side HTMX | Django-fusion handlers |
| Alpine micro-interactions | Client-side Alpine.js | No server call |
| Theme persistence | Client-side localStorage | No server call |
| Contact form | Client-side HTMX POST | POST /apis/contact/submit/ |

## Backend Data Sources

All content originates from Wagtail CMS:
- `SiteSettings` → branding, logo, social links, footer
- `HomePage` / `AboutPage` / `ProductsPage` etc. → StreamField content
- `ContactPage` → contact methods + form configuration
- `NavigationAPI` → nav items from published page tree
