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
 * Output:
 *   assets/bundles/
 *   ├── app.[contenthash].js
 *   ├── main.[contenthash].css
 *   ├── vendor.[contenthash].js
 *   ├── bundles.json          ← consumed by django-webpack-loader
 *   └── libs/                 ← copied static libs
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
  // The backend pipeline (configs/base/assets.py) computes SITE_NAME from
  // BASE_DIR.name = 'precis' and expects bundles under
  // assets/bundles/<site-name>/ so collectstatic serves them at
  // /static/bundles/precis/* and WEBPACK_LOADER/FUSION_ASSET_PIPELINE find
  // their stats file at assets/bundles/precis/bundles.json.
  outputPath: 'assets/bundles/precis',
  outputPublic: '/static/bundles/precis/',

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
║  📚 Precis LMS Webpack                                      ║
║  Output: assets/bundles/                                    ║
║  Public: /static/bundles/                                   ║
║  django-webpack-loader → {% render_bundle 'precis' %}      ║
╚══════════════════════════════════════════════════════════════╝
`);
