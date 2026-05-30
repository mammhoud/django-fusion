const path = require('path');

const WORKSPACE_ROOT = path.resolve(__dirname, '..');
const ASSETS_ROOT = path.join(WORKSPACE_ROOT, 'assets');
const ASSETS_NODE_MODULES = path.join(ASSETS_ROOT, 'node_modules');

function normalizeSiteName(value) {
  const raw = value || process.env.PROJECT_PATH || process.env.DJANGO_WEBSITE || process.env.WEBSITE || 'ctc-research.com';
  const aliases = {
    ctc: 'ctc-research.com',
    'ctc-research': 'ctc-research.com',
    structa: 'structa.cloud',
    core: 'structa.cloud',
  };
  return aliases[raw] || raw;
}

function resolveAssetPaths(siteName = normalizeSiteName()) {
  const selectedSite = normalizeSiteName(siteName);
  const sourceSiteDir = path.join(WORKSPACE_ROOT, selectedSite);
  const wrapperSiteDir = path.join(WORKSPACE_ROOT, 'websites', selectedSite);
  const siteDir = require('fs').existsSync(sourceSiteDir) ? sourceSiteDir : wrapperSiteDir;
  const siteAssetsDir = path.join(siteDir, 'assets');
  const siteStaticDir = path.join(siteAssetsDir, 'static');
  const siteBundlesDir = path.join(siteAssetsDir, 'bundles', selectedSite);
  const sharedStaticDir = path.join(ASSETS_ROOT, 'static');
  const sharedBundlesDir = path.join(ASSETS_ROOT, 'bundles', 'shared');

  return {
    workspaceRoot: WORKSPACE_ROOT,
    assetsRoot: ASSETS_ROOT,
    assetsNodeModules: ASSETS_NODE_MODULES,
    siteName: selectedSite,
    siteDir,
    siteAssetsDir,
    siteStaticDir,
    siteBundlesDir,
    sharedStaticDir,
    sharedBundlesDir,
  };
}

module.exports = {
  WORKSPACE_ROOT,
  ASSETS_ROOT,
  ASSETS_NODE_MODULES,
  normalizeSiteName,
  resolveAssetPaths,
};
