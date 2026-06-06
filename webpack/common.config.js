/**
 * Webpack Common Configuration — shared rules + optimisation for all 3 sites.
 * Required plugins are resolved from assets/node_modules.
 */

'use strict';

const path = require('path');

// Resolve all plugins from the assets node_modules so they work when
// webpack is run with --prefix assets / cwd=assets
const nm = path.join(__dirname, '../assets/node_modules');
const workspaceRoot = path.resolve(__dirname, '..');
// Canonical site entry filenames consumed by webpack/main.config.js: ctc-app.js, lms-app.js, vresume-app.js

const MiniCssExtractPlugin = require(require.resolve('mini-css-extract-plugin',     { paths: [nm] }));
const CssMinimizerPlugin   = require(require.resolve('css-minimizer-webpack-plugin', { paths: [nm] }));
const TerserPlugin         = require(require.resolve('terser-webpack-plugin',        { paths: [nm] }));

module.exports = {
  resolve: {
    alias: {
      '@base': path.resolve(workspaceRoot, 'assets/static/js/base'),
      '@utility': path.resolve(workspaceRoot, 'assets/static/js/utility'),
    },
  },
  module: {
    rules: [
      // ── JavaScript / JSX ───────────────────────────────────────────────────
      {
        test:    /\.(js|jsx)$/,
        // Exclude node_modules AND VResume pre-compiled component files
        // (those files already have core-js polyfills injected by a prior Babel pass)
        exclude: [
          /node_modules/,
          /VResume[\\/]assets[\\/]static[\\/]js[\\/]components/,
        ],
        use: {
          loader:  require.resolve('babel-loader', { paths: [nm] }),
          options: {
            presets: [
              [
                require.resolve('@babel/preset-env', { paths: [nm] }),
                { modules: false, useBuiltIns: 'usage', corejs: 3 },
              ],
            ],
            cacheDirectory: true,
          },
        },
      },
      // ── VResume pre-compiled components (no babel transform, just bundle) ──
      {
        test:    /\.(js|jsx)$/,
        include: /VResume[\\/]assets[\\/]static[\\/]js[\\/]components/,
        use: {
          loader:  require.resolve('babel-loader', { paths: [nm] }),
          options: {
            // No useBuiltIns — polyfills are already in the file
            presets: [
              [require.resolve('@babel/preset-env', { paths: [nm] }), { modules: false }],
            ],
            cacheDirectory: true,
          },
        },
      },

      // ── CSS / SCSS ─────────────────────────────────────────────────────────
      {
        test: /\.(css|scss|sass)$/,
        exclude: /node_modules\/(?!(your-package)\/).*/,  // allow node_modules CSS
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader:  require.resolve('css-loader', { paths: [nm] }),
            options: { sourceMap: true, importLoaders: 2 },
          },
          {
            loader:  require.resolve('postcss-loader', { paths: [nm] }),
            options: {
              postcssOptions: {
                plugins: ['autoprefixer'],
              },
            },
          },
          require.resolve('sass-loader', { paths: [nm] }),
        ],
      },
      // ── CSS from node_modules (no sass/postcss processing) ──────────────────
      {
        test: /\.css$/,
        include: /node_modules/,
        use: [
          MiniCssExtractPlugin.loader,
          { loader: require.resolve('css-loader', { paths: [nm] }), options: { sourceMap: false } },
        ],
      },
      // ── TypeScript (for preline and similar packages) ───────────────────────
      {
        test: /\.tsx?$/,
        include: /node_modules/,
        use: {
          loader: require.resolve('babel-loader', { paths: [nm] }),
          options: { presets: [require.resolve('@babel/preset-env', { paths: [nm] })] },
        },
      },

      // ── Vue SFC ────────────────────────────────────────────────────────────
      {
        test: /\.vue$/,
        use:  require.resolve('vue-loader', { paths: [nm] }),
      },

      // ── Images ─────────────────────────────────────────────────────────────
      {
        test:   /\.(png|jpe?g|gif|svg|webp)$/i,
        type:   'asset',
        parser: { dataUrlCondition: { maxSize: 8 * 1024 } },
        generator: { filename: 'images/[name]-[hash:8][ext]' },
      },

      // ── Fonts ──────────────────────────────────────────────────────────────
      {
        test:      /\.(woff2?|eot|ttf|otf)$/i,
        type:      'asset/resource',
        generator: { filename: 'fonts/[name]-[hash:8][ext]' },
      },
    ],
  },

  plugins: [
    new MiniCssExtractPlugin({
      filename:      '[name]-[contenthash:8].css',
      chunkFilename: 'chunk-[name]-[contenthash:8].css',
    }),
  ],

  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress:  { drop_console: false },
          format:    { comments: false },
        },
        extractComments: false,
      }),
      new CssMinimizerPlugin(),
    ],
    runtimeChunk: 'single',
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        // All node_modules → vendor chunk
        vendor: {
          test:               /[\\/]node_modules[\\/]/,
          name:               'vendor',
          priority:           10,
          reuseExistingChunk: true,
        },
        // Shared code used by ≥2 entry points → common chunk
        common: {
          minChunks:          2,
          priority:           5,
          reuseExistingChunk: true,
          name:               'common',
        },
      },
    },
  },

  performance: {
    maxEntrypointSize: 1024 * 1024,   // 1 MB — large vendor bundles expected
    maxAssetSize:       512 * 1024,
    hints:             'warning',
  },
};
