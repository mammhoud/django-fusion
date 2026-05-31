const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const CopyWebpackPlugin = require('copy-webpack-plugin');

// ── Paths ─────────────────────────────────────────────────────────────────────
const BASE_DIR = path.resolve(__dirname, '../');

const paths = {
  assets: path.join(BASE_DIR, 'assets'),
  static: path.join(BASE_DIR, 'assets/static'),
  dist:   path.join(BASE_DIR, 'assets/bundles'),
};

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  process.env.NODE_ENV = isProduction ? 'production' : 'development';

  return {
    target: 'web',
    context: BASE_DIR,

    entry: {
      // Bootstrap + jQuery — admin / non-vResume pages
      static: path.join(paths.static, 'static'),
      // Tailwind + Preline + vResume design system — portfolio pages
      styles: path.join(paths.static, 'styles'),
    },

    performance: { hints: false },

    plugins: [
      // Expose jQuery globally (Bootstrap needs it)
      new webpack.ProvidePlugin({
        $:               'jquery',
        jQuery:          'jquery',
        'window.jQuery': 'jquery',
      }),

      // Copy raw assets straight into bundles/
      new CopyWebpackPlugin({
        patterns: [
          { from: path.join(paths.static, 'js'),    to: path.join(paths.dist, 'js'),    noErrorOnMissing: true },
          { from: path.join(paths.static, 'libs'),  to: path.join(paths.dist, 'libs'),  noErrorOnMissing: true },
          { from: path.join(paths.static, 'images'),to: path.join(paths.dist, 'images'),noErrorOnMissing: true },
          { from: path.join(BASE_DIR, 'node_modules/bootstrap-icons/font/fonts'), to: path.join(paths.dist, 'fonts'), noErrorOnMissing: true },
        ],
      }),

      // Emit bundles.json — consumed by django-webpack-loader
      new BundleTracker({
        path:     paths.dist,
        filename: 'bundles.json',
      }),

      // Extract CSS into separate files so Django can serve them
      new MiniCssExtractPlugin({
        filename:      isProduction ? 'css/[name].[contenthash:8].min.css' : 'css/[name].min.css',
        chunkFilename: isProduction ? 'css/[id].[contenthash:8].chunk.css' : 'css/[id].chunk.css',
      }),
    ],

    module: {
      rules: [
        // ── JavaScript ──────────────────────────────────────────────────────
        {
          test: /\.(js|jsx)$/i,
          exclude: /node_modules/,
          use: 'babel-loader',
        },

        // ── HTML ────────────────────────────────────────────────────────────
        {
          test: /\.html$/,
          use: 'html-loader',
        },

        // ── CSS (plain — node_modules + local .css files) ───────────────────
        // Separate rule so .css files are NOT passed through sass-loader.
        // url: false → don't try to resolve font/image URLs inside CSS;
        // those files are served statically by Django / collectstatic.
        {
          test: /\.css$/i,
          use: [
            MiniCssExtractPlugin.loader,
            {
              loader: 'css-loader',
              options: {
                sourceMap: !isProduction,
                url: false,   // let Django serve font/image assets referenced in CSS
              },
            },
          ],
          sideEffects: true,
        },

        // ── SCSS (project source files) ─────────────────────────────────────
        {
          test: /\.scss$/i,
          use: [
            MiniCssExtractPlugin.loader,
            {
              loader: 'css-loader',
              options: {
                sourceMap: !isProduction,
                url: false,   // same as above — font paths resolved by Django
              },
            },
            {
              loader: 'sass-loader',
              options: {
                sourceMap: !isProduction,
                sassOptions: {
                  includePaths: [
                    path.join(BASE_DIR, 'node_modules'),
                    path.join(paths.static, 'styles'),
                  ],
                  quietDeps: true,   // silence deprecation warnings from deps
                },
              },
            },
          ],
          sideEffects: true,
        },

        // ── Images ──────────────────────────────────────────────────────────
        {
          test: /\.(png|jpe?g|gif|svg|webp)$/i,
          type: 'asset/resource',
          generator: { filename: 'images/[name][ext]' },
        },

        // ── Fonts ───────────────────────────────────────────────────────────
        {
          test: /\.(woff2?|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: { filename: 'fonts/[name][ext]' },
        },
      ],
    },

    resolve: {
      extensions: ['.js', '.jsx', '.json', '.scss', '.css'],
      alias: {
        '@':           paths.dist,
        '@static':     paths.static,
        '@js':         path.join(paths.static, 'js'),
        '@styles':     path.join(paths.static, 'styles'),
        '@components': path.join(paths.static, 'js/modules/components'),
        '@handlers':   path.join(paths.static, 'js/modules/handlers'),
        '@utils':      path.join(paths.static, 'js/utility'),
        '@modules':    path.join(paths.static, 'js/modules'),
        'bootstrap':   'bootstrap',
        'jquery':      'jquery',
        'htmx':        'htmx.org',
        'alpinejs':    'alpinejs',
        'preline':     'preline',
      },
    },
  };
};
