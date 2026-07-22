#!/usr/bin/env node
/**
 * Pre-dev / pre-build hook: ensures the database is seeded.
 *
 * Checks whether the database file (as configured by DATABASE_URL in .env,
 * defaulting to `restaurant.db` in the project root) already exists. If not,
 * it auto-runs `pnpm db:seed` to seed it.
 *
 * This prevents "relation not found" errors on first run after a clean clone.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PROJECT_ROOT = path.join(__dirname, '../..');

// ── 1. Resolve the database path ────────────────────────────────────────
let dbUrl = 'restaurant.db'; // default for local dev

try {
  const envPath = path.join(PROJECT_ROOT, '.env');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    const match = envContent.match(/^DATABASE_URL=(.+)$/m);
    if (match) {
      dbUrl = match[1].trim();
    }
  }
} catch {
  // silently ignore — use default
}

const dbPath = path.isAbsolute(dbUrl)
  ? dbUrl
  : path.join(PROJECT_ROOT, dbUrl);

// ── 2. Check if database already exists ─────────────────────────────────
if (fs.existsSync(dbPath)) {
  console.log(`✅ Database found at ${dbPath}`);
  process.exit(0);
}

// ── 3. Seed the database ────────────────────────────────────────────────
console.log(`🆕 Database not found at ${dbPath}`);
console.log('🌱 Running database seed...');

try {
  execSync('pnpm db:seed', { stdio: 'inherit', cwd: PROJECT_ROOT });
  console.log('✅ Database seeded successfully!');
} catch (error) {
  console.warn('⚠️  Database seed failed:', error.message);
  console.warn('⚠️  (missing tooling or compilation error). Skipping seed.');
  console.warn('⚠️  The app will create and migrate the database on first run.');
  process.exit(0);
}
