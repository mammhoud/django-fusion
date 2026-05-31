const { merge } = require('webpack-merge');
const commonConfig = require('./common.config');
const path = require('path');

// ── Paths ─────────────────────────────────────────────────────────────────────
// Webpack writes to assets/bundles/
// Django collectstatic then copies everything into assets/staticfiles/
const outputPath = path.resolve(__dirname, '../assets/bundles');
const staticUrl  = '/static/';

// ── Config factory ────────────────────────────────────────────────────────────
module.exports = (env, argv) => {
  const mode        = argv.mode || (process.env.NODE_ENV === 'production' ? 'production' : 'development');
  const isProduction = mode === 'production';
  const isWatch      = !!argv.watch;
  const isServe      = !!argv.hot;

  console.log(`🚀 Webpack mode: ${mode}`);
  console.log(`👀 Watch mode: ${isWatch ? 'enabled' : 'disabled'}`);
  console.log(`🔥 Serve mode: ${isServe ? 'enabled (HMR)' : 'disabled'}`);

  const common = commonConfig(env, argv);

  return merge(common, {
    mode,

    output: {
      path:          outputPath,
      publicPath:    staticUrl,
      filename:      isProduction ? '[name].[contenthash:8].js' : '[name].js',
      chunkFilename: isProduction ? 'chunk/[name].[contenthash:8].chunk.js' : 'chunk/[name].chunk.js',
      clean:         !isWatch,
    },

    cache: {
      type: 'filesystem',
      buildDependencies: { config: [__filename] },
      cacheDirectory: path.resolve(__dirname, '../node_modules/.cache/webpack'),
    },

    performance: {
      hints:             isProduction ? 'warning' : false,
      maxAssetSize:      512_000,
      maxEntrypointSize: 512_000,
    },

    optimization: {
      minimize: isProduction,
      minimizer: ['...'],
      splitChunks: {
        chunks:  'all',
        minSize: 20_000,
        maxSize: 244_000,
        cacheGroups: {
          vendors: {
            test:               /[\\/]node_modules[\\/]/,
            name:               'vendors',
            chunks:             'all',
            priority:           10,
            reuseExistingChunk: true,
            enforce:            true,
          },
          common: {
            name:               'common',
            minChunks:          2,
            chunks:             'all',
            priority:           5,
            reuseExistingChunk: true,
            enforce:            true,
          },
        },
      },
      runtimeChunk: { name: 'runtime' },
      usedExports:  true,
    },

    bail:    isProduction,
    devtool: isProduction ? 'source-map' : 'cheap-module-source-map',

    stats: {
      colors:      true,
      modules:     false,
      chunks:      false,
      assets:      true,
      performance: isProduction,
      timings:     true,
    },

    // ── Dev-server (only active for `npm run dev`) ──────────────────────────
    ...((isServe || isWatch) && {
      devServer: {
        port:       3000,
        host:       'localhost',
        hot:        isServe,
        liveReload: true,
        open:       false,
        proxy: [{
          context:      ['/'],
          target:       'http://localhost:5080',
          changeOrigin: true,
        }],
        client: {
          overlay:  { errors: true, warnings: false, runtimeErrors: true },
          progress: true,
        },
        static: {
          directory:  outputPath,
          publicPath: staticUrl,
          watch:      !isServe,
        },
        compress: true,
        historyApiFallback: true,
        devMiddleware: {
          writeToDisk: true,
          stats:       'minimal',
        },
      },
    }),
  });
};
