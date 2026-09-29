/**
 * Default Webpack Workspace
 *
 * Standard fusion asset entries and output configuration.
 * This is the fallback workspace used when no FUSION_WEBPACK_WORKSPACE
 * env var is set.
 *
 * Entry points:
 *   - fusion: Main fusion bundle (SCSS + JS for all sites)
 *
 * Output:
 *   - Bundles go to static/bundles/
 *   - Stats file: webpack-stats.json
 */

const path = require("path");

// This file lives in webpack/workspaces/, so the library root is two levels up.
const ROOT_DIR = path.resolve(__dirname, "..", "..");
const SRC_DIR = path.resolve(ROOT_DIR, "src");

module.exports = {
  /** Webpack entry points for this workspace */
  entries: {
    fusion: [
      path.join(SRC_DIR, "django_fusion", "assets", "entry.js"),
    ],
  },

  /** Output path overrides (relative to django-fusion root) */
  output: {
    path: path.resolve(ROOT_DIR, "static", "bundles"),
    publicPath: "/static/bundles/",
    filename: "js/[name].[contenthash:8].js",
    chunkFilename: "js/[name].[contenthash:8].chunk.js",
  },

  /** Additional webpack plugins for this workspace */
  plugins: [],

  /** Workspace metadata exposed via the /api/fusion/assets/ endpoint */
  metadata: {
    name: "default",
    label: "Default Fusion Workspace",
    description:
      "Standard fusion asset bundle for all django-fusion sites.",
    version: "1.0.0",
  },
};
