/**
 * Per-project webpack config — CTC Research (`projects/precis/ctc-research`).
 *
 * Extends `projects/webpack/base.config.js` (the `createConfig` factory) so the
 * CTC Research site builds its own bundles instead of relying on the deprecated
 * env-var site dispatcher in `main.config.js`.
 *
 * Entries are auto-detected by `base.config.js`:
 *   - assets/static/styles/main.scss  → `main` bundle (CSS)
 *   - assets/static/js/app.js         → `app` bundle (JS)
 *
 * Output lands in `projects/precis/ctc-research/assets/bundles/ctc-research/`
 * and is published under `/static/bundles/ctc-research/`, matching the per-site
 * `BUNDLE_DIR_NAME` in `projects/precis/ctc-research/backend/configs/base/assets.py`.
 *
 * Usage (from `projects/precis/ctc-research/assets/`):
 *   npm ci --include=dev --legacy-peer-deps
 *   npx webpack --config ../../webpack/ctc-research.config.js --mode production
 */

'use strict';

const path = require('path');
const createConfig = require('./base.config');

module.exports = createConfig({
  name: 'ctc-research',
  projectRoot: path.resolve(__dirname, '..', 'precis', 'ctc-research'),
  outputPath: 'assets/bundles/ctc-research',
  outputPublic: '/static/bundles/ctc-research/',
  aliases: {
    '@ctc': 'assets/static/js',
  },
});
