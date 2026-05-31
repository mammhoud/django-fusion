#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { existsSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const assetsRoot = path.resolve(__dirname, '..');
const workspaceRoot = path.resolve(assetsRoot, '..');
const nodeBin = process.platform === 'win32' ? 'npx.cmd' : 'npx';

const siteAliases = {
  ctc: 'ctc-research',
  'ctc-research': 'ctc-research',
  'ctc-research.com': 'ctc-research',
  structa: 'lms-demo',
  core: 'lms-demo',
  lms: 'lms-demo',
  'lms-demo': 'lms-demo',
  'structa.cloud': 'lms-demo',
  vresume: 'vresume',
  VResume: 'vresume',
  resume: 'vresume',
  'vresume.structa.cloud': 'vresume',
};

const sites = ['ctc-research', 'lms-demo', 'vresume'];
const siteDirs = {
  'ctc-research': 'ctc-research',
  'lms-demo': 'lms-demo',
  vresume: 'VResume',
};
const cleanDirs = {
  'ctc-research': ['ctc-research/assets/bundles/ctc-research'],
  'lms-demo': ['lms-demo/assets/bundles/lms-demo'],
  vresume: ['VResume/assets/bundles/vresume'],
  shared: ['assets/bundles/shared'],
};

function usage() {
  console.log(`Workspace asset CLI\n\nUsage:\n  npm --prefix assets run <script> -- [--site ctc|structa|vresume|all]\n  node assets/scripts/workspace.mjs <command> [--site SITE] [-- <extra args>]\n\nCommands:\n  build            Production webpack build for one site (default ctc-research)\n  build-dev        Development webpack build for one site\n  watch            Webpack watch for one site\n  dev              Webpack dev server for one site\n  analyze          Emit webpack stats for one site\n  clean            Remove generated bundles for one site or all sites\n  collectstatic    Run Django collectstatic for one site or all sites\n  build-collect    Build assets then collect static for one site or all sites\n  load-dumps       Load JSON dump fixtures for one site or all sites\n  populate         Run fixture loading and site-specific Python content/image population\n  manage           Run workspace manage.py for one site; pass Django args after --\n  sites            Print supported site names\n`);
}

function parse(argv) {
  const args = [...argv];
  const command = args.shift() || 'help';
  let site = process.env.PROJECT_PATH || process.env.DJANGO_SITE || process.env.WEBSITE || 'ctc-research';
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
  const env = { PROJECT_PATH: site, DJANGO_SITE: site, WEBSITE: site, NODE_ENV: mode };
  run(nodeBin, ['webpack', '--env', `site=${site}`, '--mode', mode, '--config', '../webpack/main.config.js', ...extra], { cwd: assetsRoot, env });
}

function manage(site, args) {
  run(pythonBin(), ['manage.py', `--site=${site}`, ...args], { cwd: workspaceRoot, env: { PROJECT_PATH: site, DJANGO_SITE: site, WEBSITE: site } });
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
    for (const selected of selectedSites(site)) webpack(selected, 'production', extra);
    break;
  case 'build-dev':
    for (const selected of selectedSites(site)) webpack(selected, 'development', extra);
    break;
  case 'watch':
    webpack(site, 'development', ['watch', ...extra]);
    break;
  case 'dev':
    webpack(site, 'development', ['serve', ...extra]);
    break;
  case 'analyze':
    webpack(site, 'production', ['--profile', '--json', ...extra]);
    break;
  case 'clean':
    clean(site);
    break;
  case 'collectstatic':
    for (const selected of selectedSites(site)) manage(selected, ['collectstatic', '--noinput', ...extra]);
    break;
  case 'build-collect':
    for (const selected of selectedSites(site)) {
      webpack(selected, 'production');
      manage(selected, ['collectstatic', '--noinput', ...extra]);
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
