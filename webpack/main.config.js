/**
 * Webpack Main Configuration
 * Unified entry point for all 3 workspace sites.
 *
 * Site entry files are all named app.js:
 *   ctc-research/assets/static/js/app.js
 *   lms-demo/assets/static/js/app.js
 *   VResume/assets/static/js/app.js
 *
 * Shared core bundle:
 *   assets/static/js/core/main.js
 */

'use strict';

const path = require('path');

// Resolve webpack-merge and webpack-bundle-tracker from the assets node_modules tree
const nodeModulesDir = path.join(__dirname, '../assets/node_modules');
const { merge } = require(require.resolve('webpack-merge', { paths: [nodeModulesDir] }));
let BundleTracker;
try {
  BundleTracker = require(require.resolve('webpack-bundle-tracker', { paths: [nodeModulesDir] }));
} catch (_) {
  BundleTracker = null; // optional — skip if not installed
}

const commonConfig = require('./common.config.js');

// ─────────────────────────────────────────────────────────────────────────────
// Site directory map  (alias key → real directory name)
// ─────────────────────────────────────────────────────────────────────────────
const SITE_DIR_MAP = {
  'ctc-research':     'ctc-research',
  ctc:                'ctc-research',
  'ctc-research.com': 'ctc-research',
  'lms-demo':         'lms-demo',
  lms:                'lms-demo',
  structa:            'lms-demo',
  'structa.cloud':    'lms-demo',
  vresume:            'VResume',
  VResume:            'VResume',
  resume:             'VResume',
  'vresume.structa.cloud': 'VResume',
};

// ─────────────────────────────────────────────────────────────────────────────
module.exports = (env = {}, argv = {}) => {
  const site        = process.env.PROJECT_PATH || process.env.DJANGO_SITE || env.site || 'ctc-research';
  const siteDir     = SITE_DIR_MAP[site] || site;
  const mode        = argv.mode || process.env.NODE_ENV || 'production';
  const isDev       = mode === 'development';
  const workspaceRoot = path.resolve(__dirname, '..');  // webpack/ → project root

  // ── Entry points ───────────────────────────────────────────────────────────
  // VResume has its own self-contained core/main.js + static.js bootstrap.
  // CTC-Research and LMS-Demo use the shared core/main.js + their own app.js.
  //
  // The "static" entry produces:
  //   static-[hash].css  ← vendor CSS + site SCSS (MiniCssExtractPlugin)
  //   static-[hash].js   ← tiny runtime shim
  // Templates reference it via:  {% render_bundle 'static' 'css' %}
  //                               {% render_bundle 'static' 'js' %}
  const SITE_ENTRIES = {
    'ctc-research': path.resolve(workspaceRoot, 'ctc-research/assets/static/js/app.js'),
    'lms-demo':     path.resolve(workspaceRoot, 'lms-demo/assets/static/js/app.js'),
    'VResume':      path.resolve(workspaceRoot, 'VResume/assets/static/js/app.js'),
  };

  // Static (CSS + vendor) entry — each site provides its own static.js
  const STATIC_ENTRIES = {
    'ctc-research': path.resolve(workspaceRoot, 'ctc-research/assets/static/js/static.js'),
    'lms-demo':     path.resolve(workspaceRoot, 'lms-demo/assets/static/js/static.js'),
    'VResume':      path.resolve(workspaceRoot, 'VResume/assets/static/js/static.js'),
  };

  const isVResume   = siteDir === 'VResume';
  const sharedEntry = isVResume ? {} : {
    main: path.resolve(workspaceRoot, 'assets/static/js/core/main.js'),
  };

  // Include static entry when the file exists for this site
  const staticEntryPath = STATIC_ENTRIES[siteDir] || path.resolve(workspaceRoot, `${siteDir}/assets/static/js/static.js`);
  const fs = require('fs');
  const staticEntry = fs.existsSync(staticEntryPath) ? { static: staticEntryPath } : {};

  const siteEntry = {
    app: SITE_ENTRIES[siteDir] || path.resolve(workspaceRoot, `${siteDir}/assets/static/js/app.js`),
  };

  console.log(`🚀  ${siteDir} | mode: ${mode}`);
  console.log(`📦  output: /static/bundles/${siteDir}/`);

  // ── Output path ────────────────────────────────────────────────────────────
  // Site-specific bundles land in:
  //   ctc-research/assets/bundles/ctc-research/
  //   lms-demo/assets/bundles/lms-demo/
  //   VResume/assets/bundles/vresume/
  const outputDir = siteDir === 'VResume'
    ? path.resolve(workspaceRoot, 'VResume', 'assets', 'bundles', 'vresume')
    : path.resolve(workspaceRoot, siteDir, 'assets', 'bundles', siteDir);

  return merge(commonConfig, {
    mode,
    entry: { ...sharedEntry, ...staticEntry, ...siteEntry },

    output: {
      path:          outputDir,
      publicPath:    `/static/bundles/${siteDir === 'VResume' ? 'vresume' : siteDir}/`,
      filename:      '[name]-[contenthash:8].js',
      chunkFilename: 'chunk-[name]-[contenthash:8].js',
      clean:         !isDev,
    },

    plugins: BundleTracker ? [
      new BundleTracker({
        path:     outputDir,
        filename: 'bundles.json',
      }),
    ] : [],

    resolve: {
      extensions: ['.js', '.jsx', '.vue', '.json'],
      // Always look in assets/node_modules so cross-directory imports resolve
      modules: [
        path.resolve(workspaceRoot, 'assets/node_modules'),
        'node_modules',
      ],
      alias: {
        // Shared utility layer  (@utility / @base both resolve here)
        '@utility':  path.resolve(workspaceRoot, 'assets/static/js/utility'),
        '@base':     path.resolve(workspaceRoot, 'assets/static/js/utility'),
        // VResume uses 'shared/js/utility/' — point it to the same place
        'shared/js/utility': path.resolve(workspaceRoot, 'assets/static/js/utility'),
        'shared/js':         path.resolve(workspaceRoot, 'assets/static/js'),
        // Theme system
        '@theme':    path.resolve(workspaceRoot, 'assets/static/js/theme'),
        '@layouts':  path.resolve(workspaceRoot, 'assets/static/js/theme/layouts'),
        '@usecases': path.resolve(workspaceRoot, 'assets/static/js/theme/usecases'),
        // Feature modules
        '@modules':  path.resolve(workspaceRoot, 'assets/static/js/modules'),
        '@plugins':  path.resolve(workspaceRoot, 'assets/static/js/plugins'),
        // Core bootstrap
        '@core':     path.resolve(workspaceRoot, 'assets/static/js/core'),
        '@htmx':     path.resolve(workspaceRoot, 'assets/static/js/core/htmx-bridge'),
        // Per-site shortcuts (override shared modules with site-level files)
        '@ctc':      path.resolve(workspaceRoot, 'ctc-research/assets/static/js'),
        '@lms':      path.resolve(workspaceRoot, 'lms-demo/assets/static/js'),
        '@vresume':  path.resolve(workspaceRoot, 'VResume/assets/static/js'),
      },
    },

    devtool: isDev ? 'eval-source-map' : false,

    resolveLoader: {
      modules: [
        path.resolve(workspaceRoot, 'assets/node_modules'),
        'node_modules',
      ],
    },
  });
};
