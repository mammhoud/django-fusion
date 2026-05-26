const path = require('path');
const webpack = require('webpack');
const { VueLoaderPlugin } = require('vue-loader');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { RawSource } = require('webpack-sources');
const BundleTracker = require('webpack-bundle-tracker');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const rtlcss = require('rtlcss');

// ── Path resolution ───────────────────────────────────────────────────────────
const PROJECT_PATH = process.env.PROJECT_PATH || 'ctc-research.com';
const WORKSPACE_ROOT = path.resolve(__dirname, '..');

// In Docker the app is at /app; shared assets are at /app/shared/assets/static/
const isDocker = process.env.RUNNING_ENV === 'docker';

// Per-site directory (only contains site-specific styles now)
const SITE_DIR = isDocker
  ? WORKSPACE_ROOT
  : path.resolve(__dirname, '..', PROJECT_PATH);

// Shared assets directory (fonts, images, js, videos, static.js, shared styles)
// Local dev: websites/assets/static/
// Docker:    /app/shared/assets/static/
const SHARED_DIR = isDocker
  ? path.join(WORKSPACE_ROOT, 'shared', 'assets', 'static')
  : path.join(WORKSPACE_ROOT, 'assets', 'static');

const paths = {
  // Site-specific static (only styles/ remains here)
  site: path.join(SITE_DIR, 'assets', 'static'),
  // Shared static (entry point, js, fonts, images, videos, shared styles)
  shared: SHARED_DIR,
  // Output
  dist: isDocker
    ? path.join(WORKSPACE_ROOT, 'assets', 'bundles')
    : path.join(WORKSPACE_ROOT, 'bundles', PROJECT_PATH),
};

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';

  if (isProduction) process.env.NODE_ENV = 'production';
  else process.env.NODE_ENV = 'development';

  return {
    target: 'web',

    // Context is the shared dir so static.js resolves its relative imports
    context: paths.shared,

    entry: {
      // Entry point lives in shared (websites/assets/static/static.js)
      static: path.join(paths.shared, 'static'),
    },

    performance: { hints: false },

    plugins: [
      new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
        'window.jQuery': 'jquery',
      }),

      new CopyWebpackPlugin({
        patterns: [
          // Copy shared js/ to dist
          {
            from: path.join(paths.shared, 'js'),
            to: path.join(paths.dist, 'js'),
            noErrorOnMissing: true,
          },
          // Copy shared libs/ to dist (if any)
          {
            from: path.join(paths.shared, 'libs'),
            to: path.join(paths.dist, 'libs'),
            noErrorOnMissing: true,
          },
          // Copy shared images/ to dist
          {
            from: path.join(paths.shared, 'images'),
            to: path.join(paths.dist, 'images'),
            noErrorOnMissing: true,
          },
          // Copy shared videos/ to dist
          {
            from: path.join(paths.shared, 'videos'),
            to: path.join(paths.dist, 'videos'),
            noErrorOnMissing: true,
          },
        ],
      }),

      new BundleTracker({
        path: paths.dist,
        filename: 'bundles.json',
      }),

      new MiniCssExtractPlugin({
        filename: isProduction ? 'css/[name].[contenthash:8].min.css' : 'css/[name].min.css',
        chunkFilename: isProduction ? 'css/[name].[contenthash:8].chunk.css' : 'css/[name].chunk.css',
      }),

      new VueLoaderPlugin(),
    ],

    module: {
      rules: [
        {
          test: /\.(js|jsx)$/i,
          exclude: /node_modules/,
          use: 'babel-loader',
        },
        {
          test: /\.vue$/,
          loader: 'vue-loader',
          options: { reactivityTransform: true },
        },
        {
          test: /\.html$/,
          use: 'html-loader',
        },
        {
          test: /\.s?css$/i,
          use: [
            MiniCssExtractPlugin.loader,
            'css-loader',
            { loader: 'postcss-loader', options: { postcssOptions: { plugins: [] } } },
            { loader: 'sass-loader' },
          ],
          sideEffects: true,
        },
        {
          test: /\.(png|jpe?g|gif|svg|webp)$/i,
          type: 'asset/resource',
          generator: { filename: 'images/[name][ext]' },
        },
        {
          test: /\.(woff2?|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: { filename: 'fonts/[name][ext]' },
        },
      ],
    },

    resolve: {
      extensions: ['.js', '.jsx', '.json', '.vue', '.scss', '.css'],
      alias: {
        // ~shared → websites/assets/static/ (shared styles, fonts, etc.)
        'shared': paths.shared,
        // ~site → per-site assets/static/ (site-specific styles)
        'site': paths.site,
      },
    },
  };
};
