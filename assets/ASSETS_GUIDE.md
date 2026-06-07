# Assets & Frontend Build Guide

Reference for the shared frontend build system used across all three sites.

---

## How the Webpack Build Works

All JavaScript and CSS for the workspace is managed by a single Webpack setup located in `assets/`.
The build entry point is `assets/scripts/workspace.mjs` — a Node CLI that routes commands to the right site via the `--site` flag.

The webpack configuration lives in `webpack/main.config.js` and is driven by `webpack/common.config.js`,
`webpack/dev.config.js`, and `webpack/paths.js`. The `--env site=<sitename>` argument selects which
site's entry points and output directories are used.

Site aliases are resolved in `workspace.mjs`:
- `ctc` / `ctc-research` / `ctc-research.com` → `ctc-research`
- `structa` / `lms` / `lms-demo` / `structa.cloud` → `lms-demo`
- `vresume` / `VResume` / `resume` → `vresume`

---

## Per-Site Build Commands

All commands run from the workspace root using `npm --prefix assets`:

```bash
# Build a single site (production)
npm --prefix assets run build:ctc       # ctc-research
npm --prefix assets run build:structa   # lms-demo
npm --prefix assets run build:vresume   # VResume

# Build all sites at once
npm --prefix assets run build:all

# Development builds (faster, no minification)
npm --prefix assets run build:dev -- --site ctc
npm --prefix assets run build:dev -- --site vresume

# Watch mode (rebuilds on file change)
npm --prefix assets run watch -- --site ctc

# Dev server (webpack-dev-server with HMR)
npm --prefix assets run dev -- --site ctc

# Build then run Django collectstatic
npm --prefix assets run build:collect:ctc
npm --prefix assets run build:collect:structa
npm --prefix assets run build:collect:vresume
npm --prefix assets run build:collect:all

# Collectstatic only (no rebuild)
npm --prefix assets run collectstatic:ctc
npm --prefix assets run collectstatic:all

# Clean bundles
npm --prefix assets run clean:ctc
npm --prefix assets run clean:all

# Analyze bundle sizes
npm --prefix assets run analyze -- --site ctc
```

You can also invoke `workspace.mjs` directly:

```bash
node assets/scripts/workspace.mjs build --site vresume
node assets/scripts/workspace.mjs watch --site ctc
node assets/scripts/workspace.mjs manage --site ctc -- migrate
```

---

## Available JavaScript Libraries

The following libraries are available in the shared `node_modules` and can be imported in site JS files:

### Core Frameworks
| Library | Version | Import |
|---------|---------|--------|
| Alpine.js | ^3.14 | `import Alpine from 'alpinejs'` |
| HTMX 2 | ^2.0 | `import 'htmx.org'` |
| Vue 3 | ^3.5 | `import { createApp } from 'vue'` |
| jQuery | ^3.7 | `import $ from 'jquery'` |

### UI Frameworks & Components
| Library | Version | Notes |
|---------|---------|-------|
| Bootstrap 5 | ^5.3 | CSS + JS |
| Bootstrap Icons | ^1.11 | Icon font |
| FlyonUI | ^2.2 | Tailwind component library |
| Preline | ^3.2 | Tailwind UI components |
| FrostUI | ^1.4 | UI toolkit |

### Charts & Visualization
| Library | Version | Notes |
|---------|---------|-------|
| Chart.js | ^4.4 | Canvas charts |
| ApexCharts | 4.5 | SVG charts |
| ECharts | ^5.5 | Advanced charts |
| JSVectorMap | ^1.6 | Maps |
| Leaflet | ^1.9 | Interactive maps |

### Forms & Input
| Library | Version | Notes |
|---------|---------|-------|
| Choices.js | ^11.0 | Select/multi-select |
| Select2 | ^4.1 | Enhanced select |
| Quill | ^2.0 | Rich text editor |
| Air Datepicker | ^3.5 | Date/time picker |
| noUiSlider | ^15.8 | Range slider |
| Cleave.js | ^1.6 | Input formatting |
| Dropzone | ^6.0 | File upload |
| Sortable.js | ^1.15 | Drag-and-drop sort |
| Tagify | ^4.31 | Tag input |
| Dual Listbox | ^2.0 | Transfer widget |
| Star Rating.js | ^4.3 | Star ratings |

