---
title: Websites Webpack & Frontend
description: Unified webpack build system, JS/CSS libraries, and static asset pipeline for both websites
inclusion: auto
---

# Websites Webpack & Frontend

## Overview

Both `structa.cloud` and `ctc-research.com` share a **single unified webpack build** located in `websites/webpack/`. The build is controlled by the `PROJECT_PATH` environment variable to produce site-specific output bundles.

```
websites/
├── webpack/
│   ├── common.config.js    # Shared loaders, plugins, path resolution
│   ├── main.config.js      # Mode-specific config (prod/dev/watch/serve)
│   ├── dev.config.js       # Dev server overrides
│   ├── postcss.config.js   # PostCSS plugins
│   ├── tailwind.config.js  # Tailwind CSS v4 config
│   ├── package-copy.json   # Packages to copy verbatim to bundles/libs/
│   └── preload.js          # Preload script
├── assets/
│   └── static/             # SHARED source (entry point, JS, fonts, images, videos)
│       ├── static.js        # Main entry point — imports all shared JS/CSS
│       ├── styles.js        # Shared styles entry
│       ├── js/              # Shared JavaScript modules
│       ├── styles/          # Shared CSS/SCSS
│       ├── fonts/
│       ├── images/
│       └── videos/
├── bundles/
│   ├── ctc-research.com/   # Webpack output for ctc-research.com
│   └── structa.cloud/      # Webpack output for structa.cloud
├── ctc-research.com/
│   └── assets/static/
│       └── styles/          # Site-specific styles ONLY
└── structa.cloud/
    └── assets/static/
        └── styles/          # Site-specific styles ONLY
```

## Build Commands

### From `websites/` (recommended)

```bash
# Build production bundle for ctc-research.com
npm run build:ctc

# Build production bundle for structa.cloud
npm run build:structa

# Build both sites
npm run build:all

# Development build (ctc-research.com by default)
npm run build:dev

# Watch mode
PROJECT_PATH=structa.cloud npm run watch

# Dev server with HMR (proxies to Django on :8000)
npm run dev

# Clean all bundles
npm run clean

# Bundle analysis
npm run analyze
```

### From inside a site directory

```bash
cd websites/ctc-research.com
npm run build         # production
npm run build:dev     # development
npm run watch         # watch mode
npm run dev           # dev server
```

### Via site Makefile

```bash
make frontend-build        # development build
make frontend-production   # production build
make frontend-watch        # watch mode
make frontend-install      # npm install
```

## Path Resolution

The webpack config resolves two aliases:

| Alias | Points to | Purpose |
|---|---|---|
| `shared` | `websites/assets/static/` | Shared JS, fonts, images, shared styles |
| `site` | `websites/<PROJECT_PATH>/assets/static/` | Site-specific styles |

```javascript
// In static.js or any JS file
import 'shared/styles/base.scss';
import 'site/styles/theme.scss';
```

## Entry Point

The single entry point is `websites/assets/static/static.js`. It imports all shared JS libraries and CSS:

```javascript
// websites/assets/static/static.js
import 'alpinejs';
import 'htmx.org';
import 'bootstrap';
import 'shared/styles/main.scss';
// ... other shared imports
```

Site-specific styles are imported via the `site` alias in the site's own style files.

## Output

Webpack outputs to `websites/bundles/<PROJECT_PATH>/`:

```
bundles/ctc-research.com/
├── bundles.json              # BundleTracker manifest (read by django-webpack-loader)
├── static.<hash>.js          # Main JS bundle
├── vendors.<hash>.js         # Vendor chunk
├── runtime.<hash>.js         # Webpack runtime
├── css/
│   ├── static.<hash>.min.css
│   └── static-rtl.<hash>.min.css   # Auto-generated RTL variant
├── js/                       # Copied from assets/static/js/
├── images/                   # Copied from assets/static/images/
├── fonts/                    # Copied from assets/static/fonts/
└── libs/                     # Packages from package-copy.json
```

## Django Integration

Bundles are served via **django-webpack-loader**:

```python
# configs/settings/base.py
WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": BASE_DIR / "assets" / "bundles" / "bundles.json",
    }
}
```

```html
<!-- In base templates -->
{% load webpack_loader %}
{% render_bundle 'static' 'CSS' %}
{% render_bundle 'static' 'JS' %}
```

In Docker, bundles are served by nginx from `/static/`.

## JavaScript Libraries

The workspace `package.json` defines all shared JS dependencies. Both sites use the same `node_modules/`.

### Core UI Framework

| Library | Version | Purpose |
|---|---|---|
| `alpinejs` | ^3.14.9 | Reactive UI components |
| `htmx.org` | ^2.0.8 | HTMX for server-driven UI |
| `htmx-ext-sse` | ^2.2.4 | HTMX SSE extension |
| `bootstrap` | ^5.3.6 | CSS framework |
| `bootstrap-icons` | ^1.11.3 | Icon set |

### CSS & Styling

