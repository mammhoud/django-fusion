/**
 * Webpack Main Configuration
 * Entry point configuration for all 3 workspace sites
 */

const path = require('path');
const fs = require('fs');

// Resolve webpack-merge from assets/node_modules
const webpackMergePath = require.resolve('webpack-merge', { paths: [path.join(__dirname, '../assets/node_modules')] });
const { merge } = require(webpackMergePath);

// Common config is in the same directory
const assetsRoot = path.resolve(__dirname, '../assets');
const commonConfig = require(path.join(__dirname, 'common.config.js'));

module.exports = (env, argv) => {
  const { site = 'ctc-research' } = env;
  const projectPath = process.env.PROJECT_PATH || site;
  const mode = argv.mode || 'production';

  // Map site names to directories
  const siteDir = {
    'ctc-research': 'ctc-research',
    'ctc': 'ctc-research',
    'lms-demo': 'lms-demo',
    'lms': 'lms-demo',
    'structa': 'lms-demo',
    'vresume': 'VResume',
    'resume': 'VResume',
  }[projectPath] || projectPath;

  // Determine entry point
  let entry = {};
  
  if (siteDir === 'VResume') {
    entry = {
      'vresume-app': './VResume/assets/static/js/vresume-app.js',
    };
  } else if (siteDir === 'lms-demo') {
    entry = {
      'lms-app': './lms-demo/assets/static/js/lms-app.js',
    };
  } else {
    entry = {
      'ctc-app': './ctc-research/assets/static/js/ctc-app.js',
    };
  }

  // Main JS entry points
  const sharedEntry = {
    'main': './assets/static/js/core/main.js',
  };

  console.log(`🚀 ${siteDir} webpack mode: ${mode}`);
  console.log(`📦 ${siteDir} public path: /static/bundles/${siteDir}/`);

  return merge(commonConfig, {
    mode,
    entry: {
      ...sharedEntry,
      ...entry,
    },
    output: {
      path: path.resolve(__dirname, `../assets/bundles/${siteDir}`),
      publicPath: `/static/bundles/${siteDir}/`,
      filename: '[name]-[contenthash:8].js',
      chunkFilename: 'chunk-[name]-[contenthash:8].js',
      clean: mode === 'production',
    },
    resolve: {
      extensions: ['.js', '.jsx', '.vue', '.json'],
      alias: {
        '@utility':  path.resolve(__dirname, '../assets/static/js/utility'),
        '@base':     path.resolve(__dirname, '../assets/static/js/utility'),
        '@theme':    path.resolve(__dirname, '../assets/static/js/theme'),
        '@modules':  path.resolve(__dirname, '../assets/static/js/modules'),
        '@plugins':  path.resolve(__dirname, '../assets/static/js/plugins'),
        '@core':     path.resolve(__dirname, '../assets/static/js/core'),
        '@layouts':  path.resolve(__dirname, '../assets/static/js/theme/layouts'),
        '@usecases': path.resolve(__dirname, '../assets/static/js/theme/usecases'),
        '@htmx':     path.resolve(__dirname, '../assets/static/js/core/htmx-bridge'),
        '@ctc':      path.resolve(__dirname, '../ctc-research/assets/static/js'),
        '@lms':      path.resolve(__dirname, '../lms-demo/assets/static/js'),
        '@vresume':  path.resolve(__dirname, '../VResume/assets/static/js'),
      },
    },
  });
};
