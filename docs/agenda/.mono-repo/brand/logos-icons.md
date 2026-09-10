---
Object type: Page
Tags: logos, icons
Status: Active

# Logos & Icons — Brand Assets

> **Catalog** of all logos, favicons, and brand icons used across Structa Cloud websites.
> Each entry includes file path, visual description, color palette, usage context, and dimensions.

---

## Brand Identity Summary

| Brand | Primary Color | Secondary Color | Style | Mood |
|-------|--------------|-----------------|-------|------|
| **Structa Cloud** (shared) | Deep Teal `#0d9488` | Slate `#0f172a` | Clean, modern | Professional, trustworthy |
| **CTC Research** | Sky Blue `#0ea5e9` | White `#ffffff` | Research, academic | Knowledge-driven, precise |
| **LMS Demo** | Emerald `#10b981` | Dark `#111827` | Educational, warm | Learning-focused, inviting |
| **VResume** | Gold `#d98c00` | Cream `#f0e2d0` | Premium, warm | Career-focused, elegant |
| **CyperCloud** | Cyan `#06b6d4` | Dark `#0f172a` | Tech, futuristic | AI-powered, innovative |
| **POS Suite** | Teal `#14b8a6` | Indigo `#6366f1` | Modern, clean | Retail-ready, efficient |
| **django-fusion** | Blue `#3b82f6` | White `#ffffff` | Framework, dev-tool | Developer-friendly |
| **django-bolt** | Rust Red `#f7524a` | Dark `#1a1a2e` | Bold, performance | Fast, reliable |

---

## Shared Assets

### Structa Cloud Logo (Root)

| Property | Value |
|----------|-------|
| **File** | `logo.png` |
| **Path** | `logo.png` (project root) |
| **Dimensions** | Full-resolution PNG |
| **Usage** | Root brand identity, documentation headers, GitHub profile |
| **Description** | The master Structa Cloud logo — used as the primary brand identifier across all documentation, marketing materials, and repository branding |

### Shared Favicon

| Property | Value |
|----------|-------|
| **File** | `favicon.png` |
| **Path** | `projects/assets/static/images/favicon.png` |
| **Size** | 18,247 bytes |
| **Usage** | Default favicon for all Django sites (CTC Research, LMS, Portfolio) |
| **Description** | Shared favicon used as the default across all Wagtail CMS-powered sites. Falls back to the brand_settings configuration when a site-specific favicon is not set |

### Shared Logo (Static)

| Property | Value |
|----------|-------|
| **File** | `logo.png` |
| **Path** | `projects/assets/static/images/logo.png` |
| **Size** | 7,785 bytes |
| **Usage** | Default logo fallback in header templates, email footers |
| **Description** | Lightweight shared logo used as the default fallback when a site-specific logo is not configured in Wagtail brand settings |

### Logo HTML Template

| Property | Value |
|----------|-------|
| **File** | `logo.html` |
| **Path** | `projects/assets/templates/partials/logo.html` |
| **Usage** | All Wagtail CMS sites — header logo rendering |
| **Description** | Smart logo template that checks `brand_settings.logo` first, renders the configured Wagtail image at 165×120, and falls back to a text-based logo or the `lms-ribbon.svg` brand asset |

---

## CTC Research (`ctc-research.com`)

| Asset | File | Path | Notes |
|-------|------|------|-------|
| **Favicon (96px)** | `favicon-96x96.max-96x96.png` | `projects/cms/ctc-research/assets/media/images/` | Primary favicon, served at 96×96 |
| **Favicon (165px)** | `favicon-96x96.max-165x165.png` | `projects/cms/ctc-research/assets/media/images/` | High-DPI favicon variant |
| **Favicon (200px)** | `favicon-96x96_EzniaxT.max-200x140.png` | `projects/cms/ctc-research/assets/media/images/` | Wagtail rendition for admin |
| **LMS Logo** | `lms-logo_9NNEvds.*` | `projects/cms/ctc-research/assets/media/images/` | LMS branding reused — multiple Wagtail renditions (120px, 140px, 157px, 165px, 196px, 393px) |
| **LMS Logo (alt)** | `lms-logo_eO8yOQm.max-165x165.png` | `projects/cms/ctc-research/assets/media/images/` | Square variant for sidebar/header |
| **CTC Research Logo** | `ctc_research_logo.max-165x120.jpg` | `projects/cms/ctc-research/assets/media/images/` | Research brand logo, landscape format |
| **CTC Research Logo (alt)** | `ctc_research_logo.max-200x140.jpg` | `projects/cms/ctc-research/assets/media/images/` | Higher-resolution variant |
| **UI Icons** | `ui-icons_*.png` (7 files) | `projects/cms/ctc-research/assets/static/styles/images/` | jQuery UI sprite sheets — colors: `#d8e7f3`, `#cd0a0a`, `#6da8d5`, `#2e83ff`, `#217bc0`, `#469bdd`, `#f9bd01` |
| **Avatar** | `avatar_*_diving-instructor-icon-vector-*.jpg` | `projects/cms/ctc-research/assets/avatar_images/` | Sample avatar for CMS demo content |

