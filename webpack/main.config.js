const { merge } = require('webpack-merge');
const commonConfig = require('./common.config');
const path = require('path');
const fs = require('fs-extra');
const chokidar = require('chokidar');

// Configuration paths
const staticUrl = '/static/';
const outputPath = path.resolve(__dirname, '../assets/bundles');
const libsOutputPath = path.join(outputPath, 'libs');
const configPath = path.resolve(__dirname, './package-copy.json');

// RTL CSS Pairs
const cssPairs = [
  { ltr: 'css/static.min.css', rtl: 'css/static-rtl.min.css' },
  { ltr: 'css/bootstrap.min.css', rtl: 'css/bootstrap-rtl.min.css' },
];

// Package copying function
async function copyLibs() {
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
      const sourcePath = fs.existsSync(path.join(__dirname, '../node_modules', packageName, 'dist'))
        ? path.join(__dirname, '../node_modules', packageName, 'dist')
        : path.join(__dirname, '../node_modules', packageName);

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

// Cleanup function
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

module.exports = async (env, argv) => {
  const mode = argv.mode || (process.env.NODE_ENV === 'production' ? 'production' : 'development');
  const isProduction = mode === 'production';
  const isWatch = argv.watch || false;
  const isServe = argv.hot || false;

  // Determine public path based on environment
  // In Docker/production, assets are served through nginx at /static/
  // In development with webpack-dev-server, use localhost:3000
  const publicPath = isServe
    ? 'http://localhost:3000/static/'
    : process.env.WEBPACK_PUBLIC_PATH || staticUrl;

  console.log(`🚀 Webpack mode: ${mode}`);
  console.log(`👀 Watch mode: ${isWatch ? 'enabled' : 'disabled'}`);
  console.log(`🔥 Serve mode: ${isServe ? 'enabled (HMR)' : 'disabled'}`);
  console.log(`📦 Public path: ${publicPath}`);

  let copiedPackages = [];
  let watcher = null;

  const common = commonConfig(env, argv);

  const config = merge(common, {
    mode,

    output: {
      path: outputPath,
      publicPath: publicPath,
      filename: isProduction ? '[name].[contenthash:8].js' : '[name].js',
      chunkFilename: isProduction ? 'chunk/[name].[contenthash:8].chunk.js' : 'chunk/[name].chunk.js',
      clean: !isWatch, // Don't clean during watch mode
    },

    cache: {
      type: "filesystem",
      buildDependencies: {
        config: [__filename],
      },
      cacheDirectory: path.resolve(__dirname, '../node_modules/.cache/webpack'),
    },

    performance: {
      hints: isProduction ? "warning" : false,
      maxAssetSize: 512000,
      maxEntrypointSize: 512000,
    },

    plugins: [
      {
        apply: (compiler) => {
          // Copy libraries before build starts
          compiler.hooks.beforeRun.tapPromise('CopyLibs', async () => {
            copiedPackages = await copyLibs();
          });

          // Generate RTL CSS
          compiler.hooks.thisCompilation.tap('GenerateRTL', (compilation) => {
            compilation.hooks.processAssets.tap(
              {
                name: 'GenerateRTL',
                stage: compilation.PROCESS_ASSETS_STAGE_ADDITIONAL,
              },
              () => {
                cssPairs.forEach((pair) => {
                  const ltrAsset = compilation.assets[pair.ltr];
                  if (ltrAsset) {
                    const rtlCss = rtlcss.process(ltrAsset.source(), {
                      autoRename: false,
                      clean: false
                    });
                    compilation.emitAsset(pair.rtl, new RawSource(rtlCss));
                  }
                });
              }
            );
          });

          // Watch package-copy.json in watch/serve mode
          if (isWatch || isServe) {
            compiler.hooks.watchRun.tap('WatchPackageConfig', () => {
              if (!watcher) {
                console.log('👀 Watching package-copy.json for changes...');
                watcher = chokidar.watch(configPath, {
                  persistent: true,
                  ignoreInitial: true,
                });

                watcher.on('change', async () => {
                  console.log('📄 package-copy.json changed, updating libraries...');
                  await cleanupLibs(copiedPackages);
                  copiedPackages = await copyLibs();
                });
              }
            });

            compiler.hooks.watchClose.tap('CloseWatcher', () => {
              if (watcher) {
                watcher.close();
                watcher = null;
                console.log('👋 Stopped watching package-copy.json');
              }
            });
          }

          // Cleanup after production build
          if (isProduction && !isWatch && !isServe) {
            compiler.hooks.done.tapPromise('CleanupLibs', async () => {
              await cleanupLibs(copiedPackages);
            });
          }
        }
      }
    ],

    // Development server configuration
    ...((isServe || isWatch) && {
      devServer: {
        port: 3000,
        host: 'localhost',
        hot: isServe, // Only enable HMR in serve mode
        liveReload: true,
        open: false,
        proxy: {
          '/': {
            target: 'http://localhost:8000',
            changeOrigin: true,
          }
        },
        client: {
          overlay: {
            errors: true,
            warnings: false,
            runtimeErrors: true,
          },
          progress: true,
        },
        static: {
          directory: outputPath,
          publicPath: `${staticUrl}`,
          watch: !isServe, // Watch static files in watch mode only
        },
        compress: true,
        historyApiFallback: true,
        devMiddleware: {
          writeToDisk: true, // Write files to disk for Django to serve
          stats: 'minimal',
        },
      },
    }),

    optimization: {
      minimize: isProduction,
      minimizer: [
        '...', // Use default minimizers
      ],
      splitChunks: {
        chunks: 'all',
        minSize: 10000,
        maxSize: 50000,
        cacheGroups: {
          vendors: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10,
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 5,
            reuseExistingChunk: true,
          },
        },
      },
      runtimeChunk: 'single',
    },

    bail: isProduction, // Stop on error in production
    devtool: isProduction ? 'source-map' : 'cheap-module-source-map',
    stats: {
      colors: true,
      modules: false,
      chunks: false,
      assets: true,
      performance: isProduction,
      timings: true,
    },
  });

  return config;
};
