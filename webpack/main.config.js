const path = require('path');
const { createRequire } = require('module');
const { resolveAssetPaths } = require('./paths');

const defaultAssetPaths = resolveAssetPaths();
const assetsRequire = createRequire(path.join(defaultAssetPaths.assetsRoot, 'package.json'));
const { merge } = assetsRequire('webpack-merge');
const fs = assetsRequire('fs-extra');
const chokidar = assetsRequire('chokidar');
const rtlcss = assetsRequire('rtlcss');
const { RawSource } = assetsRequire('webpack-sources');
const commonConfig = require('./common.config');

const configPath = path.resolve(__dirname, './package-copy.json');
const ALL_SITES = ['ctc-research', 'lms-demo', 'vresume'];

const cssPairs = [
  { ltr: 'css/static.min.css', rtl: 'css/static-rtl.min.css' },
  { ltr: 'css/bootstrap.min.css', rtl: 'css/bootstrap-rtl.min.css' },
];

class SiteManifestPlugin {
  apply(compiler) {
    compiler.hooks.thisCompilation.tap('SiteManifestPlugin', (compilation) => {
      compilation.hooks.processAssets.tap(
        { name: 'SiteManifestPlugin', stage: compilation.PROCESS_ASSETS_STAGE_REPORT },
        () => {
          const manifest = {};
          for (const asset of compilation.getAssets()) {
            manifest[asset.name] = `${compilation.outputOptions.publicPath || ''}${asset.name}`;
          }
          compilation.emitAsset('manifest.json', new RawSource(JSON.stringify(manifest, null, 2)));
        }
      );
    });
  }
}

class DistMirrorPlugin {
  constructor(assetPaths) {
    this.assetPaths = assetPaths;
  }

  apply(compiler) {
    compiler.hooks.afterEmit.tapPromise('DistMirrorPlugin', async () => {
      await fs.ensureDir(this.assetPaths.distSiteDir);
      await fs.copy(this.assetPaths.siteBundlesDir, this.assetPaths.distSiteDir);
      if (await fs.pathExists(this.assetPaths.sharedBundlesDir)) {
        await fs.ensureDir(this.assetPaths.distSharedDir);
        await fs.copy(this.assetPaths.sharedBundlesDir, this.assetPaths.distSharedDir);
      }
    });
  }
}

async function copyLibs(assetPaths) {
  const outputPath = assetPaths.siteBundlesDir;
  const libsOutputPath = path.join(outputPath, 'libs');
  try {
    if (!fs.existsSync(configPath)) {
      console.log('📝 No package-copy.json found, skipping library copy');
      return [];
    }

    const configContent = await fs.readFile(configPath, 'utf-8');
    const { packagesToCopy } = JSON.parse(configContent);
    const copiedPackages = [];

    await fs.ensureDir(libsOutputPath);

    for (const packageName of packagesToCopy) {
      const destPackagePath = path.join(libsOutputPath, packageName);
      const packageRoot = path.join(assetPaths.assetsNodeModules, packageName);
      const sourcePath = fs.existsSync(path.join(packageRoot, 'dist'))
        ? path.join(packageRoot, 'dist')
        : packageRoot;

      if (!fs.existsSync(sourcePath)) {
        console.warn(`⚠️ Skipping ${packageName}; run npm --prefix assets install to install package-copy dependencies.`);
        continue;
      }
      await fs.copy(sourcePath, destPackagePath);
      console.log(`📦 Copied ${packageName} to libs/`);
      copiedPackages.push(destPackagePath);
    }

    return copiedPackages;
  } catch (error) {
    console.error('❌ Error copying packages:', error);
    return [];
  }
}

async function cleanupLibs(copiedPackages) {
  try {
    for (const packagePath of copiedPackages) {
      await fs.remove(packagePath);
      console.log(`🧹 Removed ${path.basename(packagePath)} from libs/`);
    }
  } catch (error) {
    console.error('❌ Error cleaning up packages:', error);
  }
}

