/**
 * Shared Path Utilities for Project Webpack Configs
 *
 * Provides consistent path resolution for all project webpack builds.
 *
 * Usage:
 *   const { resolvePaths } = require('../../webpack/paths');
 *   const paths = resolvePaths(__dirname + '/..');
 */

const path = require('path');
const fs = require('fs');

/**
 * Resolve all standard project paths from a project root.
 *
 * @param {string} projectRoot - Absolute path to the project root
 * @returns {Object} Path map
 */
function resolvePaths(projectRoot) {
  const root = path.resolve(projectRoot);
  const assetsDir = path.join(root, 'assets');
  const staticDir = path.join(assetsDir, 'static');
  const bundlesDir = path.join(assetsDir, 'bundles');
  const nodeModulesDir = fs.existsSync(path.join(root, 'node_modules'))
    ? path.join(root, 'node_modules')
    : null;

  return {
    // Project
    projectRoot: root,
    projectName: path.basename(root),

    // Assets
    assetsDir,
    staticDir,
    bundlesDir,

    // Sub-directories
    stylesDir: path.join(staticDir, 'styles'),
    scriptsDir: path.join(staticDir, 'js'),
    imagesDir: path.join(staticDir, 'images'),
    fontsDir: path.join(staticDir, 'fonts'),
    libsDir: path.join(staticDir, 'libs'),

    // Node modules — project-local only (each project has its own package.json)
    nodeModulesDir: nodeModulesDir || path.join(root, 'node_modules'),

    // Output
    outputDir: bundlesDir,
    outputPublicPath: '/static/bundles/',
  };
}

module.exports = {
  resolvePaths,
  // Backward compat — these always resolve relative to the caller's project root.
  // Prefer resolvePaths(projectRoot) for explicit path resolution.
  WORKSPACE_ROOT: path.resolve(__dirname, '..'),
};
