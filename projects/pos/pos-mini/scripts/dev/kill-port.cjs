#!/usr/bin/env node
/**
 * kill-port.cjs
 *
 * Kills any process listening on one or more ports.
 * Default port: 1420 (Vite dev server).
 * Used before `vite` / `pnpm dev` to prevent "Port X is already in use" errors
 * from leftover Vite or Tauri dev server processes.
 *
 * Usage:
 *   node scripts/dev/kill-port.cjs              # kills port 1420
 *   node scripts/dev/kill-port.cjs 3000         # kills port 3000 only
 *   node scripts/dev/kill-port.cjs 3000 4000    # kills ports 3000 and 4000
 *   PORT=1421 node scripts/dev/kill-port.cjs    # kills port from env var only
 */

const { execSync } = require('child_process');
const platform = process.platform;

// ── Resolve ports ────────────────────────────────────────────────────
// If CLI args given, use those; else if PORT env var, use that; else default to 1420
const args = process.argv.slice(2);
const ports = args.length > 0
  ? args
  : process.env.PORT
    ? [process.env.PORT]
    : ['1420'];

// ── Kill each port ───────────────────────────────────────────────────

for (const port of ports) {
  try {
    let pidCommand;

    if (platform === 'darwin' || platform === 'linux') {
      pidCommand = `lsof -ti:${port} 2>/dev/null`;
    } else if (platform === 'win32') {
      pidCommand = `netstat -ano | findstr :${port} | findstr LISTENING`;
    } else {
      console.error(`kill-port: Unsupported platform "${platform}"`);
      continue;
    }

    const pidOutput = execSync(pidCommand, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'] }).trim();

    if (!pidOutput) {
      continue; // Port is free — nothing to do
    }

    // Extract PIDs — on Windows the output format is different
    let pids;
    if (platform === 'win32') {
      pids = pidOutput
        .split('\n')
        .map(line => line.trim().split(/\s+/).pop())
        .filter(Boolean)
        .filter((v, i, a) => a.indexOf(v) === i);
    } else {
      pids = pidOutput.split('\n').filter(Boolean);
    }

    if (pids.length === 0) {
      continue;
    }

    // Kill each PID
    for (const pid of pids) {
      try {
        execSync(`kill -9 ${pid} 2>/dev/null`, { stdio: 'ignore' });
        console.log(`kill-port: Killed process ${pid} on port ${port}`);
      } catch {
        // Process may already be dead
      }
    }
  } catch {
    // Silent fail — don't block the dev server
  }
}

process.exit(0);