**Brand Colors:**
- Primary: Sky Blue `#0ea5e9` — Trust, research, clarity
- Secondary: White `#ffffff` — Clean, academic
- Accent: Light Blue `#6da8d5` — UI elements, links
- Warning: Gold `#f9bd01` — Notifications, highlights

---

## LMS Demo (`structa.cloud`)

| Asset | File | Path | Notes |
|-------|------|------|-------|
| **Favicon (96px)** | `favicon-96x96.max-96x96.png` | `projects/lms/cms/assets/media/images/` | Primary favicon |
| **Favicon (165px)** | `favicon-96x96.max-165x165.png` | `projects/lms/cms/assets/media/images/` | HiDPI variant |
| **Favicon (alt)** | `favicon-96x96_EzniaxT.max-*.png` | `projects/lms/cms/assets/media/images/` | Wagtail renditions (96, 120, 165, 200px) |
| **LMS Logo** | `lms-logo_9NNEvds.*` | `projects/lms/cms/assets/media/images/` | Multiple Wagtail renditions — landscape and square variants |
| **LMS Logo (alt)** | `lms-logo_eO8yOQm.max-165x165.png` | `projects/lms/cms/assets/media/images/` | Square variant |
| **LMS Static Logo** | `logo.svg` | `projects/lms/assets/static/` | SVG logo for static rendering |
| **LMS Static Favicon** | `favicon.ico` | `projects/lms/assets/static/` | ICO format for legacy browsers |
| **LMS Icon** | `icon.webp` | `projects/lms/assets/static/` | Modern WebP icon |
| **LMS Dark Logo** | `logo-dark.png` | `projects/lms/assets/static/` | Dark mode variant |
| **UI Icons** | `ui-icons_*.png` (7 files) | `projects/lms/cms/assets/static/styles/images/` | jQuery UI sprite sheets |
| **Font Icons** | `remixicon.svg`, `fa-brands-400.svg`, `Flaticon.svg`, `pe-icon-7-stroke.svg` | `projects/lms/front-end/public/fonts/` | Icon font bundles for LMS frontend |

**Brand Colors:**
- Primary: Emerald `#10b981` — Growth, learning, progress
- Dark: `#111827` — Text, headers
- Accent: `#6da8d5` — Links, interactive elements
- Highlight: `#f9bd01` — Achievements, badges

---

## VResume / Portfolio (`vresume.structa.cloud`)

| Asset | File | Path | Notes |
|-------|------|------|-------|
| **Logo (SVG)** | `logo.svg` | `projects/cms/portfolio/assets/static/images/ui/` | Gold gradient text logo — "V" in bold Poppins with gold gradient (`#d98c00` → `#ffa65c`), "Resume" in cream `#f0e2d0` |
| **Favicon (SVG)** | `favicon.svg` | `projects/cms/portfolio/assets/static/images/ui/` | Rounded-rect gold gradient badge with white "V" letter — `rx="6"` border radius |
| **UI Icons** | `ui-icons_*.png` (7 files) | `projects/cms/portfolio/assets/static/styles/images/` | jQuery UI sprite sheets |
| **Font Icons** | `fa-brands-400.svg`, `remixicon.svg` | `projects/cms/portfolio/assets/static/fonts/` | FontAwesome brands + Remix icon fonts |

**Logo SVG Details:**
- **Viewbox:** `0 0 200 50`
- **"V" letter:** Poppins 700, 32px, gold gradient fill (`#d98c00` → `#ffa65c`)
- **"Resume" text:** Poppins 600, 28px, cream fill `#f0e2d0`
- **Favicon:** 32×32 rounded rect with same gradient, white "V" centered

**Brand Colors:**
- Primary Gold: `#d98c00` → `#ffa65c` (gradient) — Premium, career, warmth
- Cream: `#f0e2d0` — Elegant text, backgrounds
- Mood: Professional portfolio, career-focused, premium feel

---

## POS Suite (Desktop App)

### Tauri Icons (All Editions)

