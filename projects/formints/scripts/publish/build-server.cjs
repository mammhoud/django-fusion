#!/usr/bin/env node
/**
 * Build the POS Python/Sanic server binary via PyInstaller.
 *
 * Supports PROJECT_ROOT env var for edition-agnostic path resolution.
 *
 * Usage:
 *   node scripts/publish/build-server.cjs
 *   node scripts/publish/build-server.cjs --target x86_64-unknown-linux-gnu
 */

const { execSync, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const projectRoot = process.env.PROJECT_ROOT || path.resolve(__dirname, '../..');
const ROOT = projectRoot;
const SERVER_DIR = path.join(ROOT, 'server');
const BINARIES_DIR = path.join(ROOT, 'src-tauri', 'binaries');

function run(cmd, args, cwd, env) {
  const result = spawnSync(cmd, args, {
    cwd: cwd || ROOT,
    stdio: 'inherit',
    shell: process.platform === 'win32',
    env,
  });
  if (result.status !== 0) {
    throw new Error(`Command failed: ${cmd} ${args.join(' ')}`);
  }
}

function ensurePyinstaller() {
  try {
    execSync('pyinstaller --version', { stdio: 'ignore' });
    return 'pyinstaller';
  } catch {
    console.log('PyInstaller not found; installing into temporary venv...');
    const venvDir = path.join(SERVER_DIR, '.venv-build');
    if (!fs.existsSync(venvDir)) {
      run(process.platform === 'win32' ? 'python' : 'python3', ['-m', 'venv', venvDir], SERVER_DIR);
    }
    const pip = path.join(venvDir, process.platform === 'win32' ? 'Scripts\\pip.exe' : 'bin', 'pip');
    run(pip, ['install', '--upgrade', 'pip', 'pyinstaller'], SERVER_DIR);
    run(pip, ['install', '-r', 'requirements.txt'], SERVER_DIR);
    return path.join(venvDir, process.platform === 'win32' ? 'Scripts\\pyinstaller.exe' : 'bin', 'pyinstaller');
  }
}

function main() {
  const targetIndex = process.argv.indexOf('--target');
  const target = targetIndex !== -1 ? process.argv[targetIndex + 1] : undefined;

  fs.mkdirSync(BINARIES_DIR, { recursive: true });

  const pyinstaller = ensurePyinstaller();

  const env = { ...process.env, PYINSTALLER_BIN: pyinstaller };
  run(process.platform === 'win32' ? 'python' : 'python3', ['server/build.py'], ROOT, env);

  if (target) {
    const triple = target;
    const ext = process.platform === 'win32' ? '.exe' : '';
    const source = path.join(BINARIES_DIR, `pos-server-${triple}${ext}`);
    if (!fs.existsSync(source)) {
      console.error(`Expected binary not found at ${source}`);
      process.exit(1);
    }
    console.log(`Built server for ${triple}: ${source}`);
  }
}

main();
