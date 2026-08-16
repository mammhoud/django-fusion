/**
 * Per-project webpack config — CTC Research (`projects/precis/precis-ctc`).
 *
 * Extends `projects/webpack/base.config.js` (the `createConfig` factory) so the
 * CTC Research site builds its own bundles instead of relying on the deprecated
 * env-var site dispatcher in `main.config.js`.
 *
 * Entries are auto-detected by `base.config.js`:
 *   - assets/static/styles/main.scss  → `main` bundle (CSS)
 *   - assets/static/js/app.js         → `app` bundle (JS)
 *
 * Output lands in `projects/precis/precis-ctc/assets/bundles/precis-ctc/`
 * and is published under `/static/bundles/precis-ctc/`, matching the per-site
 * `BUNDLE_DIR_NAME` in `projects/precis/precis-ctc/backend/configs/base/assets.py`.
 *
 * Usage (from `projects/precis/precis-ctc/assets/`):
 *   npm ci --include=dev --legacy-peer-deps
 *   npx webpack --config ../../webpack/ctc-research.config.js --mode production
 */

'use strict';

const path = require('path');
const createConfig = require('./base.config');

module.exports = createConfig({
  name: 'precis-ctc',
  projectRoot: path.resolve(__dirname, '..', 'precis', 'lms-ctc'),
  outputPath: 'assets/bundles/precis-ctc',
  outputPublic: '/static/bundles/precis-ctc/',
  aliases: {
    '@ctc': 'assets/static/js',
  },
});