| Asset | File | Path | Used By |
|-------|------|------|---------|
| **App Icon (PNG)** | `icon.png` | `projects/pos/pos-{mini,solo,full}/src-tauri/icons/` | Tauri app icon, macOS/Linux |
| **App Icon (ICO)** | `icon.ico` | `projects/pos/pos-{mini,solo,full}/src-tauri/icons/` | Windows executable icon |
| **High-Res Icon** | `icon-512.png` | `projects/pos/pos-{solo,full}/src-tauri/icons/` | 512px icon for high-DPI |
| **Logo Image** | `logo-img.png` | `projects/pos/pos-{solo,full}/src-tauri/icons/` | Window title bar, about dialog |
| **Logo (src)** | `logo-img.png` | `projects/pos/pos-{solo,full}/src/assets/` | Frontend logo component |
| **Logo (mini)** | `logo-img.png` | `projects/pos/pos-mini/src/assets/` | Minimal edition frontend |

**POS Brand Colors:**
- Primary Teal: `#14b8a6` — Retail, transactions, efficiency
- Secondary Indigo: `#6366f1` — Actions, buttons, highlights
- Success Green: `#10b981` — Completed sales, positive states
- Warning Amber: `#f59e0b` — Low stock, alerts
- Danger Red: `#ef4444` — Returns, errors, deletions

---

## CyperCloud (`localhost:5073`)

| Asset | File | Path | Notes |
|-------|------|------|-------|
| **Logo (SVG)** | `logo.svg` | `projects/cypercloud/assets/static/` | Primary brand logo |
| **Logo White** | `logo-white.svg` | `projects/cypercloud/assets/static/` | White variant for dark backgrounds |
| **Favicon** | `favicon.ico` | `projects/cypercloud/assets/static/` | ICO format favicon |
| **App Icon** | `icon.png` | `projects/cypercloud/assets/static/` | PNG icon for PWA/mobile |

**Brand Colors:**
- Primary Cyan: `#06b6d4` — AI, innovation, futuristic
- Dark: `#0f172a` — Deep backgrounds, code
- Accent: `#22d3ee` — Interactive elements, highlights
- Glow: `#06b6d4` at 50% opacity — Neon effects, hover states

---

## django-fusion (Library)

| Asset | File | Path | Notes |
|-------|------|------|-------|
| **Favicon** | `favicon.png` | `libs/django-bolt/docs/` | Shared with django-bolt docs |

**Brand Colors:**
- Primary Blue: `#3b82f6` — Framework, developer tools
- Secondary: `#60a5fa` — Links, interactive
- Dark: `#1e293b` — Code blocks, backgrounds

---

## django-bolt (Library)

| Asset | File | Path | Notes |
|-------|------|------|-------|
| **Icon** | `icon.png` | `libs/django-bolt/docs/` | 65KB — Library icon |
| **Favicon** | `favicon.png` | `libs/django-bolt/docs/` | 63KB — Docs favicon |
| **Logo** | `logo.png` | `libs/django-bolt/docs/` | 101KB — Full library logo |

**Brand Colors:**
- Rust Red: `#f7524a` — Performance, speed, Rust
- Dark: `#1a1a2e` — Code, terminal backgrounds
- Accent: `#ff6b6b` — Highlights, active states

---

## Documentation Site (`structa.cloud/docs`)

| Asset | File | Path | Notes |
|-------|------|------|-------|
| **Favicon** | `favicon.png` | `site/assets/images/` | MkDocs site favicon |

---

## Icon Libraries Used

| Library | Format | Used By | Description |
|---------|--------|---------|-------------|
| **Remix Icon** | SVG font | LMS, Portfolio, all sites | 2,800+ open-source icons |
| **Font Awesome Brands** | SVG font | LMS, Portfolio | Brand/social icons (400+) |
| **Flaticon** | SVG font | LMS | Custom icon sets |
| **Pe Icon 7 Stroke** | SVG font | LMS, shared assets | 762 line icons |
| **Tabler Icons** | CSS | Shared assets | 500+ MIT-licensed icons |
| **jQuery UI Icons** | PNG sprites | CTC, LMS, Portfolio, CMS | UI widget icons (7 color variants) |

---

## Favicon Rendering Standards

| Format | Size | Browser Support |
|--------|------|----------------|
| `favicon.ico` | 32×32, 16×16 | All browsers |
| `favicon.png` | 96×96 | Modern browsers |
| `icon.png` | 192×192 | Android/PWA |
| `icon-512.png` | 512×512 | Android/PWA splash |
| `icon.webp` | — | Modern browsers (WebP) |
| `favicon.svg` | Scalable | Modern browsers (SVG) |

---

## Related

- → `./_index.md` — Brand index
- → `../objects/style.md` — Design tokens & brand
- → `../plans/projects.md` — Project color map
