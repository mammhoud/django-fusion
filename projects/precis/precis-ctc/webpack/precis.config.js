/**
 * Precis LMS Webpack Configuration
 *
 * Extends the shared @webpack/base.config.js factory.
 * Bundles project-specific SCSS/JS assets into versioned bundles consumed
 * by django-webpack-loader via {% render_bundle %} template tags.
 *
 * Build commands:
 *   # Development (watch mode)
 *   npx webpack --config webpack/precis.config.js --mode=development --watch
 *
 *   # Production
 *   npx webpack --config webpack/precis.config.js --mode=production
 *
 *   # Via the Makefile
 *   cd projects/precis && make build
 *
 * Output (shared monorepo tree, beside media):
 *   projects/assets/bundles/ctc-research/
 *   ├── app.[contenthash].js
 *   ├── main.[contenthash].css
 *   ├── vendor.[contenthash].js
 *   ├── bundles.json          ← consumed by django-webpack-loader
 *   └── libs/                 ← copied static libs
 *
 * The backend registers this dir in STATICFILES_DIRS under the
 * bundles/ctc-research/ namespace, so collectstatic copies it into STATIC_ROOT
 * and the shared Nginx proxy serves it at /static/bundles/ctc-research/.
 *
 * Template usage:
 *   {% load render_bundle from webpack_loader %}
 *   {% render_bundle 'main' 'css' %}
 *   {% render_bundle 'app' 'js' %}
 */

const path = require('path');
const createConfig = require('../../webpack/base.config');

const PROJECT_ROOT = path.resolve(__dirname, '..');

module.exports = createConfig({
  name: 'precis',

  projectRoot: PROJECT_ROOT,

  // ── Entry points ─────────────────────────────────────────────────────
  entries: {
    precis: [
      'assets/static/styles/main.scss',
      'assets/static/js/app.js',
    ],
  },

  // ── Output ───────────────────────────────────────────────────────────
  // Bundles land in the shared monorepo tree (projects/assets/bundles/ctc-research/,
  // beside projects/assets/media/ctc-research/) using the site's public identity
  // 'ctc-research' so the shared Nginx proxy can map them at
  // /static/bundles/ctc-research/ without renaming. The backend registers this
  // dir in STATICFILES_DIRS (see backend/settings.py) so collectstatic serves
  // them from STATIC_ROOT and WEBPACK_LOADER/FUSION_ASSET_PIPELINE find the
  // stats file at projects/assets/bundles/ctc-research/bundles.json.
  outputPath: '../../assets/bundles/ctc-research',
  outputPublic: '/static/bundles/ctc-research/',

  // ── Resolve aliases ──────────────────────────────────────────────────
  aliases: {
    '@precis': 'assets/static',
    '@precis-styles': 'assets/static/styles',
    '@precis-js': 'assets/static/js',
    '@precis-images': 'assets/static/images',
    '@lms': 'assets/static',         // legacy alias for backward compat
    // django-fusion integration
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
║  🏥 CTC Research Webpack                                    ║
║  Output: projects/assets/bundles/ctc-research/              ║
║  Public: /static/bundles/ctc-research/                      ║
║  django-webpack-loader → {% render_bundle 'precis' %}      ║
╚══════════════════════════════════════════════════════════════╝
`);
