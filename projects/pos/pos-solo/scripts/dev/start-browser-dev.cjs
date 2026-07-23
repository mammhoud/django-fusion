#!/usr/bin/env node
const { spawn } = require('node:child_process');

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

const sidecar = run('python3', [
  'server.py',
  '--port', '8766',
  '--host', '127.0.0.1',
  '--migrate',
], { cwd: 'sidecar' });

sidecar.on('exit', (code) => {
  if (code !== 0 && children.size > 0) {
    console.error(`[dev] sidecar exited with code ${code}`);
    shutdown(code ?? 1);
  }
});

const vite = run('vite', []);
vite.on('exit', (code) => shutdown(code ?? 0));
