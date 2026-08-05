#!/usr/bin/env node
const { spawn, execSync } = require('node:child_process');
const path = require('node:path');

const SIDECAR_DIR = path.join(__dirname, '..', '..', 'sidecar');
const children = new Set();

function run(command, args, options = {}) {
  const child = spawn(command, args, {
    stdio: 'inherit',
    shell: process.platform === 'win32',
    ...options,
  });
  children.add(child);
  child.on('exit', () => children.delete(child));
  return child;
}

function shutdown(code = 0) {
  for (const child of children) {
    if (!child.killed) child.kill('SIGTERM');
  }
  process.exit(code);
}

process.on('SIGINT', () => shutdown(130));
process.on('SIGTERM', () => shutdown(143));

// ── Detect uv for sidecar Python dependency management ──
let hasUv = false;
try {
  execSync('uv --version', { stdio: 'ignore' });
  hasUv = true;
} catch {
  hasUv = false;
}

if (hasUv) {
  try {
    console.log('🔄 Syncing sidecar Python dependencies via uv...');
    execSync('uv sync', { cwd: SIDECAR_DIR, stdio: 'inherit' });
    console.log('✅ Sidecar Python deps ready');
  } catch (err) {
    console.error('❌ uv sync failed — falling back to bare python3');
    console.error(err.message);
    hasUv = false;
  }
}

const sidecarCmd = hasUv ? 'uv' : 'python3';
const sidecarArgs = hasUv
  ? ['run', 'python', 'server.py', '--port', '8766', '--host', '127.0.0.1', '--migrate']
  : ['server.py', '--port', '8766', '--host', '127.0.0.1', '--migrate'];

const sidecar = run(sidecarCmd, sidecarArgs, { cwd: SIDECAR_DIR });

sidecar.on('exit', (code) => {
  if (code !== 0 && children.size > 0) {
    console.error(`[dev] sidecar exited with code ${code}`);
    shutdown(code ?? 1);
  }
});

const vite = run('vite', []);
vite.on('exit', (code) => shutdown(code ?? 0));
