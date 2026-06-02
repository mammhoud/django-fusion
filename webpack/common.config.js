const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');
const { resolveAssetPaths } = require('./paths');

let assetPaths = resolveAssetPaths(process.env.PROJECT_PATH);
const assetsRequire = createRequire(path.join(assetPaths.assetsRoot, 'package.json'));
const webpack = assetsRequire('webpack');
const fse = assetsRequire('fs-extra');
const { VueLoaderPlugin } = assetsRequire('vue-loader');
const MiniCssExtractPlugin = assetsRequire('mini-css-extract-plugin');
const BundleTracker = assetsRequire('webpack-bundle-tracker');
const CopyWebpackPlugin = assetsRequire('copy-webpack-plugin');

class SharedAssetCopyPlugin {
  constructor(paths) {
    this.paths = paths;
  }

  apply(compiler) {
    compiler.hooks.afterEmit.tapPromise('SharedAssetCopyPlugin', async () => {
      const directories = ['js', 'fonts', 'images', 'videos'];
      const copyJobs = directories.map((directory) => ({
        source: path.join(this.paths.sharedStaticDir, directory),
        destination: path.join(this.paths.sharedBundlesDir, directory),
      }));
      copyJobs.push({
        source: this.paths.sharedMediaDir,
        destination: path.join(this.paths.sharedBundlesDir, 'media'),
      });
      await fse.ensureDir(this.paths.sharedBundlesDir);
      await Promise.all(copyJobs.map(async ({ source, destination }) => {
        if (await fse.pathExists(source)) {
          await fse.copy(source, destination);
        }
      }));
    });
  }
}

function buildEntries(paths) {
  const entries = {
    shared: path.join(paths.sharedStaticDir, 'static'),
    shared_styles: path.join(paths.sharedStaticDir, 'styles'),
  };
  const siteStaticEntry = path.join(paths.siteStaticDir, 'static.js');
  const siteStylesEntry = path.join(paths.siteStaticDir, 'styles.js');
  const siteStyles = path.join(paths.siteStaticDir, 'styles', 'main.scss');
  const siteMain = path.join(paths.siteStaticDir, 'js', 'main.js');
  const siteAppEntries = {
    'ctc-research': path.join(paths.siteStaticDir, 'js', 'ctc-app.js'),
    'lms-demo': path.join(paths.siteStaticDir, 'js', 'lms-app.js'),
    vresume: path.join(paths.siteStaticDir, 'js', 'vresume-app.js'),
  };
  const sharedBaseEntry = path.join(paths.baseStaticDir, 'index.js');
  const staticStack = [];

  if (fs.existsSync(sharedBaseEntry)) {
    entries.shared_base = sharedBaseEntry;
  }
  if (siteAppEntries[paths.siteName] && fs.existsSync(siteAppEntries[paths.siteName])) {
    entries[`${paths.siteName}_app`] = siteAppEntries[paths.siteName];
    staticStack.push(siteAppEntries[paths.siteName]);
  }
  if (fs.existsSync(siteMain)) {
    entries.site_main = siteMain;
    staticStack.push(siteMain);
  }
  staticStack.push(path.join(paths.sharedStaticDir, 'static'));
  if (fs.existsSync(siteStaticEntry)) {
    staticStack.push(siteStaticEntry);
  }
  entries.static = staticStack;
  if (fs.existsSync(siteStylesEntry)) {
    entries.styles = siteStylesEntry;
  }
  if (fs.existsSync(siteStyles)) {
    entries.site_styles = siteStyles;
  }
  return entries;
}

module.exports = (env = {}, argv = {}) => {
  if (env.site) {
    process.env.PROJECT_PATH = env.site;
  }
  assetPaths = resolveAssetPaths(env.site || process.env.PROJECT_PATH);
  const isProduction = argv.mode === 'production';
  process.env.NODE_ENV = isProduction ? 'production' : 'development';

  return {
    target: 'web',
    context: assetPaths.sharedStaticDir,
    entry: buildEntries(assetPaths),
    performance: { hints: false },
    plugins: [
      new webpack.ProvidePlugin({ $: 'jquery', jQuery: 'jquery', 'window.jQuery': 'jquery' }),
      new CopyWebpackPlugin({ patterns: [
        { from: path.join(assetPaths.siteStaticDir, 'images'), to: path.join(assetPaths.siteBundlesDir, 'images'), noErrorOnMissing: true },
        { from: path.join(assetPaths.siteStaticDir, 'js'), to: path.join(assetPaths.siteBundlesDir, 'js'), noErrorOnMissing: true },
      ]}),
      new SharedAssetCopyPlugin(assetPaths),
      new BundleTracker({ path: assetPaths.siteBundlesDir, filename: 'bundles.json' }),
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
      { test: /\.scss$/i, use: [MiniCssExtractPlugin.loader, { loader: 'css-loader', options: { url: false }}, { loader: 'sass-loader', options: { sassOptions: { includePaths: [path.join(assetPaths.siteStaticDir, 'styles'), path.join(assetPaths.sharedStaticDir, 'styles'), assetPaths.baseScssDir] } } }], sideEffects: true },
      { test: /\.(png|jpe?g|gif|svg|webp)$/i, type: 'asset/resource', generator: { filename: 'images/[name][ext]' } },
      { test: /\.(woff2?|eot|ttf|otf)$/i, type: 'asset/resource', generator: { filename: 'fonts/[name][ext]' } },
    ]},
    resolve: {
      extensions: ['.js', '.jsx', '.json', '.vue', '.scss', '.css'],
      alias: { shared: assetPaths.sharedStaticDir, site: assetPaths.siteStaticDir, '@base': assetPaths.baseStaticDir },
      modules: [assetPaths.assetsNodeModules, 'node_modules'],
    },
  };
};
