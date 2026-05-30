const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');
const { resolveAssetPaths } = require('./paths');

const assetPaths = resolveAssetPaths();
const assetsRequire = createRequire(path.join(assetPaths.assetsRoot, 'package.json'));
const webpack = assetsRequire('webpack');
const fse = assetsRequire('fs-extra');
const { VueLoaderPlugin } = assetsRequire('vue-loader');
const MiniCssExtractPlugin = assetsRequire('mini-css-extract-plugin');
const BundleTracker = assetsRequire('webpack-bundle-tracker');
const CopyWebpackPlugin = assetsRequire('copy-webpack-plugin');

const SITE_NAME = assetPaths.siteName;
const SITE_DIR = assetPaths.siteDir;
const SHARED_DIR = assetPaths.sharedStaticDir;
const SITE_STATIC_DIR = assetPaths.siteStaticDir;
const DIST_DIR = assetPaths.siteBundlesDir;
const SHARED_BUNDLES_DIR = assetPaths.sharedBundlesDir;

class SharedAssetCopyPlugin {
  apply(compiler) {
    compiler.hooks.afterEmit.tapPromise('SharedAssetCopyPlugin', async () => {
      const directories = ['js', 'fonts', 'images', 'videos'];
      await fse.ensureDir(SHARED_BUNDLES_DIR);
      await Promise.all(directories.map(async (directory) => {
        const source = path.join(SHARED_DIR, directory);
        const destination = path.join(SHARED_BUNDLES_DIR, directory);
        if (await fse.pathExists(source)) {
          await fse.copy(source, destination);
        }
      }));
    });
  }
}

function buildEntries() {
  const entries = {
    shared: path.join(SHARED_DIR, 'static'),
    shared_styles: path.join(SHARED_DIR, 'styles'),
  };
  const siteStyles = path.join(SITE_STATIC_DIR, 'styles', 'main.scss');
  const siteMain = path.join(SITE_STATIC_DIR, 'js', 'main.js');
  if (fs.existsSync(siteStyles)) {
    entries.site_styles = siteStyles;
  }
  if (fs.existsSync(siteMain)) {
    entries.site_main = siteMain;
  }
  return entries;
}

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  process.env.NODE_ENV = isProduction ? 'production' : 'development';

  return {
    target: 'web',
    context: SHARED_DIR,
    entry: buildEntries(),
    performance: { hints: false },
    plugins: [
      new webpack.ProvidePlugin({ $: 'jquery', jQuery: 'jquery', 'window.jQuery': 'jquery' }),
      new CopyWebpackPlugin({ patterns: [
        { from: path.join(SITE_STATIC_DIR, 'images'), to: path.join(DIST_DIR, 'images'), noErrorOnMissing: true },
        { from: path.join(SITE_STATIC_DIR, 'js'), to: path.join(DIST_DIR, 'js'), noErrorOnMissing: true },
      ]}),
      new SharedAssetCopyPlugin(),
      new BundleTracker({ path: DIST_DIR, filename: 'bundles.json' }),
      new MiniCssExtractPlugin({ filename: isProduction ? 'css/[name].[contenthash:8].min.css' : 'css/[name].min.css' }),
      new VueLoaderPlugin(),
    ],
    resolveLoader: {
      modules: [assetPaths.assetsNodeModules, 'node_modules'],
    },
    module: { rules: [
      { test: /\.(js|jsx)$/i, exclude: /node_modules/, use: 'babel-loader' },
      { test: /\.vue$/, loader: 'vue-loader' },
      { test: /\.html$/, use: 'html-loader' },
      { test: /\.css$/i, use: [MiniCssExtractPlugin.loader, { loader: 'css-loader', options: { url: false }}], sideEffects: true },
      { test: /\.scss$/i, use: [MiniCssExtractPlugin.loader, { loader: 'css-loader', options: { url: false }}, 'sass-loader'], sideEffects: true },
      { test: /\.(png|jpe?g|gif|svg|webp)$/i, type: 'asset/resource', generator: { filename: 'images/[name][ext]' } },
      { test: /\.(woff2?|eot|ttf|otf)$/i, type: 'asset/resource', generator: { filename: 'fonts/[name][ext]' } },
    ]},
    resolve: {
      extensions: ['.js', '.jsx', '.json', '.vue', '.scss', '.css'],
      alias: { shared: SHARED_DIR, site: SITE_STATIC_DIR },
      modules: [assetPaths.assetsNodeModules, 'node_modules'],
    },
  };
};
