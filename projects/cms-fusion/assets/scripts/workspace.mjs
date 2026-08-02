#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { existsSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const assetsRoot = path.resolve(__dirname, '..');
const workspaceRoot = path.resolve(assetsRoot, '..');
const webpackBin = path.join(assetsRoot, 'node_modules', '.bin', process.platform === 'win32' ? 'webpack.cmd' : 'webpack');

const siteAliases = {
  structa: 'lms',
  core: 'lms',
  lms: 'lms',
  'lms': 'lms',
  'structa.cloud': 'lms',
  vresume: 'vresume',
  VResume: 'vresume',
  resume: 'vresume',
  'vresume.structa.cloud': 'vresume',
  cypercloud: 'cypercloud',
  customizer: 'cypercloud',
  cust: 'cypercloud',
  crm: 'crm',
  'crm.structa.cloud': 'crm',
  inventory: 'crm',
  'lms-fusion': 'lms-fusion',
  fusionlms: 'lms-fusion',
  fusioncms: 'cms-fusion',
  'cms-fusion': 'cms-fusion',
};

const sites = ['lms', 'vresume', 'cypercloud', 'crm', 'lms-fusion', 'cms-fusion'];
const siteDirs = {
  'lms': 'lms',
  vresume: 'VResume',
  cypercloud: 'cypercloud',
  crm: 'crm',
  'lms-fusion': 'lms-fusion',
  'cms-fusion': 'cms-fusion',
};
const cleanDirs = {
  'lms': ['lms/assets/bundles/lms'],
  vresume: ['VResume/assets/bundles/vresume'],
  cypercloud: ['cypercloud/assets/bundles/customizer'],
  crm: ['crm/assets/bundles/crm'],
  'lms-fusion': ['lms-fusion/assets/bundles/lms-fusion'],
  'cms-fusion': ['cms-fusion/assets/bundles/cms-fusion'],
  shared: ['assets/bundles/shared'],
};

function usage() {
  console.log(`Workspace asset CLI\n\nUsage:\n  npm --prefix assets run <script> -- [--site structa|vresume|customizer|all]\n  node assets/scripts/workspace.mjs <command> [--site SITE] [-- <extra args>]\n\nSites:\n  structa, lms       Structa LMS Demo\n  vresume                 VResume resume builder\n  cypercloud, customizer, cust  Structa template cypercloud (standalone webpack)\n  lms-fusion, fusionlms          Fusion LMS (isolated)\n  cms-fusion, fusioncms          Fusion CMS (isolated)\n\nCommands:\n  build            Production webpack build for one site (default cms-fusion)\n  build-dev        Development webpack build for one site\n  watch            Webpack watch for one site\n  dev              Webpack dev server for one site\n  analyze          Emit webpack stats for one site (not supported for customizer)\n  clean            Remove generated bundles for one site or all sites\n  collectstatic    Run Django collectstatic for one site or all sites\n  build-collect    Build assets then collect static for one site or all sites\n  load-dumps       Load JSON dump fixtures for one site or all sites\n  populate         Run fixture loading and site-specific Python content/image population\n  manage           Run workspace manage.py for one site; pass Django args after --\n  sites            Print supported site names\n`);
}

function parse(argv) {
  const args = [...argv];
  const command = args.shift() || 'help';
  let site = process.env.PROJECT_PATH || process.env.DJANGO_SITE || process.env.WEBSITE || 'cms-fusion';
  const extra = [];
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === '--') {
      extra.push(...args.slice(i + 1));
      break;
    }
    if (arg === '--site' || arg === '-s') {
      site = args[i + 1] || site;
      i += 1;
    } else if (arg.startsWith('--site=')) {
      site = arg.split('=', 2)[1];
    } else {
      extra.push(arg);
    }
  }
  return { command, site: normalizeSite(site), extra };
}

function normalizeSite(value) {
  return siteAliases[value] || value;
}

function selectedSites(site) {
  return site === 'all' ? sites : [site];
}

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd || workspaceRoot,
    env: { ...process.env, ...(options.env || {}) },
    stdio: 'inherit',
    shell: false,
  });
  if (result.error) {
    console.error(result.error.message);
    process.exit(result.status || 1);
  }
  if (result.status !== 0) {
    process.exit(result.status);
  }
}

function pythonBin() {
  const candidate = path.join(workspaceRoot, '.venv', 'bin', 'python');
  return existsSync(candidate) ? candidate : 'python';
}

function webpack(site, mode, extra = []) {
  if (!existsSync(webpackBin)) {
    console.error('Missing local webpack CLI. Run `npm --prefix assets ci --include=dev --legacy-peer-deps` before building assets.');
    process.exit(1);
  }
  const env = { PROJECT_PATH: site, DJANGO_SITE: site, WEBSITE: site, NODE_ENV: mode };
  run(webpackBin, ['--env', `site=${site}`, '--mode', mode, '--config', '../webpack/main.config.js', ...extra], { cwd: assetsRoot, env });
}

