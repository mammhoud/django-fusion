/**
 * Webpack Common Configuration — shared loaders, rules, and plugins.
 *
 * Used by base.config.js as the foundation all project configs extend.
 * Accepts { projectRoot, nodeModulesPath } so each project can resolve
 * its own dependencies via module.createRequire.
 *
 * @param {Object} opts
 * @param {string} opts.projectRoot - Absolute path to the project root
 * @param {string} opts.nodeModulesPath - Path to node_modules to use
 */

'use strict';

const path = require('path');
const { createRequire } = require('module');

function commonConfig({ projectRoot, nodeModulesPath } = {}) {
  const root = projectRoot || path.resolve(__dirname, '..');
  const nm = nodeModulesPath || path.resolve(root, 'node_modules');

  // Resolve from the project's node_modules, not from projects/webpack/
  const req = createRequire(path.join(nm, '_fusion_webpack_resolve_.js'));
  const MiniCssExtractPlugin = req('mini-css-extract-plugin');

  // Project-local resolve aliases are set in base.config.js (merge-safe).

  return {

    module: {
      rules: [
        // ── JavaScript / JSX ────────────────────────────────────────────
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: require.resolve('babel-loader', { paths: [nm] }),
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

        // ── CSS / SCSS / Sass ───────────────────────────────────────────
        {
          test: /\.(css|scss|sass)$/,
          exclude: /node_modules/,
          use: [
            MiniCssExtractPlugin.loader,
            {
              loader: require.resolve('css-loader', { paths: [nm] }),
              options: { sourceMap: true, importLoaders: 2 },
            },
            {
              loader: require.resolve('postcss-loader', { paths: [nm] }),
              options: {
                postcssOptions: {
                  plugins: ['autoprefixer'],
                },
              },
            },
            {
              loader: require.resolve('sass-loader', { paths: [nm] }),
              options: {
                sassOptions: {
                  silenceDeprecations: ['import'],
                  includePaths: [
                    path.resolve(root, 'assets', 'static', 'styles'),
                    path.resolve(root, 'node_modules'),
                  ],
                },
              },
            },
          ],
        },

        // ── CSS from node_modules (no sass/postcss) ─────────────────────
        {
          test: /\.css$/,
          include: /node_modules/,
          use: [
            MiniCssExtractPlugin.loader,
            {
              loader: require.resolve('css-loader', { paths: [nm] }),
              options: { sourceMap: false },
            },
          ],
        },

        // ── TypeScript (for vendored TS packages) ───────────────────────
        {
          test: /\.tsx?$/,
          include: /node_modules/,
          use: {
            loader: require.resolve('babel-loader', { paths: [nm] }),
            options: {
              presets: [require.resolve('@babel/preset-env', { paths: [nm] })],
            },
          },
        },

        // ── Vue SFC ─────────────────────────────────────────────────────
        {
          test: /\.vue$/,
          use: require.resolve('vue-loader', { paths: [nm] }),
        },

        // ── Images ──────────────────────────────────────────────────────
        {
          test: /\.(png|jpe?g|gif|svg|webp)$/i,
          type: 'asset',
          parser: { dataUrlCondition: { maxSize: 8 * 1024 } },
          generator: { filename: 'images/[name]-[hash:8][ext]' },
        },

        // ── Fonts ───────────────────────────────────────────────────────
        {
          test: /\.(woff2?|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: { filename: 'fonts/[name]-[hash:8][ext]' },
        },
      ],
    },

    plugins: [
      new MiniCssExtractPlugin({
        filename: '[name]-[contenthash:8].css',
        chunkFilename: 'chunk-[name]-[contenthash:8].css',
      }),
    ],
  };
}

module.exports = commonConfig;
