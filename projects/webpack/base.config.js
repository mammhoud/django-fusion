/**
 * Webpack Base Config Factory
 *
 * Shared foundation for all project webpack configs (landing-fusion, precis, etc.).
 * Replaces the legacy env-var-based main.config.js site dispatcher with explicit
 * per-project configuration.
 *
 * **Returns a function `(env, argv)`** — webpack calls it at build-time so
 * mode-dependent settings (isDev, hashing, minimization) use the actual CLI
 * flags, not require-time state.
 *
 * Usage in each project:
 *   const createConfig = require('../../webpack/base.config');
 *   module.exports = createConfig({
 *     name: 'landing-fusion',
 *     projectRoot: __dirname + '/..',
 *     entries: { landing: './assets/static/js/app.js' },
 *     aliases: { '@landing': './assets/static' },
 *     outputPath: './backend/assets/static/bundles',
 *   });
 *
 * Peer dependencies (must be installed in the project's own node_modules):
 *   webpack, webpack-merge, webpack-bundle-tracker, mini-css-extract-plugin,
 *   css-minimizer-webpack-plugin, terser-webpack-plugin, copy-webpack-plugin,
 *   babel-loader, @babel/core, @babel/preset-env, core-js,
 *   css-loader, postcss-loader, sass-loader, autoprefixer, vue-loader
 *
 * @param {Object} opts - Project configuration
 * @param {string} opts.name - Project name for logging
 * @param {string} opts.projectRoot - Absolute path to project root
 * @param {Object} [opts.entries] - Additional entry points (merged with common)
 * @param {string} [opts.outputPath] - Override output directory
 * @param {string} [opts.outputPublic] - Override publicPath (default: /static/bundles/)
 * @param {Object} [opts.aliases] - Additional resolve.alias entries
 * @param {string[]} [opts.scssIncludes] - Additional sass-loader includePaths
 * @param {Object[]} [opts.plugins] - Additional webpack plugins
 * @param {boolean} [opts.trackBundles=true] - Generate bundles.json via BundleTracker
 * @param {string} [opts.nodeModulesPath] - Path to node_modules (auto-resolved if omitted)
 * @returns {Function} Webpack config function (env, argv) => config object
 */

'use strict';

const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');

// Local-only require (not from node_modules — this file is in the same repo)
const commonConfig = require('./common.config');

// ─────────────────────────────────────────────────────────────────────────────
// Helper: resolve project-relative paths
// ─────────────────────────────────────────────────────────────────────────────
function resolveProject(projectRoot, maybePath) {
  if (!maybePath) return maybePath;
  if (path.isAbsolute(maybePath)) return maybePath;
  return path.resolve(projectRoot, maybePath);
}