function createSiteConfig(env = {}, argv = {}, siteName) {
  const assetPaths = resolveAssetPaths(siteName || env.site || process.env.PROJECT_PATH);
  const outputPath = assetPaths.siteBundlesDir;
  const staticUrl = `/static/bundles/${assetPaths.siteName}/`;
  const mode = argv.mode || (process.env.NODE_ENV === 'production' ? 'production' : 'development');
  const isProduction = mode === 'production';
  const isWatch = argv.watch || false;
  const isServe = argv.hot || false;

  const publicPath = isServe
    ? 'http://localhost:3000/static/'
    : process.env.WEBPACK_PUBLIC_PATH || staticUrl;

  console.log(`🚀 ${assetPaths.siteName} webpack mode: ${mode}`);
  console.log(`📦 ${assetPaths.siteName} public path: ${publicPath}`);

  let copiedPackages = [];
  let watcher = null;
  const common = commonConfig({ ...env, site: assetPaths.siteName }, argv);

  return merge(common, {
    name: assetPaths.siteName,
    mode,
    output: {
      path: outputPath,
      publicPath,
      filename: isProduction ? '[name].[contenthash:8].js' : '[name].js',
      chunkFilename: isProduction ? 'chunk/[name].[contenthash:8].chunk.js' : 'chunk/[name].chunk.js',
      clean: !isWatch,
    },
    cache: {
      type: 'filesystem',
      buildDependencies: { config: [__filename] },
      cacheDirectory: path.join(assetPaths.assetsNodeModules, '.cache', 'webpack', assetPaths.siteName),
    },
    performance: {
      hints: isProduction ? 'warning' : false,
      maxAssetSize: 512000,
      maxEntrypointSize: 512000,
    },
    plugins: [
      new SiteManifestPlugin(),
      new DistMirrorPlugin(assetPaths),
      {
        apply: (compiler) => {
          compiler.hooks.beforeRun.tapPromise('CopyLibs', async () => {
            copiedPackages = await copyLibs(assetPaths);
          });
          compiler.hooks.thisCompilation.tap('GenerateRTL', (compilation) => {
            compilation.hooks.processAssets.tap(
              { name: 'GenerateRTL', stage: compilation.PROCESS_ASSETS_STAGE_ADDITIONAL },
              () => {
                cssPairs.forEach((pair) => {
                  const ltrAsset = compilation.assets[pair.ltr];
                  if (ltrAsset) {
                    const rtlCss = rtlcss.process(ltrAsset.source(), { autoRename: false, clean: false });
                    compilation.emitAsset(pair.rtl, new RawSource(rtlCss));
                  }
                });
              }
            );
          });
          if (isWatch || isServe) {
            compiler.hooks.watchRun.tap('WatchPackageConfig', () => {
              if (!watcher) {
                watcher = chokidar.watch(configPath, { persistent: true, ignoreInitial: true });
                watcher.on('change', async () => {
                  await cleanupLibs(copiedPackages);
                  copiedPackages = await copyLibs(assetPaths);
                });
              }
            });
            compiler.hooks.watchClose.tap('CloseWatcher', () => {
              if (watcher) {
                watcher.close();
                watcher = null;
              }
            });
          }
          if (isProduction && !isWatch && !isServe) {
            compiler.hooks.done.tapPromise('CleanupLibs', async () => cleanupLibs(copiedPackages));
          }
        },
      },
    ],
    ...((isServe || isWatch) && {
      devServer: {
        port: 3000,
        host: 'localhost',
        hot: isServe,
        liveReload: true,
        open: false,
        proxy: { '/': { target: process.env.DJANGO_DEV_SERVER || 'http://localhost:5080', changeOrigin: true } },
        client: { overlay: { errors: true, warnings: false, runtimeErrors: true }, progress: true },
        static: { directory: outputPath, publicPath: staticUrl, watch: !isServe },
        compress: true,
        historyApiFallback: true,
        devMiddleware: { writeToDisk: true, stats: 'minimal' },
      },
    }),
    optimization: {
      minimize: isProduction,
      minimizer: ['...'],
      splitChunks: {
        chunks: 'all',
        minSize: 10000,
        maxSize: 50000,
        cacheGroups: {
          vendors: { test: /[\\/]node_modules[\\/]/, name: 'vendors', chunks: 'all', priority: 20, enforce: true },
          sharedBase: { test: /[\\/]assets[\\/]static[\\/]js[\\/]base[\\/]/, name: 'shared-base', chunks: 'all', priority: 15, enforce: true },
          common: { name: 'common', minChunks: 2, chunks: 'all', priority: 5, reuseExistingChunk: true },
        },
      },
      runtimeChunk: 'single',
    },
    bail: isProduction,
    devtool: isProduction ? 'source-map' : 'cheap-module-source-map',
    stats: { colors: true, modules: false, chunks: false, assets: true, performance: isProduction, timings: true },
  });
}

module.exports = async (env = {}, argv = {}) => {
  const selected = env.site || process.env.PROJECT_PATH || 'ctc-research';
  if (selected === 'all') {
    return ALL_SITES.map((site) => createSiteConfig(env, argv, site));
  }
  return createSiteConfig(env, argv, selected);
};
