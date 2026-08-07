# 📊 Static Assets Usage Analysis

**Path:** `projects/assets/static/`
**Status:** ✅ Active — used by all projects

---

## Directory Overview

This directory contains all shared frontend assets (JS, CSS/SCSS, images, fonts, videos). It is served at `/static/` via Django's staticfiles framework and Nginx `shared-media`.

**Configuration source:** `projects/configs/base/assets.py` → `SHARED_STATIC_DIR`

---

## Subdirectory Usage

| Subdirectory | Used By | Usage Pattern |
|-------------|---------|---------------|
| `js/` | **All projects** | Loaded via `static.js` entry point → webpack bundles → `{% static %}` in templates |
| `styles/` | **All projects** | SCSS compiled via `main.scss` → webpack → CSS bundles → `{% static %}` in templates |
| `images/` | **All projects** | Referenced in CSS/SCSS (`url()`) and directly in templates (`{% static %}`) |
| `fonts/` | **All projects** | Loaded via CSS `@font-face` rules in stylesheets |
| `videos/` | **All projects** | Referenced in templates for hero sections and backgrounds |

---

## Key Files

| File | Used By | Notes |
|------|---------|-------|
| `static.js` | **All projects** | Main JS entry point — imports libraries, site SCSS, and `main.js` |
| `styles.js` | **All projects** | Empty — placeholder for future CSS-only entry |
| `js/main.js` | **All projects** | Core application JavaScript |
| `js/app.js` | **All projects** | Application initialization |
| `js/core/app.js` | **All projects** | App runtime bootstrap |
| `js/core/main.js` | **All projects** | Main module loader |
| `js/core/init.config.js` | **All projects** | Configuration initialization |
| `js/core/htmx-bridge.js` | **All projects** | HTMX integration bridge |
| `js/modules/` | **All projects** | Feature modules (index, manager.init, readiness) |
| `js/plugins/` | **All projects** | Plugin JS entry points |
| `js/forms.js` | **All projects** | Form handling |
| `js/modals.js` | **All projects** | Modal interactions |
| `js/notifications.js` | **All projects** | Notification UI |
| `js/registry.js` | **All projects** | Component registry |
| `js/htmx-config.js` | **All projects** | HTMX configuration |
| `js/theme/` | **All projects** | Theme-specific JS |
| `js/utility/` | **All projects** | Utility helpers (dom, url, state, mixins, etc.) |
| `styles/main.scss` | **All projects** | Main SCSS entry point |
| `styles/components/` | **All projects** | Component styles (accordions, carousels, dropdowns, events, filters, header, menu, modals, popups, profile, progress, etc.) |
| `styles/layout/` | **All projects** | Layout styles (content, grid, listing, sections) |
| `styles/pages/` | **All projects** | Page-specific styles (auth, contact, errors, learning, preloader, profile, video-viewer) |
| `styles/base/` | **All projects** | Base styles (base, buttons, forms, modal, typography) |
| `styles/colors/` | **All projects** | Color system (index, master, palette, shared) |
| `styles/theme/` | **All projects** | Theme configuration (index) |
| `styles/spacing/` | **All projects** | Spacing utilities (paddings) |
| `styles/utility/` | **All projects** | Utility classes (helpers, nice-select, simplebar) |
| `styles/usecases/` | **All projects** | Use-case-specific styles (animations, crm, forms, landing, lms, modal, spa) |
| `fonts/fa/` | **All projects** | Font Awesome icon font |
| `fonts/bootstrap-icons/` | **All projects** | Bootstrap Icons font |
| `fonts/inter/` | **All projects** | Inter font family |
| `fonts/roboto/` | **All projects** | Roboto font family |
| `fonts/remixicon/` | **All projects** | Remixicon icon font |
| `fonts/ming-cute/` | **All projects** | MingCute icon font |
| `fonts/pe-icons/` | **All projects** | PE Icon 7 Stroke font |
| `fonts/flat-icons/` | **All projects** | Flaticon icon font |
| `fonts/material-symbols/` | **All projects** | Material Symbols font |
| `fonts/tabler-icons.css` | **All projects** | Tabler Icons CSS |
| `fonts/consax.css` | **All projects** | Consax icon CSS |
| `fonts/feather.js` | **All projects** | Feather Icons JS |
| `fonts/index.css` | **All projects** | Combined font index |
| `fonts/flags/` | **All projects** | Flag icon CSS |
| `images/element/` | **All projects** | UI element illustrations (SVG, PNG) |
| `images/avatar/` | **All projects** | Avatar images |
| `images/brand/` | **All projects** | Brand logos and illustrations |
| `images/backgrounds/` | **All projects** | Background patterns |
| `images/about/` | **All projects** | About page images |
| `images/default-avatar.jpg` | **All projects** | Default user avatar |
| `images/default-course.jpg` | **All projects** | Default course image |
| `images/logo.png` | **All projects** | Site logo |
| `images/favicon.png` | **All projects** | Favicon |
| `images/loader.svg` | **All projects** | Loading spinner |
| `images/coming-soon.jpg` | **All projects** | Coming soon placeholder |
| `images/auth-bg-default.jpg` | **All projects** | Auth page background |
| `videos/home-video-1.mp4` | **All projects** | Hero section background video |