function resolveAliases(projectRoot, aliases) {
  if (!aliases) return {};
  const resolved = {};
  for (const [k, v] of Object.entries(aliases)) {
    resolved[k] = resolveProject(projectRoot, v);
  }
  return resolved;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper: create a require() that resolves from the project's node_modules
// ─────────────────────────────────────────────────────────────────────────────
function createProjectRequire(nodeModulesPath) {
  // createRequire(filename) produces a require that resolves from filename's dir.
  // Give it a dummy file inside node_modules so require('webpack-merge') etc.
  // resolve from the project's dependency tree, not from projects/webpack/.
  const dummy = path.join(nodeModulesPath, '_fusion_webpack_resolve_.js');
  return createRequire(dummy);
}

// ─────────────────────────────────────────────────────────────────────────────
// Factory
// ─────────────────────────────────────────────────────────────────────────────
function createConfig(opts = {}) {
  const {
    name = 'project',
    projectRoot = path.resolve(__dirname, '..'),
    entries: extraEntries = {},
    outputPath = null,
    outputPublic = '/static/bundles/',
    aliases: extraAliases = {},
    scssIncludes: extraScssIncludes = [],
    plugins: extraPlugins = [],
    trackBundles = true,
    nodeModulesPath = null,
  } = opts;

  // Resolve node_modules — project-local only (each project has its own package.json)
  const resolvedNodeModules = nodeModulesPath
    ? path.resolve(nodeModulesPath)
    : path.join(projectRoot, 'node_modules');

  // Create a require function that resolves from the project's node_modules
  const req = createProjectRequire(resolvedNodeModules);

  // Lazy-load packages from the project's node_modules (not from projects/webpack/)
  const { merge } = req('webpack-merge');
  const MiniCssExtractPlugin = req('mini-css-extract-plugin');
  const TerserPlugin = req('terser-webpack-plugin');
  const CssMinimizerPlugin = req('css-minimizer-webpack-plugin');
  const CopyWebpackPlugin = req('copy-webpack-plugin');
  let BundleTracker = null;
  try {
    BundleTracker = req('webpack-bundle-tracker');
  } catch (_) {
    // Optional — skip if not installed
  }

  // Derive output path
  const derivedOutput = outputPath
    ? resolveProject(projectRoot, outputPath)
    : path.resolve(projectRoot, 'assets', 'bundles');

  console.log(`[webpack:${name}] Project root: ${projectRoot}`);
  console.log(`[webpack:${name}] Node modules: ${resolvedNodeModules}`);
  console.log(`[webpack:${name}] Output: ${derivedOutput}`);

  // ── Base entry points ─────────────────────────────────────────────────
  const baseEntries = {
    // Default entry from SCSS in assets/static/styles/main.scss
    ...(fs.existsSync(path.resolve(projectRoot, 'assets/static/styles/main.scss'))
      ? { main: path.resolve(projectRoot, 'assets/static/styles/main.scss') }
      : {}),
    // Default JS entry
    ...(fs.existsSync(path.resolve(projectRoot, 'assets/static/js/app.js'))
      ? { app: path.resolve(projectRoot, 'assets/static/js/app.js') }
      : {}),
  };

  // Resolve extra entry paths
  const resolvedEntries = {};
  for (const [entryName, entryFiles] of Object.entries(extraEntries)) {
    const files = Array.isArray(entryFiles) ? entryFiles : [entryFiles];
    resolvedEntries[entryName] = files.map(f => resolveProject(projectRoot, f));
  }

  // ── Resolve aliases ───────────────────────────────────────────────────
  const projectAliases = resolveAliases(projectRoot, extraAliases);

  // ── Return a FUNCTION so webpack calls us with (env, argv) ────────────
  //     This ensures mode-dependent settings (isDev, hashing, minimization)
  //     are computed at build-time using webpack's actual CLI flags, not at
  //     require-time when Node first loads the file.
  return (env, argv) => {
    const isDev = argv.mode === 'development';

    // ── Build plugins ───────────────────────────────────────────────────
    const plugins = [
      // BundleTracker for django-webpack-loader
      ...(trackBundles && BundleTracker
        ? [new BundleTracker({ path: derivedOutput, filename: 'bundles.json' })]
        : []),

      // Copy static assets from assets/static/libs
      ...(fs.existsSync(path.resolve(projectRoot, 'assets/static/libs'))
        ? [
            new CopyWebpackPlugin({
              patterns: [{
                from: path.resolve(projectRoot, 'assets/static/libs'),
                to: path.join(derivedOutput, 'libs'),
                noErrorOnMissing: true,
              }],
            }),
          ]
        : []),

      ...extraPlugins,
    ];

    // ── Merge with common config ────────────────────────────────────────
    return merge(commonConfig({ projectRoot, nodeModulesPath: resolvedNodeModules }), {
      name: name,
      mode: argv.mode || 'production',

      entry: {
        ...baseEntries,
        ...resolvedEntries,
      },

      output: {
        path: derivedOutput,
        publicPath: outputPublic,
        filename: isDev ? '[name].js' : '[name].[contenthash:8].js',
        chunkFilename: isDev ? '[id].js' : '[id].[contenthash:8].js',
        clean: !isDev,
      },

      plugins,

      resolve: {
        alias: {
          '@shared': path.resolve(projectRoot, 'assets', 'static'),
          '@assets': path.resolve(projectRoot, 'assets'),
          ...projectAliases,
        },
        modules: [
          resolvedNodeModules,
          'node_modules',
        ],
      },

      resolveLoader: {
        modules: [
          resolvedNodeModules,
          'node_modules',
        ],
      },

      optimization: {
        minimize: !isDev,
        runtimeChunk: 'single',
        minimizer: [
          new TerserPlugin({
            terserOptions: {
              compress: { drop_console: !isDev },
              format: { comments: false },
            },
            extractComments: false,
          }),
          new CssMinimizerPlugin(),
        ],
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendor',
              priority: 10,
              reuseExistingChunk: true,
            },
            common: {
              minChunks: 2,
              priority: 5,
              reuseExistingChunk: true,
              name: 'common',
            },
          },
        },
      },

      performance: {
        maxEntrypointSize: 1024 * 1024,  // 1 MB — large vendor bundles expected
        maxAssetSize: 512 * 1024,
        hints: 'warning',
      },
    });
  };
}

module.exports = createConfig;