| Library | Version | Purpose |
|---|---|---|
| `tailwindcss` | ^4.1.18 | Utility CSS (v4) |
| `@tailwindcss/forms` | ^0.5.10 | Form styles |
| `@tailwindcss/postcss` | ^4.1.11 | PostCSS integration |
| `flyonui` | ^2.2.0 | UI component library |
| `preline` | ^3.2.2 | Tailwind UI components |
| `animate.css` | ^4.1.1 | CSS animations |
| `remixicon` | ^4.6.0 | Icon set |

### Charts & Data Visualization

| Library | Version | Purpose |
|---|---|---|
| `apexcharts` | 4.5.0 | Charts |
| `chart.js` | ^4.4.4 | Charts |
| `echarts` | ^5.5.1 | Advanced charts |
| `jsvectormap` | ^1.6.0 | Vector maps |

### Forms & Input

| Library | Version | Purpose |
|---|---|---|
| `choices.js` | ^11.0.2 | Select/multiselect |
| `select2` | ^4.1.0-rc.0 | Select with search |
| `@yaireo/tagify` | ^4.31.3 | Tag input |
| `quill` | ^2.0.2 | Rich text editor |
| `air-datepicker` | ^3.5.3 | Date picker |
| `cleave.js` | ^1.6.0 | Input masking |
| `nouislider` | ^15.8.1 | Range slider |
| `dropzone` | ^6.0.0-beta.2 | File upload |

### UI Components

| Library | Version | Purpose |
|---|---|---|
| `swiper` | ^11.1.14 | Touch slider |
| `glightbox` | ^3.3.1 | Lightbox |
| `fullcalendar` | ^6.1.15 | Calendar |
| `sortablejs` | ^1.15.3 | Drag-and-drop sorting |
| `dragula` | ^3.7.3 | Drag-and-drop |
| `sweetalert2` | ^11.14.5 | Alert dialogs |
| `shepherd.js` | ^14.3.0 | Product tours |
| `simplebar` | ^6.3.2 | Custom scrollbar |
| `gridjs` | ^6.2.0 | Data grid |

### jQuery & Plugins

| Library | Version | Purpose |
|---|---|---|
| `jquery` | ^3.7.1 | DOM manipulation |
| `jquery-ui` | ^1.14.0 | UI widgets |
| `slick-carousel` | ^1.8.1 | Carousel |
| `owl.carousel` | ^2.3.4 | Carousel |
| `masonry-layout` | ^4.2.2 | Masonry grid |

### Vue.js

| Library | Version | Purpose |
|---|---|---|
| `vue` | ^3.5.16 | Vue 3 components |
| `vue-loader` | ^17.4.2 | Webpack Vue loader |
| `@vue/compiler-sfc` | ^3.5.16 | SFC compilation |

### Utilities

| Library | Version | Purpose |
|---|---|---|
| `aos` | ^2.3.4 | Scroll animations |
| `countup.js` | ^2.8.0 | Number animations |
| `wowjs` | ^1.1.3 | Scroll reveal |
| `leaflet` | ^1.9.4 | Maps |
| `plyr` | ^3.4.3 | Media player |
| `prismjs` | ^1.29.0 | Syntax highlighting |
| `feather-icons` | ^4.29.2 | Icon set |

## PostCSS Pipeline

```javascript
// webpack/postcss.config.js
module.exports = {
  plugins: [
    require('postcss-import'),
    require('@tailwindcss/postcss'),
    require('autoprefixer'),
    require('postcss-preset-env'),
    require('cssnano'),   // production only
  ]
}
```

## RTL Support

The build automatically generates RTL CSS variants using `rtlcss`:

```
css/static.min.css      → LTR (default)
css/static-rtl.min.css  → RTL (auto-generated)
```

Load the RTL variant based on `dir="rtl"` on the `<html>` element.

## Docker Build

In Docker (`RUNNING_ENV=docker`), webpack runs during the image build:

```dockerfile
# compose/django/Dockerfile
RUN npm ci --prefix /app/shared
RUN PROJECT_PATH=${SITE_NAME} npm run build:prod --prefix /app/shared
```

The output is placed in `/app/assets/bundles/` and served by nginx at `/static/`.

## Development Workflow

```bash
# 1. Install dependencies (once)
cd websites
npm install

# 2. Start Django dev server (in one terminal)
cd websites/ctc-research.com
make dev

# 3. Start webpack watch (in another terminal)
cd websites
PROJECT_PATH=ctc-research.com npm run watch

# Or use the dev server with HMR (proxies to Django :8000)
npm run dev
```

The dev server runs on `http://localhost:3000` and proxies all non-asset requests to Django on `:8000`.

## Adding a New JS Library

1. Add to `websites/package.json` dependencies with a pinned version.
2. Import in `websites/assets/static/static.js` (shared) or in a site-specific JS file.
3. If the library needs to be available globally (e.g., jQuery plugins), add to `ProvidePlugin` in `common.config.js`.
4. If the library should be copied verbatim (not bundled), add to `websites/webpack/package-copy.json`.

## Tailwind CSS v4

The project uses Tailwind CSS v4 with PostCSS integration:

```css
/* In a .scss or .css file */
@import "tailwindcss";
@plugin "@iconify/tailwind4";
```

Configuration is in `websites/webpack/tailwind.config.js`. Site-specific theme customization goes in the site's `assets/static/styles/` directory.
