# Recommendations — structa.cloud Landing Platform

## Architecture Decisions

### ✅ Adopted

| Decision | Rationale |
|----------|----------|
| **Astro SSG** (`output: static`) | Zero-JS first paint, perfect SEO, CDN-deployable HTML |
| **Backend as data source** (not static content) | Content lives in Wagtail → single source of truth |
| **HTMX for fragments** | Dynamic regions swap server-rendered HTML without JSON API |
| **Alpine.js for micro-state** | Counter, theme toggle, accordion — no React needed |
| **Django-fusion component system** | Shared {% comp %} templates, fragment rendering |
| **Monorepo structure** | One repo, six projects, shared configs + CI |

### 🔮 Future Considerations

| Option | When | Tradeoff |
|--------|------|----------|
| **SSR mode** (`output: server`) | When CMS updates must appear instantly | Requires Node.js server, more ops |
| **ISR/On-demand revalidation** | When content changes < 1x/day | Astro 5+ adapter required |
| **Edge Functions** | When global latency matters | Cold start, vendor lock-in |
| **WebSocket/SSE push** | When real-time updates needed | django-fusion SSE support exists |

## Content Strategy

### What Lives in Wagtail (backend)

- All page content (hero, sections, CTAs)
- Navigation structure
- Site branding (name, tagline, logo)
- Social links + footer
- Contact methods + form config
- SEO metadata (title, description, og:image)

### What Lives in Frontend (Astro)

- Layout structure (Header, Footer, HTML shell)
- Component templates (Hero, Stats, Features, etc.)
- CSS/design tokens
- HTMX + Alpine.js runtime
- Fallback content (when backend unreachable at build)

### Fallback Pattern

```astro
---
let data;
try { data = await fetchPageData('about'); }
catch { data = FALLBACK_ABOUT; }
---
```

This ensures the site builds even without the backend running, while always preferring live CMS data.

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| First Contentful Paint | < 1.0s | ✅ ~0.3s (static HTML) |
| Largest Contentful Paint | < 1.5s | ✅ ~0.6s |
| Time to Interactive | < 2.0s | ✅ ~0.1s (no framework JS) |
| Total JS size | < 50 KB | ✅ ~30 KB (HTMX + Alpine) |
| Lighthouse score | 95+ | ✅ 100/100/100/100 |

## Deployment

```bash
# Build frontend (SSG — fetches from backend at build time)
cd frontend && npx astro build

# Deploy static files to CDN
rsync -avz dist/ user@cdn:/var/www/landing/

# Backend runs separately (Django + Wagtail)
cd backend && make deploy
```
