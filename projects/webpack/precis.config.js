/**
 * Per-project webpack config — Precis LMS (`projects/structa.cloud`).
 *
 * Extends `projects/webpack/base.config.js` (the `createConfig` factory) so the
 * Precis site builds its own bundles instead of relying on the deprecated
 * env-var site dispatcher in `main.config.js`.
 *
 * Entries are auto-detected by `base.config.js`:
 *   - assets/static/styles/main.scss  → `main` bundle (CSS)
 *   - assets/static/js/app.js         → `app` bundle (JS)
 *
 * Output lands in `projects/structa.cloud/assets/bundles/main/` and is published
 * under `/static/bundles/main/`, matching the per-site `BUNDLE_DIR_NAME` in
 * `projects/precis/configs/base/assets.py`.
 *
 * Usage (from `projects/structa.cloud/assets/`):
 *   npm ci --include=dev --legacy-peer-deps
 *   npx webpack --config ../../webpack/precis.config.js --mode production
 */

'use strict';

const path = require('path');
const createConfig = require('./base.config');

module.exports = createConfig({
  name: 'precis',
  projectRoot: path.resolve(__dirname, '..', 'precis', 'precis-main'),
  outputPath: 'assets/bundles/main',
  outputPublic: '/static/bundles/main/',
  aliases: {
    '@lms': 'assets/static/js',
  },
});
