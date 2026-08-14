/**
 * Landing-Fusion Webpack Workspace (for django-fusion webpack)
 *
 * ⚠️  This is a WORKSPACE CONFIG consumed by libs/django-fusion/webpack.config.js
 *     via FUSION_WEBPACK_WORKSPACE_PATH. It only defines django-fusion component
 *     asset overrides.
 *
 * For full project webpack builds (SCSS, JS, images, vendor splitting),
 * use landing-fusion.config.js which extends projects/webpack/base.config.js.
 *
 * Loaded when FUSION_WEBPACK_WORKSPACE=landing or
 * FUSION_WEBPACK_WORKSPACE_PATH points here.
 *
 * Entry points:
 *   - fusion:   django-fusion base SCSS/JS (inherited from default)
 *   - landing:  landing-fusion-specific SCSS/JS entries
 *
 * Usage:
 *   cd libs/django-fusion
 *   FUSION_WEBPACK_WORKSPACE=landing \
 *     FUSION_WEBPACK_WORKSPACE_PATH=../../projects/landing-fusion/webpack/landing.js \
 *     FUSION_PROJECT_ROOT=../../projects/landing-fusion \
 *     npx webpack --config webpack.config.js
 */

const path = require("path");

// Resolve paths relative to this file's location
const LANDING_ROOT = process.env.FUSION_PROJECT_ROOT
  ? path.resolve(process.env.FUSION_PROJECT_ROOT)
  : path.resolve(__dirname, "..");

module.exports = {
  /** Additional entry points beyond the base "fusion" entry */
  entries: {
    landing: [
      path.join(LANDING_ROOT, "assets", "static", "styles", "main.scss"),
      path.join(LANDING_ROOT, "assets", "static", "js", "app.js"),
    ],
  },

  /** Output overrides */
  output: {
    path: path.join(LANDING_ROOT, "backend", "assets", "static", "bundles"),
    publicPath: "/static/bundles/",
  },

  /** Landing-specific resolve aliases */
  aliases: {
    "@landing-styles": path.join(LANDING_ROOT, "assets", "static", "styles"),
    "@landing-js": path.join(LANDING_ROOT, "assets", "static", "js"),
    "@landing-images": path.join(LANDING_ROOT, "assets", "static", "images"),
  },

  /** Additional plugins */
  plugins: [],

  /** Workspace metadata */
  metadata: {
    name: "landing",
    label: "Landing-Fusion Workspace",
    description: "Asset bundle for the landing-fusion Astro + Django/Wagtail site.",
    version: "1.0.0",
    project: "projects/landing-fusion/",
  },
};