function manage(site, args) {
  run(pythonBin(), ['manage.py', `--site=${site}`, ...args], { cwd: workspaceRoot, env: { PROJECT_PATH: site, DJANGO_SITE: site, WEBSITE: site } });
}

function generateAssetManifest(site) {
  manage(site, ['generate_asset_manifest']);
}

function clean(site) {
  for (const selected of selectedSites(site)) {
    const dirs = cleanDirs[selected] || [`${siteDirs[selected] || selected}/assets/bundles/${selected}`];
    for (const relative of dirs) {
      rmSync(path.join(workspaceRoot, relative), { recursive: true, force: true });
      console.log(`Removed ${relative}`);
    }
  }
  if (site === 'all') {
    for (const relative of cleanDirs.shared) {
      rmSync(path.join(workspaceRoot, relative), { recursive: true, force: true });
      console.log(`Removed ${relative}`);
    }
  }
}

// ── Customizer helpers (standalone app, not the shared webpack/config) ─────

const isTinker = (site) => site === 'cypercloud';

function tinkerBuild(mode) {
  const script = mode === 'production' ? 'build' : 'build:dev';
  run('npm', ['--prefix', 'cypercloud/assets', 'run', script], { cwd: workspaceRoot });
}

function tinkerWatch() {
  run('npm', ['--prefix', 'cypercloud/assets', 'run', 'watch'], { cwd: workspaceRoot });
}

function tinkerDev() {
  run('npm', ['--prefix', 'cypercloud/assets', 'run', 'dev'], { cwd: workspaceRoot });
}

function tinkerClean() {
  const dirs = cleanDirs['cypercloud'];
  for (const relative of dirs) {
    rmSync(path.join(workspaceRoot, relative), { recursive: true, force: true });
    console.log(`Removed ${relative}`);
  }
}

function tinkerCollectstatic() {
  const managePy = path.join(workspaceRoot, 'cypercloud', 'manage.py');
  if (!existsSync(managePy)) {
    console.error('Tinker manage.py not found — cannot collectstatic.');
    process.exit(1);
  }
  run(pythonBin(), [managePy, 'collectstatic', '--noinput'], { cwd: workspaceRoot });
}

function tinkerBuildCollect() {
  tinkerBuild('production');
  tinkerCollectstatic();
}

function populate(site, extra) {
  for (const selected of selectedSites(site)) {
    run(pythonBin(), ['tests/scripts/populate_site_data.py', '--site', selected, ...extra], { cwd: workspaceRoot, env: { PROJECT_PATH: selected, DJANGO_SITE: selected, WEBSITE: selected } });
  }
}

const { command, site, extra } = parse(process.argv.slice(2));

switch (command) {
  case 'help':
  case '--help':
  case '-h':
    usage();
    break;
  case 'sites':
    console.log(sites.join('\n'));
    break;
  case 'build':
    for (const selected of selectedSites(site)) {
      if (isTinker(selected)) { tinkerBuild('production'); }
      else { webpack(selected, 'production', extra); }
    }
    break;
  case 'build-dev':
    for (const selected of selectedSites(site)) {
      if (isTinker(selected)) { tinkerBuild('development'); }
      else { webpack(selected, 'development', extra); }
    }
    break;
  case 'watch':
    if (isTinker(site)) { tinkerWatch(); break; }
    webpack(site, 'development', ['watch', ...extra]);
    break;
  case 'dev':
    if (isTinker(site)) { tinkerDev(); break; }
    webpack(site, 'development', ['serve', ...extra]);
    break;
  case 'analyze':
    if (isTinker(site)) {
      console.log('analyze is not supported for cypercloud (uses standalone webpack config). Use `npm --prefix cypercloud/assets run build -- --profile --json` instead.');
      break;
    }
    webpack(site, 'production', ['--profile', '--json', ...extra]);
    break;
  case 'clean':
    if (isTinker(site)) { tinkerClean(); break; }
    clean(site);
    break;
  case 'collectstatic':
    for (const selected of selectedSites(site)) {
      if (isTinker(selected)) { tinkerCollectstatic(); }
      else {
        manage(selected, ['collectstatic', '--noinput', ...extra]);
        generateAssetManifest(selected);
      }
    }
    break;
  case 'build-collect':
    for (const selected of selectedSites(site)) {
      if (isTinker(selected)) { tinkerBuildCollect(); }
      else {
        webpack(selected, 'production');
        manage(selected, ['collectstatic', '--noinput', ...extra]);
        generateAssetManifest(selected);
      }
    }
    break;
  case 'load-dumps':
    for (const selected of selectedSites(site)) run(pythonBin(), ['tests/scripts/load_dumped_data.py', '--site', selected, ...extra], { cwd: workspaceRoot });
    break;
  case 'populate':
    populate(site, extra);
    break;
  case 'manage':
    manage(site, extra);
    break;
  default:
    console.error(`Unknown workspace asset command: ${command}`);
    usage();
    process.exit(2);
}
