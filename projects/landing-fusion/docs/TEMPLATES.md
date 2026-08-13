# Landing-Fusion — Template Architecture

> **Last updated:** 2026-08-10
> **Template engine:** Django (DjangoTemplates) + Wagtail CMS
> **Frontend companion:** Astro 5 (see `frontend/src/layouts/Layout.astro`)

---

## 1. Overview

Landing-Fusion uses a **dual-rendering** architecture: the same page can be served as
server-rendered HTML from Django templates OR as JSON data consumed by the Astro client.
The Django template layer is the canonical content source — Wagtail pages, snippets, and
the brandkit are authored in the CMS admin and rendered through Django templates.

```
Browser request
    │
    ├── / (HTML) ──────→ Django/Wagtail → pages/base.html → skeleton → content
    │
    └── /apis/* (JSON) → Django/Wagtail → JSON response → Astro client renders
```

---

## 2. Template Directory Map

```
projects/landing-fusion/
├── backend/apps/pages/templates/pages/    ← Canonical Django/Wagtail page templates
│   ├── base.html                          ← Root layout (everything)
│   ├── startup.html                       ← "The Startup" showcase
│   ├── founder.html                       ← Founder story page
│   ├── phase.html                         ← Project phase timeline
│   ├── prompt.html                        ← AI prompt / interact page
│   └── partials/
│       ├── skeleton.html                  ← Shimmer loading skeleton
│       ├── header.html                    ← Site header (nav, logo, auth)
│       └── footer.html                    ← Site footer
│
├── backend/assets/templates/              ← Product asset/template workspace;
│                                           not a source for the canonical page views
│
├── templates/                             ← django-allauth overrides
│   ├── account/login.html                 ← Login form
│   ├── account/signup.html                ← Signup form
│   └── mfa/index.html                     ← MFA setup
│
└── frontend/src/layouts/Layout.astro      ← Astro client-side layout (mirrors base.html)
```

---

## 3. Template Flow

### 3.1 Full Page Load

```
HTTP GET /
    │
    ▼
Django URL router → WagtailPage.serve()
    │
    ▼
pages/base.html                    ← <html>, <head>, theme init, fonts, CSS vars
    │
    ├── pages/partials/skeleton.html   ← Shimmer placeholder (hidden by inline JS)
    ├── #htmx-indicator                ← Global HTMX in-flight overlay
    ├── pages/partials/header.html     ← Nav + logo + auth controls
    │
    ├── <main>
    │   ├── auth_shell block           ← Allauth wrapper (transparent for non-auth)
    │   └── content block              ← Page-specific template rendered here
    │       (e.g., backend/apps/pages/templates/pages/startup.html)
    │
    ├── pages/partials/footer.html     ← Site footer
    ├── Cookie consent banner          ← Alpine component
    ├── Login modal                    ← Alpine component (allauth headless)
    ├── Brand modal                    ← Alpine component (product brandkit)
    │
    └── Scripts: HTMX + Alpine + i18n bridge + magnetic CTA
```

### 3.2 HTMX Fragment Swap

```
User clicks nav link
    │
    ▼
HTMX hx-get="/page-url/" → Django returns fragment HTML
    │
    ├── Response has no <html>/<head> — just the content block
    ├── #htmx-indicator shows shimmer during flight
    └── HTMX swaps content into <main>
```

---

## 4. Skeleton System

### 4.1 Design Philosophy

The skeleton is a **shimmer placeholder** that mirrors the real page layout — nav bar,
hero, stats grid, features grid, testimonial, and footer. It renders before content loads
(pure CSS, no JS) and is hidden once the DOM is interactive.

```
skeleton.html structure:
┌──────────────────────────────────────┐
│ ████          ██ ██ ██ ██     █████  │  ← nav bar
├──────────────────────────────────────┤
│              ┌────────┐              │
│              │  tag   │              │  ← hero section
│        ━━━━━━━━━━━━━━━━━━━━          │
│            ━━━━━━━━━━                │
│        [  btn  ] [  btn  ]           │
├──────────────────────────────────────┤
│  ████    ████    ████    ████        │  ← stats row
├──────────────────────────────────────┤
│         ┌────────┐                   │
│     ━━━━━━━━━━━━━━━━                 │  ← features section
│   ┌──────┐ ┌──────┐ ┌──────┐        │
│   └──────┘ └──────┘ └──────┘        │
├──────────────────────────────────────┤
│         ┌────────┐                   │
│     ━━━━━━━━━━━━━━━━                 │  ← testimonial section
│   ┌────────────────────┐            │
├──────────────────────────────────────┤
│ ██████    ██████    ██████           │  ← footer
└──────────────────────────────────────┘
```

