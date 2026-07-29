/**
 * django-fusion — Webpack Entry Point
 *
 * This is the main entry point for the django-fusion webpack bundle.
 * It imports all component JS modules and SCSS styles that should be
 * included in the ``fusion`` bundle served via django-webpack-loader.
 *
 * The ``FUSION_ASSETS`` Django setting can optionally override which
 * assets are included per site, but this entry point defines the
 * *library-level defaults* that every django-fusion consumer gets.
 *
 * Usage (in Django template):
 *   {% load render_bundle from webpack_loader %}
 *   {% render_bundle 'fusion' 'css' %}
 *   {% render_bundle 'fusion' 'js' %}
 *
 * Or via the FusionAssets component in Next.js:
 *   <FusionAssets placement="top" />   (CSS in <head>)
 *   <FusionAssets placement="bottom" /> (JS before </body>)
 */

// ── Styles ──────────────────────────────────────────────────────────────────
// Import the main SCSS entry that bundles all component styles.
// Individual component SCSS files are imported from here so webpack
// can tree-shake unused styles in production builds.
import './fusion.scss';

// ── Component JavaScript ────────────────────────────────────────────────────
// Import shared UI behaviours: theme toggle, language switcher, modals, etc.
// These modules attach to global DOM events and enhance the server-rendered
// components without requiring a full SPA framework.
//
// Each import below corresponds to a registered django-fusion component
// that has JS interactivity. Add new imports as components are created.

// Base utilities (lazy-loaded on demand — not imported eagerly here)
// import './utils/dom-helpers';

// ---------------------------------------------------------------------------
// Lazy / deferred imports
// ---------------------------------------------------------------------------
// The following imports use dynamic `import()` so they are code-split into
// separate chunks and only loaded when the corresponding component is
// detected on the page. This keeps the initial `fusion` bundle lean.
//
// Example:
//   if (document.querySelector('[data-component="carousel"]')) {
//     import('./components/carousel');
//   }
// ---------------------------------------------------------------------------

// ── Polyfills (if needed) ──────────────────────────────────────────────────
// import 'core-js/stable';
// import 'regenerator-runtime/runtime';

// ── HMR helper (dev only) ──────────────────────────────────────────────────
if (module.hot) {
  module.hot.accept();
}
