/**
 * Precis LMS Webpack Workspace (for django-fusion webpack)
 *
 * ⚠️  This is a WORKSPACE CONFIG consumed by libs/django-fusion/webpack.config.js
 *     via FUSION_WEBPACK_WORKSPACE_PATH. It only defines django-fusion component
 *     asset overrides.
 *
 * For full project webpack builds (SCSS, JS, images, vendor splitting),
 * use precis.config.js which extends projects/webpack/base.config.js.
 *
 * Loaded when FUSION_WEBPACK_WORKSPACE=precis or
 * FUSION_WEBPACK_WORKSPACE_PATH points here.
 *
 * Entry points:
 *   - fusion:  django-fusion base SCSS/JS (inherited from default)
 *   - precis:  precis-specific SCSS/JS entries
 *
 * Usage:
 *   cd libs/django-fusion
 *   FUSION_WEBPACK_WORKSPACE=precis \
 *     FUSION_WEBPACK_WORKSPACE_PATH=../../projects/precis/webpack/precis.js \
 *     FUSION_PROJECT_ROOT=../../projects/precis \
 *     npx webpack --config webpack.config.js
 */

const path = require("path");

// Resolve paths relative to this file's location
const PRECIS_ROOT = process.env.FUSION_PROJECT_ROOT
  ? path.resolve(process.env.FUSION_PROJECT_ROOT)
  : path.resolve(__dirname, "..");

module.exports = {
  /** Additional entry points beyond the base "fusion" entry */
  entries: {
    precis: [
      path.join(PRECIS_ROOT, "assets", "static", "styles", "main.scss"),
      path.join(PRECIS_ROOT, "assets", "static", "js", "app.js"),
    ],
  },

  /** Output overrides */
  output: {
    path: path.join(PRECIS_ROOT, "assets", "static", "bundles"),
    publicPath: "/static/bundles/",
  },

  /** Precis-specific resolve aliases */
  aliases: {
    "@precis-styles": path.join(PRECIS_ROOT, "assets", "static", "styles"),
    "@precis-js": path.join(PRECIS_ROOT, "assets", "static", "js"),
    "@precis-images": path.join(PRECIS_ROOT, "assets", "static", "images"),
  },

  /** Additional plugins */
  plugins: [],

  /** Workspace metadata */
  metadata: {
    name: "precis",
    label: "Precis LMS Workspace",
    description: "Asset bundle for the Precis LMS Django/Wagtail site.",
    version: "1.0.0",
    project: "projects/precis/",
  },
};
