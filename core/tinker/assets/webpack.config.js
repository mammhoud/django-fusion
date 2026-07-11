/**
 * Customizer Webpack Configuration
 *
 * Builds Bootstrap 5 + customizer SCSS/JS with RTL support.
 *
 * Entry points:
 *   app      – Bootstrap JS + customizer JS modules
 *   styles   – Bootstrap CSS + customizer SCSS (LTR + RTL via rtlcss)
 *
 * Output lands in: customizer/assets/bundles/
 */

'use strict';

const path = require('path');
const fs = require('fs');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const rtlcss = require('rtlcss');
const postcss = require('postcss');

// ─────────────────────────────────────────────────────────────
// Paths
// ─────────────────────────────────────────────────────────────
const ASSETS_DIR = __dirname;                                // customizer/assets/
const STATIC_DIR = path.join(ASSETS_DIR, 'static');           // customizer/assets/static/
const BUNDLES_DIR = path.join(ASSETS_DIR, 'bundles', 'customizer'); // customizer/assets/bundles/tinker/

// BundleTracker – optional: generates bundles.json manifest read by
// django-webpack-loader's {% render_bundle %} template tag.
let BundleTracker;
try {
  BundleTracker = require(require.resolve('webpack-bundle-tracker', {
    paths: [
      path.join(ASSETS_DIR, 'node_modules'),
      path.join(ASSETS_DIR, '..', 'assets', 'node_modules'),
    ],
  }));
} catch (_) {
  BundleTracker = null;
}

// ─────────────────────────────────────────────────────────────
// Custom plugin: generates an RTL-flipped copy of every CSS
// file emitted by MiniCssExtractPlugin.
// ─────────────────────────────────────────────────────────────
class RtlCssPlugin {
  apply(compiler) {
    compiler.hooks.afterCompile.tapPromise('RtlCssPlugin', async (compilation) => {
      const assets = compilation.getAssets();
      const cssAssets = assets.filter(a => a.name.endsWith('.css') && !a.name.endsWith('.rtl.css'));

      for (const asset of cssAssets) {
        const source = asset.source.source();
        try {
          const result = await postcss([rtlcss]).process(source, { from: asset.name });
          const rtlName = asset.name.replace(/\.css$/, '.rtl.css');
          compilation.emitAsset(rtlName, new compiler.webpack.sources.RawSource(result.css));
          console.log(`  🌐 RTL: ${rtlName}`);
        } catch (err) {
          console.warn(`  ⚠️  RTLCSS failed for ${asset.name}: ${err.message}`);
        }
      }
    });
  }
}

// ─────────────────────────────────────────────────────────────
// Config
// ─────────────────────────────────────────────────────────────
module.exports = (env, argv) => {
  const mode = argv.mode || 'production';
  const isDev = mode === 'development';

  console.log(`🚀  customizer | mode: ${mode}`);
  console.log(`📦  output: ${BUNDLES_DIR}/`);

  return {
    target: 'web',
    mode,
    context: ASSETS_DIR,

    entry: {
      // Bootstrap JS + customizer JS modules
      app: [
        path.join(STATIC_DIR, 'js', 'index.js'),
      ],
      // Bootstrap CSS + customizer SCSS
      styles: [
        path.join(STATIC_DIR, 'styles', 'main.scss'),
      ],
    },

    output: {
      path: BUNDLES_DIR,
      publicPath: '/static/tinker/',
      filename: isDev ? '[name].js' : '[name]-[contenthash:8].js',
      chunkFilename: isDev ? '[name].chunk.js' : '[name]-[contenthash:8].chunk.js',
      clean: !isDev,
    },

    resolve: {
      extensions: ['.js', '.jsx', '.json', '.scss', '.css'],
      modules: [
        path.join(ASSETS_DIR, 'node_modules'),
        path.join(ASSETS_DIR, '..', 'assets', 'node_modules'),
        'node_modules',
      ],
      alias: {
        '@styles': path.join(STATIC_DIR, 'styles'),
        '@js': path.join(STATIC_DIR, 'js'),
      },
    },

    module: {
      // Monaco Editor CDN loader uses AMD-style require() that webpack
      // shouldn't try to bundle — suppress the critical-dependency warnings.
      parser: {
        javascript: {
          exprContextCritical: false,
          wrappedContextCritical: false,
        },
      },
      rules: [
        // ── JavaScript / JSX ─────────────────────────────────
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: [
                ['@babel/preset-env', { modules: false, useBuiltIns: 'usage', corejs: 3 }],
              ],
              cacheDirectory: true,
            },
          },
        },

        // ── CSS / SCSS (from source files) ───────────────────
        {
          test: /\.(css|scss|sass)$/,
          exclude: /node_modules\/(?!(bootstrap)\/).*/,
          use: [
            MiniCssExtractPlugin.loader,
            {
              loader: 'css-loader',
              options: { sourceMap: isDev, importLoaders: 2 },
            },
            {
              loader: 'postcss-loader',
              options: {
                postcssOptions: {
                  plugins: [
                    'autoprefixer',
                  ],
                },
              },
            },
            'sass-loader',
          ],
        },

        // ── CSS from node_modules (no sass) ──────────────────
        {
          test: /\.css$/,
          include: /node_modules/,
          use: [
            MiniCssExtractPlugin.loader,
            { loader: 'css-loader', options: { sourceMap: false } },
          ],
        },

        // ── Images ───────────────────────────────────────────
        {
          test: /\.(png|jpe?g|gif|svg|webp)$/i,
          type: 'asset',
          parser: { dataUrlCondition: { maxSize: 8 * 1024 } },
          generator: { filename: 'images/[name]-[hash:8][ext]' },
        },

        // ── Fonts ────────────────────────────────────────────
        {
          test: /\.(woff2?|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: { filename: 'fonts/[name]-[hash:8][ext]' },
        },
      ],
    },

    plugins: [
      new MiniCssExtractPlugin({
        filename: isDev ? '[name].css' : '[name]-[contenthash:8].css',
        chunkFilename: isDev ? '[name].chunk.css' : '[name]-[contenthash:8].chunk.css',
      }),

      // Generate RTL copies of all CSS files
      new RtlCssPlugin(),

      // BundleTracker – generates bundles.json for django-webpack-loader
      ...(BundleTracker ? [new BundleTracker({
        path: BUNDLES_DIR,
        filename: 'bundles.json',
      })] : []),
    ],

    optimization: {
      minimize: !isDev,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: { drop_console: false },
            format: { comments: false },
          },
          extractComments: false,
        }),
        new CssMinimizerPlugin(),
      ],
      runtimeChunk: 'single',
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendor',
            priority: 10,
            reuseExistingChunk: true,
          },
        },
      },
    },

    devtool: isDev ? 'eval-source-map' : false,

    devServer: {
      static: BUNDLES_DIR,
      port: 5093,
      hot: true,
    },

    performance: {
      maxEntrypointSize: 1024 * 1024,
      maxAssetSize: 512 * 1024,
      hints: 'warning',
    },
  };
};
