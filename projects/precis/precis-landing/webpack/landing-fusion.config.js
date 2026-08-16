/**
 * Landing-Fusion Webpack Configuration
 *
 * Extends the shared @webpack/base.config.js factory.
 * Bundles project-specific SCSS/JS assets into versioned bundles consumed
 * by django-webpack-loader via {% render_bundle %} template tags.
 *
 * Build commands:
 *   # Development (watch mode)
 *   npx webpack --config webpack/precis-landing.config.js --mode=development --watch
 *
 *   # Production
 *   npx webpack --config webpack/precis-landing.config.js --mode=production
 *
 *   # Via the Makefile
 *   make build
 *
 * Output:
 *   backend/assets/static/bundles/
 *   ├── app.[contenthash].js
 *   ├── main.[contenthash].css
 *   ├── vendor.[contenthash].js
 *   ├── bundles.json          ← consumed by django-webpack-loader
 *   └── libs/                 ← copied static libs
 */

const path = require('path');
const createConfig = require('../../webpack/base.config');

const PROJECT_ROOT = path.resolve(__dirname, '..');

module.exports = createConfig({
  name: 'precis-landing',

  projectRoot: PROJECT_ROOT,

  // ── Entry points ─────────────────────────────────────────────────────
  entries: {
    landing: [
      'assets/styles/_index.scss',
      'assets/static/js/app.js',
    ],
  },

  // ── Output ───────────────────────────────────────────────────────────
  outputPath: 'backend/assets/static/bundles',
  outputPublic: '/static/bundles/',

  // ── Resolve aliases ──────────────────────────────────────────────────
  aliases: {
    '@landing': 'assets/static',
    '@landing-styles': 'assets/static/styles',
    '@landing-js': 'assets/static/js',
    '@landing-images': 'assets/static/images',
    // django-fusion integration (when fusion bundles are consumed)
    '@fusion': path.resolve(PROJECT_ROOT, '../../libs/django-fusion/src/django_fusion/assets'),
  },

  // ── Additional SCSS include paths ────────────────────────────────────
  scssIncludes: [
    'assets/static/styles',
    '../../libs/django-fusion/src/django_fusion/assets',
  ],
});

// ── Console summary ────────────────────────────────────────────────────────
console.log(`
╔══════════════════════════════════════════════════════════════╗
║  🌐 Landing-Fusion Webpack                                  ║
║  Output: backend/assets/static/bundles/                     ║
║  Public: /static/bundles/                                   ║
║  django-webpack-loader → {% render_bundle 'landing' %}      ║
╚══════════════════════════════════════════════════════════════╝
`);
