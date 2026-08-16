/**
 * Tests for the kill-port script.
 *
 * These tests verify that:
 * 1. The script exits with code 0 when port is free
 * 2. The script kills a child process holding a port open
 * 3. The script does not throw when no process is listening
 */
import { describe, it, expect, afterEach } from 'vitest';
import { execSync, spawn } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import net from 'net';

// Compute script path using import.meta.url for ESM compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const scriptPath = resolve(__dirname, '../../../scripts/kill-port.cjs');
const TEST_PORT = 19999; // Use an unusual port to avoid conflicts

/** Helper: check if a port is in use by trying to listen on it */
function isPortInUse(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', () => resolve(true));
    server.once('listening', () => {
      server.close();
      resolve(false);
    });
    server.listen(port);
  });
}

describe('kill-port script', () => {
  afterEach(async () => {
    // Clean up any leftover processes on the test port
    try {
      execSync(`node "${scriptPath}" ${TEST_PORT}`, { stdio: 'pipe' });
    } catch {
      // ignore
    }
    // Give OS time to release the port
    await new Promise((r) => setTimeout(r, 300));
  });

  it('exits with code 0 when port is already free', () => {
    expect(() => {
      execSync(`node "${scriptPath}" 39999`, { stdio: 'pipe' });
    }).not.toThrow();
  });

  it('kills a child process holding the specified port', async () => {
    // Spawn a separate child process that holds the port open
    // This is necessary because kill-port uses lsof which returns PIDs.
    // An in-process net.Server would make lsof return the vitest PID,
    // causing the script to kill the test runner itself!
    const child = spawn(
      process.execPath,
      [
        '-e',
        `
          const net = require('net');
          const server = net.createServer();
          server.listen(${TEST_PORT}, () => {
            // Signal we're ready by writing to stdout
            process.stdout.write('listening');
          });
          // Keep the process alive
          setInterval(() => {}, 60000);
        `,
      ],
      { stdio: ['pipe', 'pipe', 'pipe'] }
    );

    // Wait for the child to start listening
    await new Promise<void>((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('Timeout waiting for child')), 5000);
      child.stdout?.once('data', () => {
        clearTimeout(timeout);
        resolve();
      });
      child.once('error', (err) => {
        clearTimeout(timeout);
        reject(err);
      });
    });

    // Verify the port is now occupied
    expect(await isPortInUse(TEST_PORT)).toBe(true);

    // Run the kill-port script
    execSync(`node "${scriptPath}" ${TEST_PORT}`, { stdio: 'pipe' });

    // Wait for the OS to release the port (poll up to 5 seconds)
    let portFree = false;
    for (let i = 0; i < 50; i++) {
      if (!(await isPortInUse(TEST_PORT))) {
        portFree = true;
        break;
      }
      await new Promise((r) => setTimeout(r, 100));
    }

    // Verify the port is now free
    expect(portFree).toBe(true);

    // Clean up the child process if it's still alive
    child.kill();
  });

  it('does not throw when port has no listener', () => {
    expect(() => {
      execSync(`node "${scriptPath}" 40000`, { stdio: 'pipe' });
    }).not.toThrow();
  });
});
