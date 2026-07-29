/**
 * Webpack Workspace Configuration Loader
 *
 * Loads a workspace-specific webpack configuration based on the
 * FUSION_WEBPACK_WORKSPACE environment variable.
 *
 * Usage:
 *   FUSION_WEBPACK_WORKSPACE=default npx webpack --config webpack.config.js
 *   FUSION_WEBPACK_WORKSPACE=custom npx webpack --config webpack.config.js
 *
 * Workspace configs live in the `webpack/workspaces/` directory.
 * Each workspace exports `{ entries, output, plugins }` overrides.
 */

const path = require("path");
const fs = require("fs");

const WORKSPACES_DIR = path.resolve(__dirname, "workspaces");
const DEFAULT_WORKSPACE = process.env.FUSION_WEBPACK_WORKSPACE || "default";

/**
 * Resolve and load a workspace configuration by name.
 * Falls back to "default" if the named workspace is not found.
 */
function loadWorkspace(name) {
  const customPath = process.env.FUSION_WEBPACK_WORKSPACE_PATH;
  if (customPath && fs.existsSync(customPath)) {
    return require(path.resolve(customPath));
  }

  const workspacePath = path.join(WORKSPACES_DIR, `${name}.js`);
  if (fs.existsSync(workspacePath)) {
    console.log(`[fusion-webpack] Loading workspace: "${name}"`);
    return require(workspacePath);
  }

  const defaultPath = path.join(WORKSPACES_DIR, "default.js");
  if (fs.existsSync(defaultPath)) {
    console.warn(
      `[fusion-webpack] Workspace "${name}" not found. Falling back to "default".`
    );
    return require(defaultPath);
  }

  console.warn(
    `[fusion-webpack] No workspace configs found at ${WORKSPACES_DIR}. Using empty config.`
  );
  return { entries: {}, output: {}, plugins: [] };
}

const workspace = loadWorkspace(DEFAULT_WORKSPACE);

module.exports = {
  workspace,
  loadWorkspace,
  DEFAULT_WORKSPACE,
  WORKSPACES_DIR,
};