### UX & Animation
| Library | Version | Notes |
|---------|---------|-------|
| SweetAlert2 | ^11.14 | Beautiful alerts/modals |
| Swiper | ^11.1 | Touch slider/carousel |
| AOS | ^2.3 | Animate on scroll |
| Animate.css | ^4.1 | CSS animations |
| Dragula | ^3.7 | Drag-and-drop |
| GLightbox | ^3.3 | Image/video lightbox |
| Shepherd.js | ^14.3 | Product tours |
| WOW.js | ^1.1 | Scroll reveal |
| SAL.js | ^0.8 | Scroll animation |

### Layout & Navigation
| Library | Version | Notes |
|---------|---------|-------|
| Isotope | ^3.0 | Filterable grid |
| Masonry | ^4.2 | Masonry layout |
| SimpleBar | ^6.3 | Custom scrollbar |
| MixItUp | ^3.3 | Animated filter/sort |

### Media & Calendar
| Library | Version | Notes |
|---------|---------|-------|
| FullCalendar | ^6.1 | Event calendar |
| Plyr | ^3.4 | Media player |
| Vanilla Calendar Pro | latest | Lightweight calendar |

### CSS
| Library | Version | Notes |
|---------|---------|-------|
| Tailwind CSS | ^4.1 | Utility-first CSS |
| Bootstrap 5 | ^5.3 | Component CSS |
| Remixicon | ^4.6 | Icon set |

---

## Static File Paths

Each site has its own static source files and compiled output:

### ctc-research
- Source JS: `ctc-research/assets/static/js/`
- Source SCSS: `ctc-research/assets/static/styles/`
- Compiled bundles: `ctc-research/assets/bundles/ctc-research/`
- Collectstatic output: `ctc-research/assets/staticfiles/`

### lms-demo
- Source JS: `lms-demo/assets/static/js/`
- Source SCSS: `lms-demo/assets/static/styles/`
- Compiled bundles: `lms-demo/assets/bundles/lms-demo/`
- Collectstatic output: `lms-demo/assets/staticfiles/`

### VResume
- Source JS: `VResume/assets/static/js/`
- Source SCSS: `VResume/assets/static/styles/`
- Compiled bundles: `VResume/assets/bundles/vresume/`
- Collectstatic output: `VResume/assets/staticfiles/`

### Shared
- Shared source: `assets/static/`
- Shared bundles: `assets/bundles/shared/`
- node_modules: `assets/node_modules/`

---

## Media Configuration

Media files (user-uploaded content) are stored separately from static files:

| Site | Media directory | Django setting |
|------|----------------|----------------|
| ctc-research | `assets/media/` (workspace-level) | `MEDIA_ROOT` |
| lms-demo | `lms-demo/assets/media/` | `MEDIA_ROOT` |
| VResume | `VResume/assets/media/` | `MEDIA_ROOT` |

In Docker, the workspace media directory is mounted:
```yaml
volumes:
  - ../assets/media:/app/assets/media:z
```

VResume has `MediaRequestLoggingMiddleware` which logs all requests to `MEDIA_URL` paths
for debugging media serving issues (see `VResume/www/core/middleware.py`).

---

## How to Add New JS to a Site

1. **Install the package** (from `assets/` directory):
   ```bash
   npm --prefix assets install <package-name> --save
   ```

2. **Import it in the site's entry file**, e.g. `ctc-research/assets/static/js/app.js`:
   ```js
   import MyLibrary from 'my-library';
   // initialise...
   ```

3. **For lazy-loaded chunks**, use dynamic imports:
   ```js
   const module = await import('heavy-library');
   ```

4. **Rebuild**:
   ```bash
   npm --prefix assets run build:ctc
   ```

5. **Collect static** (if running Django locally):
   ```bash
   npm --prefix assets run collectstatic:ctc
   ```

If the library is shared across all sites, import it from the shared entry (`assets/static/static.js`)
and add it to the shared bundle config in `webpack/common.config.js`.

---

## Bundle Manifest

After a successful build, each site's bundle directory contains a `bundles.json` manifest file
that maps logical chunk names to hashed filenames. Django reads this via `webpack_loader` or
`django-webpack-loader` to inject the correct script/link tags in templates.

Example: `VResume/assets/bundles/vresume/bundles.json`

---

## Install Dependencies

Before building, install Node dependencies once:

```bash
npm --prefix assets ci --include=dev --legacy-peer-deps
```

Or via Make:

```bash
make install-assets
```
