const path = require('path');

const WORKSPACE_ROOT = path.resolve(__dirname, '..');
const ASSETS_ROOT = path.join(WORKSPACE_ROOT, 'assets');
const ASSETS_NODE_MODULES = path.join(ASSETS_ROOT, 'node_modules');
const DIST_ROOT = path.join(WORKSPACE_ROOT, 'dist');

function normalizeSiteName(value) {
  const raw = value || process.env.PROJECT_PATH || process.env.DJANGO_WEBSITE || process.env.WEBSITE || 'ctc-research.com';
  const aliases = {
    ctc: 'ctc-research',
    'ctc-website': 'ctc-research',
    'ctc-website.local': 'ctc-research',
    'ctc-research.com': 'ctc-research',
    structa: 'lms-demo',
    core: 'lms-demo',
    'structa.cloud': 'lms-demo',
    resume: 'vresume',
    VResume: 'vresume',
    'vresume.structa.cloud': 'vresume',
    'crm.structa.cloud': 'crm',
    inventory: 'crm',
  };
  return aliases[raw] || raw;
}

function resolveAssetPaths(siteName = normalizeSiteName()) {
  const selectedSite = normalizeSiteName(siteName);
  const siteDirectoryNames = { vresume: 'VResume' };
  const sourceSiteDir = path.join(WORKSPACE_ROOT, siteDirectoryNames[selectedSite] || selectedSite);
  const wrapperSiteDir = path.join(WORKSPACE_ROOT, 'websites', selectedSite);
  const siteDir = require('fs').existsSync(sourceSiteDir) ? sourceSiteDir : wrapperSiteDir;
  const siteAssetsDir = path.join(siteDir, 'assets');
  const siteStaticDir = path.join(siteAssetsDir, 'static');
  const siteBundlesDir = path.join(siteAssetsDir, 'bundles', selectedSite);
  const sharedStaticDir = path.join(ASSETS_ROOT, 'static');
  const baseStaticDir = path.join(sharedStaticDir, 'js', 'base');
  const baseScssDir = path.join(sharedStaticDir, 'scss');
  const sharedBundlesDir = path.join(ASSETS_ROOT, 'bundles', 'shared');
  const sharedMediaDir = path.join(ASSETS_ROOT, 'media');
  const distRoot = DIST_ROOT;
  const distSharedDir = path.join(DIST_ROOT, 'shared');
  const distSiteDir = path.join(DIST_ROOT, selectedSite);

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
    baseStaticDir,
    baseScssDir,
    sharedBundlesDir,
    sharedMediaDir,
    distRoot,
    distSharedDir,
    distSiteDir,
  };
}

module.exports = {
  WORKSPACE_ROOT,
  ASSETS_ROOT,
  ASSETS_NODE_MODULES,
  DIST_ROOT,
  normalizeSiteName,
  resolveAssetPaths,
};
