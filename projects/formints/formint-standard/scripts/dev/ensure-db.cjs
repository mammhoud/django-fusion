#!/usr/bin/env node

/**
 * ensure-db.cjs — ensure the local development database is available.
 *
 * This is a no-op placeholder for the formint-standard edition. When this
 * edition's dev/build scripts call ensure-db.cjs, it confirms that the
 * expected database file exists and prints the message callers expect:
 *
 *   Database found at <DB_PATH>
 *
 * If the database file is missing, this script is intentionally a no-op
 * placeholder. Real database initialization for this edition happens through
 * the Rust seed binary (`make seed` / `cargo run --bin seed`), not through
 * this Node helper.
 */

const fs = require('fs');
const path = require('path');

function main() {
  const projectRoot = process.env.PROJECT_ROOT || process.cwd();
  const dbPath = path.resolve(projectRoot, 'restaurant.db');

  if (!fs.existsSync(dbPath)) {
    console.log(`Database not found at ${dbPath}`);
    return;
  }

  console.log(`Database found at ${dbPath}`);
}

try {
  main();
} catch (err) {
  console.error('ensure-db: unexpected error', err);
  process.exit(1);
}
