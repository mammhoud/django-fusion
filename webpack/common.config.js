const path = require('path');
const webpack = require('webpack');
const { VueLoaderPlugin } = require('vue-loader');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const CopyWebpackPlugin = require('copy-webpack-plugin');

const PROJECT_PATH = process.env.PROJECT_PATH || 'ctc-research.com';
const SITE_NAME = path.basename(PROJECT_PATH);
const WORKSPACE_ROOT = path.resolve(__dirname, '..');
const isDocker = process.env.RUNNING_ENV === 'docker';
const SITE_DIR = isDocker ? WORKSPACE_ROOT : path.resolve(WORKSPACE_ROOT, PROJECT_PATH);
const SHARED_DIR = isDocker ? path.join(WORKSPACE_ROOT, 'shared', 'assets', 'static') : path.join(WORKSPACE_ROOT, 'assets', 'static');
const DIST_DIR = path.join(SITE_DIR, 'assets', 'bundles');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  process.env.NODE_ENV = isProduction ? 'production' : 'development';

  return {
    target: 'web',
    context: SHARED_DIR,
    entry: {
      static: path.join(SHARED_DIR, 'static'),
      styles: path.join(SHARED_DIR, 'styles'),
    },
    performance: { hints: false },
    plugins: [
      new webpack.ProvidePlugin({ $: 'jquery', jQuery: 'jquery', 'window.jQuery': 'jquery' }),
      new CopyWebpackPlugin({ patterns: [
        { from: path.join(SHARED_DIR, 'js'), to: path.join(DIST_DIR, 'js'), noErrorOnMissing: true },
        { from: path.join(SHARED_DIR, 'libs'), to: path.join(DIST_DIR, 'libs'), noErrorOnMissing: true },
        { from: path.join(SHARED_DIR, 'images'), to: path.join(DIST_DIR, 'images'), noErrorOnMissing: true },
      ]}),
      new BundleTracker({ path: DIST_DIR, filename: 'bundles.json' }),
      new MiniCssExtractPlugin({ filename: isProduction ? 'css/[name].[contenthash:8].min.css' : 'css/[name].min.css' }),
      new VueLoaderPlugin(),
    ],
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
      alias: { shared: SHARED_DIR, site: path.join(SITE_DIR, 'assets', 'static') },
    },
  };
};
