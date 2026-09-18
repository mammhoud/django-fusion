#!/usr/bin/env node

/**
 * update-year.cjs — keep copyright year stamps current for the local edition.
 *
 * This is a no-op placeholder for the formint-standard edition. The repo's
 * build/pre-dev scripts call this script, but this edition does not maintain
 * a separate copyright-year stamp, so the script exits cleanly and prints
 * the "already up-to-date" message expected by callers.
 *
 * If this edition later adds year stamps, implement the update here and print:
 *   Copyright year already up-to-date (<YEAR>)
 */

const currentYear = new Date().getFullYear();

try {
  console.log(`Copyright year already up-to-date (${currentYear})`);
} catch (err) {
  console.error('update-year: unexpected error', err);
  process.exit(1);
}
