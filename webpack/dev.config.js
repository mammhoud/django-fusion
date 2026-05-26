const path = require('path');
const webpack = require('webpack');
const { VueLoaderPlugin } = require('vue-loader');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { RawSource } = require('webpack-sources');
const BundleTracker = require('webpack-bundle-tracker');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const rtlcss = require('rtlcss');

// Base directory
const BASE_DIR = path.resolve(__dirname, '../');

// Define all paths
const paths = {
  assets: path.join(BASE_DIR, 'assets'),
  static: path.join(BASE_DIR, 'assets/static'),
  dist: path.join(BASE_DIR, 'assets/bundles'),
};

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';

  return {
    target: 'web',
    context: BASE_DIR,

    entry: {
      static: path.join(paths.static, 'static'),
      // Uncomment if needed:
      // bottom: path.join(paths.static, 'scripts'),
      // icons: path.join(paths.static, 'scss/icons.scss'),
    },

    performance: {
      hints: false,
    },

    plugins: [
      new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
        'window.jQuery': 'jquery',
      }),

      new CopyWebpackPlugin({
        patterns: [
          {
            from: path.join(paths.static, 'js'),
            to: path.join(paths.dist, 'js'),
            noErrorOnMissing: true,
          },
          {
            from: path.join(paths.static, 'libs'),
            to: path.join(paths.dist, 'libs'),
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
          options: {
            reactivityTransform: true,
          },
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
            {
              loader: 'postcss-loader',
              options: {
                postcssOptions: {
                  plugins: [
                    'postcss-import',
                    // 'tailwindcss/nesting',
                    // 'tailwindcss',
                    'autoprefixer',
                    'postcss-preset-env',
                    ...(isProduction ? [
                      ['@fullhuman/postcss-purgecss', {
                        content: [
                          './assets/static/**/*.{html,js,vue}',
                          './templates/**/*.html',
                          './**/*.py',
                        ],
                        defaultExtractor: (content) => {
                          return content.match(/[\w-/:]+(?<!:)/g) || [];
                        },
                        safelist: {
                          standard: [/^bg-/, /^text-/, /^border-/],
                          deep: [/^vue/, /^v-/],
                        }
                      }]
                    ] : [])
                  ],
                },
              },
            },
            'sass-loader',
          ],
          sideEffects: true,
        },
        {
          test: /\.(png|jpe?g|gif|svg|webp)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'images/[name][ext]',
          },
        },
        {
          test: /\.(woff2?|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'fonts/[name][ext]',
          },
        },
      ],
    },

    resolve: {
      extensions: ['.js', '.jsx', '.json', '.vue', '.scss', '.css'],
      alias: {
        '@*': paths.dist,
        'static': paths.static,
      },
    },
  };
};