### 4.2 Two Skeleton Mechanisms

| Mechanism | When | What |
|---|---|---|
| **First-paint skeleton** (`#fusion-skeleton`) | Full page load | Full-page shimmer with all regions. Hidden by inline script on `DOMContentLoaded`. |
| **HTMX indicator** (`#htmx-indicator`) | Fragment swap | Global overlay shimmer during `htmx:beforeRequest` → `htmx:afterRequest`. |

### 4.3 Skeleton vs Content Transition

```js
// Inline in base.html — runs before any external script
(function () {
  var skeleton = document.getElementById('fusion-skeleton');
  if (!skeleton) return;
  // Wait for DOM to be interactive, then fade out skeleton
  function hide() {
    skeleton.style.transition = 'opacity 0.3s ease';
    skeleton.style.opacity = '0';
    setTimeout(function () { skeleton.remove(); }, 300);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', hide);
  } else {
    hide();
  }
})();
```

---

## 5. Key Template Features

### 5.1 FOUC-Free Theme Init

Before any CSS loads, an inline script reads `localStorage('fusion-theme')` and sets
`<html class="dark|light">` to prevent a flash of wrong theme. Mirrors the Astro
`ThemeToggle.astro` component exactly.

### 5.2 Fusion Render Mode Meta

```html
<meta name="fusion-render-first" content="true|false" />
<meta name="fusion-render-mode" content="fusion-render|data-api" />
```

The Astro client reads these to decide whether to hydrate with server HTML or fetch
JSON from `/apis/*`.

### 5.3 CSS Variable System

```
:root {
  --fu-paper: 46 25% 98%;     ← page background
  --fu-ink: 40 6% 10%;        ← body text
  --fu-muted: 45 5% 44%;      ← secondary text
  --fu-line: 45 14% 88%;      ← borders
  --fu-card: 48 33% 100%;     ← card surfaces
  --fu-link: 217 91% 43%;     ← links
  --fu-accent: 48 100% 60%;   ← highlight
}
.dark { /* inverted palette */ }
```

All values are HSL color-space numbers (no `hsl()` wrapper) so Tailwind can compose
opacity variants: `bg-[hsl(var(--fu-card)/.8)]`.

### 5.4 Shared Design System CSS

The single CSS file `assets/static/css/fusion.css` is compiled from `frontend/src/styles/globals.css`
via `make css` (`@tailwindcss/cli`). It serves **both** render paths:
- Django: `<link rel="stylesheet" href="{% static 'css/fusion.css' %}">`
- Astro: imported by Vite in Layout.astro

`@source` directives in `globals.css` scan Django templates so Tailwind tree-shakes
correctly for both paths.

### 5.5 Inline Components (Alpine.js)

The `base.html` contains several Alpine components inline (not extracted to JS bundles) so
they work **without a JS build step**:

| Component | Trigger | Purpose |
|---|---|---|
| Cookie consent | `x-data` on page load | One-time consent banner |
| Login modal | `fusion:open-login` event | django-allauth headless login |
| Brand modal | `fusion:open-brand` event | Product brandkit viewer |
| Magnetic CTA | `alpine:init` → `Alpine.data('magnetic')` | Hero CTA hover effect |

### 5.6 i18n Bridge

A small JS snippet (`updateFusionLanguage()`) mirrors the Astro language switcher for
server-rendered pages. Supported languages: `en`, `ar`, `sv`, `fr`, `de`, `es`, `pt`.

---

## 6. Webpack Integration

Django-side JS/SCSS is bundled by webpack via `webpack/landing-fusion.config.js`:

```django
{% load webpack_loader %}
{% render_bundle 'landing' 'css' %}
{% render_bundle 'landing' 'js' %}
```

Output: `backend/assets/static/bundles/landing.[hash].css` + `bundles.json`.

---

## 7. Related Files

| File | Role |
|---|---|
| `backend/apps/pages/templates/pages/base.html` | Root layout — all pages extend this |
| `backend/apps/pages/templates/pages/partials/skeleton.html` | Shimmer placeholder skeleton |
| `frontend/src/layouts/Layout.astro` | Astro client-side layout (mirrors base.html) |
| `frontend/src/styles/globals.css` | Shared design system (compiled to fusion.css) |
| `webpack/landing-fusion.config.js` | Webpack config for Django-side SCSS/JS |
| `Makefile` | `make css` builds fusion.css; `make build-assets` builds webpack |
