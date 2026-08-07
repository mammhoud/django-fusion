#!/usr/bin/env node
/**
 * kill-port.cjs — Terminate processes holding a given TCP port.
 *
 * Usage: node kill-port.cjs <port>
 *
 * Returns exit code 0 on success or if the port is already free.
 * Prints the PID(s) killed to stderr, if any.
 */

const { execSync } = require('child_process');
const port = parseInt(process.argv[2], 10);

if (!port || port < 1 || port > 65535) {
  console.error(`Usage: node kill-port.cjs <port>`);
  process.exit(1);
}

// Find processes holding the port using lsof (macOS/Linux)
// lsof exits with code 1 when no process is found — that's normal.
let stdout = '';
try {
  stdout = execSync(
    `lsof -ti tcp:${port} 2>/dev/null`,
    { stdio: ['pipe', 'pipe', 'pipe'], timeout: 5000 }
  ).toString().trim();
} catch (err) {
  // lsof exits with code 1 when nothing is listening — treat as empty
  const stderr = err.stderr ? err.stderr.toString() : '';
  if (stderr.includes('command not found')) {
    console.error('lsof not found — cannot kill port processes');
    process.exit(0);
  }
  stdout = '';
}

if (!stdout) {
  // Port is free — nothing to kill
  process.exit(0);
}

const pids = stdout.split('\n').filter(Boolean);

for (const pid of pids) {
  try {
    execSync(`kill -9 ${pid}`, { stdio: 'pipe', timeout: 3000 });
    console.error(`Killed PID ${pid} holding port ${port}`);
  } catch {
    // Process may have already exited — ignore
  }
}

process.exit(0);
