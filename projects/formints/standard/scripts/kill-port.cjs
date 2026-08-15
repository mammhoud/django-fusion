#!/usr/bin/env node

/**
 * kill-port.cjs — Kill any process listening on the given port.
 *
 * Usage: node kill-port.cjs <port>
 *
 * Works on macOS/Linux via lsof, and Windows via netstat+taskkill.
 * Exits with code 0 on success, 1 on failure.
 */

const { execSync } = require('child_process');
const port = parseInt(process.argv[2], 10);

if (!port || isNaN(port) || port < 1 || port > 65535) {
  console.error(`Usage: node kill-port.cjs <port>`);
  process.exit(1);
}

try {
  const platform = process.platform;

  if (platform === 'win32') {
    // Windows: netstat to find PID, then taskkill
    const netstatOut = execSync(`netstat -ano | findstr :${port}`, {
      encoding: 'utf-8',
      stdio: 'pipe',
    });
    const lines = netstatOut.trim().split('\n').filter(Boolean);
    for (const line of lines) {
      const parts = line.trim().split(/\s+/);
      const pid = parts[parts.length - 1];
      if (pid && pid !== '0') {
        try {
          execSync(`taskkill /PID ${pid} /F`, { stdio: 'pipe' });
          console.log(`Killed PID ${pid} on port ${port}`);
        } catch {
          // process may already be gone
        }
      }
    }
  } else {
    // macOS / Linux: lsof to find PID, then kill
    const lsofOut = execSync(
      `lsof -ti :${port}`,
      { encoding: 'utf-8', stdio: 'pipe' }
    );
    const pids = lsofOut.trim().split('\n').filter(Boolean);
    for (const pid of pids) {
      try {
        execSync(`kill -9 ${pid}`, { stdio: 'pipe' });
        console.log(`Killed PID ${pid} on port ${port}`);
      } catch {
        // process may already be gone
      }
    }
  }

  process.exit(0);  } catch (err) {
    // If lsof/netstat exits with non-zero, it usually means no process is
    // listening — that's not an error for our use case.
    const stderr = (err.stderr || '').toString().toLowerCase();
    const stdout = (err.stdout || '').toString().toLowerCase();
    const combined = `${stderr} ${stdout}`;
    if (
      combined.includes('no such process') ||
      combined.includes('no process') ||
      combined.includes('cannot find') ||
      combined.includes('no file use found') ||
      // lsof exits code 1 with empty output when no process is listening
      (err.status === 1 && !stdout.trim())
    ) {
      process.exit(0);
    }
    console.error(`Error killing port ${port}:`, err.message);
    process.exit(1);
  }
